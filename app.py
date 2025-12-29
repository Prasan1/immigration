from flask import Flask, render_template, jsonify, request, redirect, url_for, session, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from functools import wraps
import stripe
import json
import os
from datetime import datetime
from config import Config
from models import db, User, ImmigrationForm, Subscription, EnterpriseSettings, FormTemplate
from team_models import Team, TeamMembership
from form_guides import get_form_guide

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # CORS - properly configured based on environment
    if app.config['ENV'] == 'production':
        CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    else:
        CORS(app)

    # Security headers (HTTPS, CSP, etc.) - only in production
    if app.config['ENV'] == 'production':
        Talisman(app,
                 force_https=True,
                 strict_transport_security=True,
                 content_security_policy={
                     'default-src': "'self'",
                     'script-src': ["'self'", "'unsafe-inline'", "https://js.stripe.com", "https://challenges.cloudflare.com"],
                     'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
                     'font-src': ["'self'", "https://fonts.gstatic.com"],
                     'img-src': ["'self'", "data:", "https:"],
                     'connect-src': ["'self'", "https://api.stripe.com", "https://clerk.com"],
                     'frame-src': ["'self'", "https://js.stripe.com", "https://challenges.cloudflare.com"]
                 })

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config['RATELIMIT_STORAGE_URL'],
        default_limits=[app.config['RATELIMIT_DEFAULT']] if app.config['RATELIMIT_ENABLED'] else []
    )

    # Initialize Stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    return app, limiter

app, limiter = create_app()

# Register team routes
from team_routes import register_team_routes
register_team_routes(app)

# Register passport processing routes
from passport_routes import register_passport_routes
register_passport_routes(app, limiter)

# Register document processing routes (checklists, cover letters, I-94)
from document_routes import register_document_routes
register_document_routes(app, limiter)

# Register file compressor routes
from file_compressor_routes import register_file_compressor_routes
register_file_compressor_routes(app, limiter)

# Load branding settings for each request
@app.before_request
def load_branding():
    """Load branding settings into g object for templates"""
    # Default branding
    g.branding = {
        'site_name': 'Immigration Templates',
        'logo_url': None,
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'footer_text': None,
        'show_powered_by': True
    }

    # If database tables don't exist yet, skip branding customization
    try:
        # If user is logged in, load branding from their team owner (if in a team)
        user = get_current_user()
        if user:
            # Check if user is part of a team
            team_membership = TeamMembership.query.filter_by(
                user_id=user.id,
                status='active'
            ).first()

            if team_membership:
                # Load branding from team owner
                team = team_membership.team
                team_owner = team.owner

                # If team owner has enterprise settings, use those
                if team_owner.subscription_tier == 'enterprise':
                    settings = EnterpriseSettings.query.filter_by(user_id=team_owner.id).first()
                    if settings:
                        g.branding = {
                            'site_name': settings.site_name,
                            'logo_url': settings.logo_url,
                            'primary_color': settings.primary_color,
                            'secondary_color': settings.secondary_color,
                            'footer_text': settings.footer_text,
                            'show_powered_by': settings.show_powered_by
                        }
            elif user.subscription_tier == 'enterprise':
                # User is not in a team but has business tier (they are the owner)
                settings = EnterpriseSettings.query.filter_by(user_id=user.id).first()
                if settings:
                    g.branding = {
                        'site_name': settings.site_name,
                        'logo_url': settings.logo_url,
                        'primary_color': settings.primary_color,
                        'secondary_color': settings.secondary_color,
                        'footer_text': settings.footer_text,
                        'show_powered_by': settings.show_powered_by
                    }
    except Exception:
        # Database tables don't exist yet or other DB error - use default branding
        pass

# Helper function to get current user from Clerk session
def get_current_user():
    """Get current user from session"""
    clerk_user_id = session.get('clerk_user_id')
    if clerk_user_id:
        return User.query.filter_by(clerk_user_id=clerk_user_id).first()
    return None

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clerk_user_id' not in session:
            return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Subscription check decorator
def subscription_required(required_tier='basic'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
            user_tier_level = tier_hierarchy.get(user.subscription_tier, 0)
            required_tier_level = tier_hierarchy.get(required_tier, 1)

            if user_tier_level < required_tier_level or not user.has_active_subscription():
                return jsonify({
                    'error': 'Subscription required',
                    'required_tier': required_tier,
                    'current_tier': user.subscription_tier,
                    'redirect': '/pricing'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============== ROUTES ==============

@app.route('/')
def home():
    user = get_current_user()
    return render_template('home.html', user=user, config=Config)

@app.route('/forms')
def forms():
    user = get_current_user()
    return render_template('index.html', user=user, config=Config)

@app.route('/pricing')
def pricing():
    user = get_current_user()
    return render_template('pricing.html',
                         user=user,
                         tiers=Config.SUBSCRIPTION_TIERS,
                         stripe_pk=Config.STRIPE_PUBLISHABLE_KEY)

@app.route('/login')
def login():
    return render_template('auth.html', config=Config)

@app.route('/signup')
def signup():
    return render_template('auth.html', config=Config)

@app.route('/privacy')
def privacy_policy():
    user = get_current_user()
    return render_template('privacy.html', user=user, config=Config)

@app.route('/terms')
def terms_of_service():
    user = get_current_user()
    return render_template('terms.html', user=user, config=Config)

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    return render_template('dashboard.html', user=user, config=Config)


# ============== API ROUTES ==============

@app.route('/api/documents')
def get_documents():
    """Get all documents with access control"""
    user = get_current_user()

    forms = ImmigrationForm.query.all()
    documents = []

    for form in forms:
        form_dict = form.to_dict()

        # Access control logic:
        # 1. Free tier forms show PREVIEW to anonymous users, FULL to logged-in users
        # 2. Paid tier forms require login AND appropriate subscription
        if form.access_level == 'free':
            if user:
                # Logged in users get full access to free forms
                form_dict['has_access'] = True
                form_dict['requires_login'] = False
                form_dict['is_preview'] = False
            else:
                # Anonymous users get preview (first 3 items)
                checklist = form.get_checklist()
                if checklist and len(checklist) > 3:
                    form_dict['checklist'] = checklist[:3]  # Only first 3 items
                    form_dict['checklist_total'] = len(checklist)
                    form_dict['is_preview'] = True
                else:
                    form_dict['checklist_total'] = len(checklist) if checklist else 0
                    form_dict['is_preview'] = False
                form_dict['has_access'] = True  # Can still view modal
                form_dict['requires_login'] = True  # But needs login for full list
        elif user and user.can_access_form(form):
            # User is logged in and has appropriate subscription
            form_dict['has_access'] = True
            form_dict['requires_login'] = False
            form_dict['is_preview'] = False
        elif user:
            # User is logged in but needs to upgrade
            form_dict['has_access'] = False
            form_dict['requires_login'] = False
            form_dict['requires_upgrade'] = True
            form_dict['is_preview'] = False
            form_dict['checklist'] = []  # Hide checklist
        else:
            # User not logged in - needs to sign up
            form_dict['has_access'] = False
            form_dict['requires_login'] = True
            form_dict['is_preview'] = False
            form_dict['checklist'] = []  # Hide checklist

        form_dict['required_tier'] = form.access_level
        documents.append(form_dict)

    return jsonify(documents)

@app.route('/api/documents/<int:doc_id>')
def get_document(doc_id):
    """Get single document with access control"""
    user = get_current_user()
    form = ImmigrationForm.query.get_or_404(doc_id)

    form_dict = form.to_dict()

    # Access control - free forms show preview to anonymous, full to logged-in
    if form.access_level == 'free':
        if user:
            # Logged in users get full access to free forms
            form_dict['has_access'] = True
            form_dict['requires_login'] = False
            form_dict['is_preview'] = False
        else:
            # Anonymous users get preview (first 3 items)
            checklist = form.get_checklist()
            if checklist and len(checklist) > 3:
                form_dict['checklist'] = checklist[:3]
                form_dict['checklist_total'] = len(checklist)
                form_dict['is_preview'] = True
            else:
                form_dict['checklist_total'] = len(checklist) if checklist else 0
                form_dict['is_preview'] = False
            form_dict['has_access'] = True
            form_dict['requires_login'] = True
    elif user and user.can_access_form(form):
        # User has appropriate subscription
        form_dict['has_access'] = True
        form_dict['requires_login'] = False
        form_dict['is_preview'] = False
    else:
        # Access denied
        form_dict['has_access'] = False
        form_dict['is_preview'] = False
        form_dict['checklist'] = []

        if not user:
            # Not logged in
            return jsonify({
                'error': 'Login required',
                'message': f'Sign up for {form.access_level.title()} plan to access this form',
                'required_tier': form.access_level,
                'requires_login': True,
                'upgrade_url': '/pricing'
            }), 401
        else:
            # Logged in but need to upgrade
            return jsonify({
                'error': 'Subscription required',
                'message': f'Upgrade to {form.access_level.title()} plan to access this form',
                'required_tier': form.access_level,
                'requires_upgrade': True,
                'upgrade_url': '/pricing'
            }), 403

    return jsonify(form_dict)

@app.route('/api/categories')
def get_categories():
    """Get all unique categories"""
    forms = ImmigrationForm.query.with_entities(ImmigrationForm.category).distinct().all()
    categories = [f[0] for f in forms]
    return jsonify(categories)

@app.route('/api/form-guide/<int:form_id>')
def get_form_guide_api(form_id):
    """Get step-by-step filling guide for a form"""
    form = ImmigrationForm.query.get_or_404(form_id)
    guide = get_form_guide(form.title)

    if guide:
        return jsonify({
            'available': True,
            'form_title': form.title,
            'guide': guide
        })
    else:
        return jsonify({
            'available': False,
            'message': 'Filling guide not available for this form yet. Check back soon!'
        })

@app.route('/api/user/profile')
@login_required
def get_user_profile():
    """Get current user profile"""
    user = get_current_user()
    return jsonify(user.to_dict())


# ============== CLERK AUTHENTICATION ==============

@app.route('/api/auth/session', methods=['POST'])
def create_session():
    """Create user session after Clerk authentication"""
    data = request.json
    clerk_user_id = data.get('clerk_user_id')
    email = data.get('email')
    full_name = data.get('full_name')

    if not clerk_user_id or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    # Find or create user
    user = User.query.filter_by(clerk_user_id=clerk_user_id).first()

    if not user:
        user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            full_name=full_name
        )
        db.session.add(user)
        db.session.commit()

    # Set session
    session.permanent = True  # Make session persist for 24 hours
    session['clerk_user_id'] = clerk_user_id

    return jsonify({'success': True, 'user': user.to_dict()})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user - clear Flask session and return Clerk signout URL"""
    session.pop('clerk_user_id', None)
    session.clear()  # Clear all session data
    return jsonify({
        'success': True,
        'message': 'Logged out successfully',
        'clerk_signout': True  # Signal frontend to sign out from Clerk
    })

# Development-only login endpoint
@app.route('/dev-login')
def dev_login():
    """Development-only endpoint to quickly log in as test user"""
    if Config.ENV != 'development':
        return jsonify({'error': 'Only available in development mode'}), 403

    # Find or create test user
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        test_user = User(
            clerk_user_id='dev_test_user',
            email='test@example.com',
            full_name='Test User (Dev)',
            subscription_tier='basic',  # Professional tier for testing
            subscription_status='active'
        )
        db.session.add(test_user)
        db.session.commit()

    # Set session
    session.permanent = True
    session['clerk_user_id'] = test_user.clerk_user_id

    # Redirect to file compressor or dashboard
    from flask import redirect
    return redirect('/file-compressor')


# ============== STRIPE INTEGRATION ==============

@app.route('/api/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    data = request.json
    tier = data.get('tier')

    if tier not in Config.SUBSCRIPTION_TIERS:
        return jsonify({'error': 'Invalid subscription tier'}), 400

    tier_info = Config.SUBSCRIPTION_TIERS[tier]
    price_id = tier_info.get('price_id')

    if not price_id:
        return jsonify({'error': 'Price ID not configured'}), 500

    user = get_current_user()

    try:
        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': user.id, 'clerk_user_id': user.clerk_user_id}
            )
            user.stripe_customer_id = customer.id
            db.session.commit()

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'dashboard?success=true',
            cancel_url=request.host_url + 'pricing?canceled=true',
            metadata={
                'user_id': user.id,
                'tier': tier
            }
        )

        return jsonify({'checkout_url': checkout_session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync-subscription', methods=['POST'])
@login_required
def sync_subscription():
    """Manually sync subscription from Stripe (for testing without webhooks)"""
    user = get_current_user()

    if not user.stripe_customer_id:
        return jsonify({'error': 'No Stripe customer found'}), 404

    try:
        # Get active subscriptions from Stripe
        subscriptions = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            status='active',
            limit=1
        )

        if not subscriptions.data:
            return jsonify({'message': 'No active subscription found', 'tier': 'free'}), 200

        subscription = subscriptions.data[0]

        # Map price ID to tier
        tier_map = {
            Config.STRIPE_PRICE_ID_BASIC: 'basic',
            Config.STRIPE_PRICE_ID_PRO: 'pro',
            Config.STRIPE_PRICE_ID_ENTERPRISE: 'enterprise'
        }

        price_id = subscription['items']['data'][0]['price']['id']
        tier = tier_map.get(price_id, 'free')

        # Update user subscription
        user.subscription_tier = tier
        user.subscription_status = subscription['status']
        user.stripe_subscription_id = subscription.id

        # Create subscription record if doesn't exist
        existing_sub = Subscription.query.filter_by(
            stripe_subscription_id=subscription.id
        ).first()

        if not existing_sub:
            sub = Subscription(
                user_id=user.id,
                tier=tier,
                status=subscription['status'],
                stripe_subscription_id=subscription.id
            )
            db.session.add(sub)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Subscription synced successfully',
            'tier': tier,
            'status': subscription['status']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-portal-session', methods=['POST'])
@login_required
def create_portal_session():
    """Create Stripe customer portal session"""
    user = get_current_user()

    if not user.stripe_customer_id:
        return jsonify({'error': 'No subscription found'}), 404

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=request.host_url + 'dashboard',
        )

        return jsonify({'portal_url': portal_session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    # Verify webhook signature if secret is configured
    if Config.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError:
            return jsonify({'error': 'Invalid signature'}), 400
    else:
        # No webhook secret configured - parse payload directly (dev only!)
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON'}), 400

    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return jsonify({'success': True})

def handle_checkout_completed(session):
    """Handle successful checkout"""
    user_id = session['metadata'].get('user_id')
    tier = session['metadata'].get('tier')
    subscription_id = session.get('subscription')

    user = User.query.get(user_id)
    if user:
        user.subscription_tier = tier
        user.subscription_status = 'active'
        user.stripe_subscription_id = subscription_id

        # Create subscription record
        sub = Subscription(
            user_id=user.id,
            tier=tier,
            status='active',
            stripe_subscription_id=subscription_id
        )
        db.session.add(sub)
        db.session.commit()

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    user = User.query.filter_by(stripe_subscription_id=subscription['id']).first()
    if user:
        user.subscription_status = subscription['status']
        db.session.commit()

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    user = User.query.filter_by(stripe_subscription_id=subscription['id']).first()
    if user:
        user.subscription_status = 'cancelled'
        user.subscription_tier = 'free'

        # Update subscription record
        sub = Subscription.query.filter_by(
            stripe_subscription_id=subscription['id']
        ).order_by(Subscription.started_at.desc()).first()

        if sub:
            sub.status = 'cancelled'
            sub.ended_at = datetime.utcnow()

        db.session.commit()


# ============== ADMIN ROUTES ==============

@app.route('/api/admin/forms', methods=['GET', 'POST'])
@login_required
def admin_forms():
    """Admin: List or create forms"""
    user = get_current_user()

    # Simple admin check (you can enhance this)
    if user.subscription_tier != 'enterprise':
        return jsonify({'error': 'Admin access required'}), 403

    if request.method == 'POST':
        data = request.json
        form = ImmigrationForm(
            title=data['title'],
            category=data['category'],
            description=data['description'],
            pdf_url=data.get('pdf_url'),
            info_url=data.get('info_url'),
            processing_time=data.get('processing_time'),
            fee=data.get('fee'),
            access_level=data.get('access_level', 'free')
        )

        if 'checklist' in data:
            form.set_checklist(data['checklist'])

        if 'last_updated' in data:
            form.last_updated = datetime.strptime(data['last_updated'], '%Y-%m-%d').date()

        db.session.add(form)
        db.session.commit()

        return jsonify(form.to_dict()), 201

    else:
        forms = ImmigrationForm.query.all()
        return jsonify([f.to_dict() for f in forms])

@app.route('/api/admin/forms/<int:form_id>', methods=['PUT', 'DELETE'])
@login_required
def admin_form_detail(form_id):
    """Admin: Update or delete a form"""
    user = get_current_user()

    if user.subscription_tier != 'enterprise':
        return jsonify({'error': 'Admin access required'}), 403

    form = ImmigrationForm.query.get_or_404(form_id)

    if request.method == 'PUT':
        data = request.json

        form.title = data.get('title', form.title)
        form.category = data.get('category', form.category)
        form.description = data.get('description', form.description)
        form.pdf_url = data.get('pdf_url', form.pdf_url)
        form.info_url = data.get('info_url', form.info_url)
        form.processing_time = data.get('processing_time', form.processing_time)
        form.fee = data.get('fee', form.fee)
        form.access_level = data.get('access_level', form.access_level)

        if 'checklist' in data:
            form.set_checklist(data['checklist'])

        if 'last_updated' in data:
            form.last_updated = datetime.strptime(data['last_updated'], '%Y-%m-%d').date()

        db.session.commit()
        return jsonify(form.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(form)
        db.session.commit()
        return jsonify({'success': True})


# ============== FORM TEMPLATES ==============

@app.route('/templates')
def form_templates():
    """Browse fillable form templates"""
    user = get_current_user()
    return render_template('templates_browse.html', user=user)

@app.route('/api/templates')
def get_templates():
    """Get all form templates with access control"""
    user = get_current_user()
    templates = FormTemplate.query.all()

    result = []
    for template in templates:
        template_dict = template.to_dict()

        # Access control
        if template.access_level == 'free':
            template_dict['has_access'] = True
        elif user and user.can_access_template(template):
            template_dict['has_access'] = True
        else:
            template_dict['has_access'] = False
            if not user:
                template_dict['requires_login'] = True
            else:
                template_dict['requires_upgrade'] = True

        result.append(template_dict)

    return jsonify(result)

@app.route('/templates/client-intake-family')
def template_client_intake():
    """Client Intake Questionnaire - FREE template, no login required"""
    user = get_current_user()
    return render_template('form_client_intake_family.html', user=user)

@app.route('/templates/personal-declaration')
def template_personal_declaration():
    """Personal Declaration Template - FREE template, no login required"""
    user = get_current_user()
    return render_template('form_personal_declaration.html', user=user)

@app.route('/templates/uscis-cover-letter')
@login_required
def template_cover_letter():
    """USCIS Cover Letter Template"""
    user = get_current_user()

    # Basic tier required
    if user.subscription_tier == 'free':
        return redirect('/pricing')

    return render_template('form_uscis_cover_letter.html', user=user)

@app.route('/templates/evidence-index')
@login_required
def template_evidence_index():
    """Table of Contents / Evidence Index Template"""
    user = get_current_user()

    # Basic tier required
    if user.subscription_tier == 'free':
        return redirect('/pricing')

    return render_template('form_evidence_index.html', user=user)

@app.route('/templates/retainer-agreement')
@login_required
def template_retainer():
    """Attorney-Client Retainer Agreement Template"""
    user = get_current_user()

    # Pro tier required
    tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
    if tier_hierarchy.get(user.subscription_tier, 0) < 2:
        return redirect('/pricing')

    return render_template('form_retainer_agreement.html', user=user)

@app.route('/templates/employer-letter')
@login_required
def template_employer_letter():
    """Employer Support Letter Template"""
    user = get_current_user()

    # Pro tier required
    tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
    if tier_hierarchy.get(user.subscription_tier, 0) < 2:
        return redirect('/pricing')

    return render_template('form_employer_letter.html', user=user)

@app.route('/templates/marriage-bona-fide')
@login_required
def template_marriage_bona_fide():
    """Marriage Bona Fide Declaration Template"""
    user = get_current_user()

    # Basic tier required
    if user.subscription_tier == 'free':
        return redirect('/pricing')

    return render_template('form_marriage_bona_fide.html', user=user)

@app.route('/templates/hardship-declaration')
@login_required
def template_hardship_declaration():
    """Extreme Hardship Declaration (I-601/I-601A) Template"""
    user = get_current_user()

    # Pro tier required
    tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
    if tier_hierarchy.get(user.subscription_tier, 0) < 2:
        return redirect('/pricing')

    return render_template('form_hardship_declaration.html', user=user)

@app.route('/templates/rfe-response')
@login_required
def template_rfe_response():
    """RFE Response Cover Letter Template"""
    user = get_current_user()

    # Pro tier required
    tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
    if tier_hierarchy.get(user.subscription_tier, 0) < 2:
        return redirect('/pricing')

    return render_template('form_rfe_response.html', user=user)

@app.route('/templates/job-offer-letter')
@login_required
def template_job_offer():
    """Job Offer Letter Template"""
    user = get_current_user()

    # Basic tier required
    if user.subscription_tier == 'free':
        return redirect('/pricing')

    return render_template('form_job_offer_letter.html', user=user)

@app.route('/templates/spouse-affidavit')
@login_required
def template_spouse_affidavit():
    """Spouse Affidavit Template"""
    user = get_current_user()

    # Basic tier required
    if user.subscription_tier == 'free':
        return redirect('/pricing')

    return render_template('form_spouse_affidavit.html', user=user)

@app.route('/templates/hardship-worksheet')
@login_required
def template_hardship_worksheet():
    """Extreme Hardship Worksheet Template"""
    user = get_current_user()

    # Pro tier required (attorney tool)
    tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
    if tier_hierarchy.get(user.subscription_tier, 0) < 2:
        return redirect('/pricing')

    return render_template('form_extreme_hardship_worksheet.html', user=user)

@app.route('/templates/immigration-history')
@login_required
def template_immigration_history():
    """Immigration History Worksheet Template"""
    user = get_current_user()

    # Basic tier required
    if user.subscription_tier == 'free':
        return redirect('/pricing')

    return render_template('form_immigration_history.html', user=user)


# ============== ENTERPRISE SETTINGS ==============

@app.route('/enterprise/settings')
@login_required
def enterprise_settings_page():
    """Enterprise settings page"""
    user = get_current_user()

    if user.subscription_tier != 'enterprise':
        return redirect('/pricing')

    return render_template('enterprise_settings.html', user=user)

@app.route('/api/enterprise/settings', methods=['GET', 'PUT'])
@login_required
def enterprise_settings():
    """Get or update enterprise branding settings"""
    user = get_current_user()

    if user.subscription_tier != 'enterprise':
        return jsonify({'error': 'Enterprise subscription required'}), 403

    if request.method == 'GET':
        # Get or create settings
        settings = EnterpriseSettings.query.filter_by(user_id=user.id).first()

        if not settings:
            # Create default settings
            settings = EnterpriseSettings(user_id=user.id)
            db.session.add(settings)
            db.session.commit()

        return jsonify(settings.to_dict())

    elif request.method == 'PUT':
        data = request.json
        settings = EnterpriseSettings.query.filter_by(user_id=user.id).first()

        if not settings:
            settings = EnterpriseSettings(user_id=user.id)
            db.session.add(settings)

        # Update fields
        if 'site_name' in data:
            settings.site_name = data['site_name']
        if 'logo_url' in data:
            settings.logo_url = data['logo_url']
        if 'primary_color' in data:
            settings.primary_color = data['primary_color']
        if 'secondary_color' in data:
            settings.secondary_color = data['secondary_color']
        if 'footer_text' in data:
            settings.footer_text = data['footer_text']
        if 'show_powered_by' in data:
            settings.show_powered_by = data['show_powered_by']
        if 'custom_domain' in data:
            settings.custom_domain = data['custom_domain']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Branding settings updated successfully',
            'settings': settings.to_dict()
        })


@app.route('/initialize-database')
def initialize_database():
    """Initialize database tables and load forms data"""
    try:
        # Create all tables
        db.create_all()

        # Check if forms already exist
        existing_forms = ImmigrationForm.query.count()
        if existing_forms > 0:
            return jsonify({
                'success': True,
                'message': f'Database already initialized with {existing_forms} forms',
                'forms_count': existing_forms
            })

        # Load forms data from init_db.py
        from datetime import datetime
        forms_data = [
            {
                "title": "Form I-130 - Immediate Relative/Family Preference Petition",
                "category": "Family-Based Immigration",
                "description": "Petition filed by U.S. citizens and lawful permanent residents to establish qualifying family relationship for relatives seeking to immigrate to or adjust status in the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-130.pdf",
                "info_url": "https://www.uscis.gov/i-130",
                "last_updated": "2024-01-15",
                "processing_time": "12-33 months",
                "fee": "$535",
                "access_level": "free",
                "checklist": [
                    "Completed Form I-130",
                    "Filing fee of $535",
                    "Proof of U.S. citizenship or permanent residence",
                    "Proof of relationship to beneficiary",
                    "Passport-style photos of petitioner and beneficiary",
                    "Birth certificates",
                    "Marriage certificate (if applicable)",
                    "Divorce decree (if previously married)"
                ]
            },
            {
                "title": "Form I-485 - Application to Adjust Status to Permanent Resident",
                "category": "Adjustment of Status",
                "description": "Used to apply for adjustment of status to become a lawful permanent resident of the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-485.pdf",
                "info_url": "https://www.uscis.gov/i-485",
                "last_updated": "2024-02-01",
                "processing_time": "13-25 months",
                "fee": "$1,225",
                "access_level": "free",
                "checklist": [
                    "Completed Form I-485",
                    "Filing fee of $1,225",
                    "Form I-693 Medical Examination",
                    "Two passport-style photographs",
                    "Copy of birth certificate",
                    "Copy of passport and I-94",
                    "Form I-864 Affidavit of Support",
                    "Tax returns for past 3 years",
                    "Employment authorization (if applicable)"
                ]
            },
            {
                "title": "Form N-400 - Naturalization Application for U.S. Citizenship",
                "category": "Naturalization",
                "description": "Used to apply for U.S. citizenship through naturalization.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/n-400.pdf",
                "info_url": "https://www.uscis.gov/n-400",
                "last_updated": "2024-01-20",
                "processing_time": "14-22 months",
                "fee": "$725",
                "access_level": "free",
                "checklist": [
                    "Completed Form N-400",
                    "Filing fee of $725",
                    "Copy of Permanent Resident Card",
                    "Copy of marriage certificate (if applicable)",
                    "Divorce decree (if previously married)",
                    "Tax returns for past 5 years",
                    "Travel history records",
                    "Two passport-style photographs"
                ]
            }
        ]

        # Add forms to database
        for form_data in forms_data:
            form = ImmigrationForm(
                title=form_data['title'],
                category=form_data['category'],
                description=form_data['description'],
                pdf_url=form_data['pdf_url'],
                info_url=form_data['info_url'],
                processing_time=form_data['processing_time'],
                fee=form_data['fee'],
                last_updated=datetime.strptime(form_data['last_updated'], '%Y-%m-%d').date(),
                access_level=form_data.get('access_level', 'free')
            )
            form.set_checklist(form_data['checklist'])
            db.session.add(form)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Database initialized successfully!',
            'forms_loaded': len(forms_data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to initialize database'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

