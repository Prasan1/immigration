"""Routes for passport application processing"""
from flask import jsonify, request, render_template, session
from functools import wraps
from datetime import datetime
from document_models import PassportApplication, DocumentProcessingTransaction
from models import db, User
from config import Config
import stripe

def register_passport_routes(app, limiter):
    """Register all passport-related routes"""

    def get_current_user():
        """Get current user from session"""
        clerk_user_id = session.get('clerk_user_id')
        if clerk_user_id:
            return User.query.filter_by(clerk_user_id=clerk_user_id).first()
        return None

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'clerk_user_id' not in session:
                return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
            return f(*args, **kwargs)
        return decorated_function

    def subscription_required_for_doc_processing(f):
        """Check if user has subscription tier that allows document processing"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            # Check if user's tier allows document processing
            tier_info = Config.SUBSCRIPTION_TIERS.get(user.subscription_tier, {})
            if not tier_info.get('document_processing', False):
                return jsonify({
                    'error': 'Subscription upgrade required',
                    'message': 'Upgrade to Professional plan or higher to access document processing',
                    'required_tier': 'basic',
                    'current_tier': user.subscription_tier,
                    'redirect': '/pricing'
                }), 403

            return f(*args, **kwargs)
        return decorated_function

    # ============== PASSPORT ROUTES ==============

    @app.route('/documents/passport')
    @login_required
    @subscription_required_for_doc_processing
    def passport_page():
        """Passport application page"""
        user = get_current_user()
        return render_template('passport_application.html', user=user, config=Config)

    @app.route('/api/passport/applications', methods=['GET', 'POST'])
    @login_required
    @subscription_required_for_doc_processing
    @limiter.limit("10 per minute")
    def passport_applications():
        """List all passport applications or create a new one"""
        user = get_current_user()

        if request.method == 'GET':
            # Get all applications for this user
            applications = PassportApplication.query.filter_by(user_id=user.id).order_by(
                PassportApplication.created_at.desc()
            ).all()
            return jsonify([app.to_dict() for app in applications])

        elif request.method == 'POST':
            # Create new passport application
            data = request.json

            application = PassportApplication(
                user_id=user.id,
                full_name=data.get('full_name'),
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
                place_of_birth=data.get('place_of_birth'),
                ssn=data.get('ssn'),
                gender=data.get('gender'),
                height=data.get('height'),
                hair_color=data.get('hair_color'),
                eye_color=data.get('eye_color'),
                email=data.get('email', user.email),
                phone=data.get('phone'),
                mailing_address=data.get('mailing_address'),
                city=data.get('city'),
                state=data.get('state'),
                zip_code=data.get('zip_code'),
                emergency_contact_name=data.get('emergency_contact_name'),
                emergency_contact_phone=data.get('emergency_contact_phone'),
                emergency_contact_relationship=data.get('emergency_contact_relationship'),
                occupation=data.get('occupation'),
                employer=data.get('employer'),
                travel_date=datetime.strptime(data['travel_date'], '%Y-%m-%d').date() if data.get('travel_date') else None,
                destination=data.get('destination'),
                parent1_name=data.get('parent1_name'),
                parent1_birthplace=data.get('parent1_birthplace'),
                parent1_dob=datetime.strptime(data['parent1_dob'], '%Y-%m-%d').date() if data.get('parent1_dob') else None,
                parent2_name=data.get('parent2_name'),
                parent2_birthplace=data.get('parent2_birthplace'),
                parent2_dob=datetime.strptime(data['parent2_dob'], '%Y-%m-%d').date() if data.get('parent2_dob') else None,
                status='draft'
            )

            db.session.add(application)
            db.session.commit()

            return jsonify(application.to_dict()), 201

    @app.route('/api/passport/applications/<int:app_id>', methods=['GET', 'PUT', 'DELETE'])
    @login_required
    @subscription_required_for_doc_processing
    def passport_application_detail(app_id):
        """Get, update, or delete a specific passport application"""
        user = get_current_user()
        application = PassportApplication.query.filter_by(id=app_id, user_id=user.id).first_or_404()

        if request.method == 'GET':
            return jsonify(application.to_dict())

        elif request.method == 'PUT':
            # Update application
            data = request.json

            # Update fields
            if 'full_name' in data:
                application.full_name = data['full_name']
            if 'date_of_birth' in data:
                application.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            if 'place_of_birth' in data:
                application.place_of_birth = data['place_of_birth']
            if 'ssn' in data:
                application.ssn = data['ssn']
            if 'gender' in data:
                application.gender = data['gender']
            if 'height' in data:
                application.height = data['height']
            if 'hair_color' in data:
                application.hair_color = data['hair_color']
            if 'eye_color' in data:
                application.eye_color = data['eye_color']
            if 'email' in data:
                application.email = data['email']
            if 'phone' in data:
                application.phone = data['phone']
            if 'mailing_address' in data:
                application.mailing_address = data['mailing_address']
            if 'city' in data:
                application.city = data['city']
            if 'state' in data:
                application.state = data['state']
            if 'zip_code' in data:
                application.zip_code = data['zip_code']
            if 'emergency_contact_name' in data:
                application.emergency_contact_name = data['emergency_contact_name']
            if 'emergency_contact_phone' in data:
                application.emergency_contact_phone = data['emergency_contact_phone']
            if 'emergency_contact_relationship' in data:
                application.emergency_contact_relationship = data['emergency_contact_relationship']
            if 'occupation' in data:
                application.occupation = data['occupation']
            if 'employer' in data:
                application.employer = data['employer']
            if 'travel_date' in data and data['travel_date']:
                application.travel_date = datetime.strptime(data['travel_date'], '%Y-%m-%d').date()
            if 'destination' in data:
                application.destination = data['destination']

            db.session.commit()
            return jsonify(application.to_dict())

        elif request.method == 'DELETE':
            # Can only delete draft applications
            if application.payment_status == 'paid':
                return jsonify({'error': 'Cannot delete paid application'}), 400

            db.session.delete(application)
            db.session.commit()
            return jsonify({'success': True})

    @app.route('/api/passport/applications/<int:app_id>/checkout', methods=['POST'])
    @login_required
    @subscription_required_for_doc_processing
    @limiter.limit("5 per minute")
    def create_passport_checkout(app_id):
        """Create Stripe checkout for passport processing payment"""
        user = get_current_user()
        application = PassportApplication.query.filter_by(id=app_id, user_id=user.id).first_or_404()

        # Check if application is complete
        if not application.is_complete():
            return jsonify({'error': 'Please complete all required fields before checkout'}), 400

        # Check if already paid
        if application.payment_status == 'paid':
            return jsonify({'error': 'Application already paid'}), 400

        try:
            # Get passport processing price
            passport_config = Config.DOCUMENT_TYPES.get('passport')
            price_id = passport_config.get('price_id')

            if not price_id:
                return jsonify({'error': 'Passport processing price not configured'}), 500

            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(passport_config['price'] * 100),  # Convert to cents
                currency='usd',
                customer=user.stripe_customer_id if user.stripe_customer_id else None,
                metadata={
                    'user_id': user.id,
                    'application_id': application.id,
                    'document_type': 'passport',
                    'full_name': application.full_name
                },
                description=f'Passport Application Processing - {application.full_name}'
            )

            # Update application
            application.stripe_payment_intent_id = payment_intent.id
            application.status = 'pending_payment'
            db.session.commit()

            return jsonify({
                'client_secret': payment_intent.client_secret,
                'amount': passport_config['price']
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/passport/applications/<int:app_id>/confirm-payment', methods=['POST'])
    @login_required
    @subscription_required_for_doc_processing
    def confirm_passport_payment(app_id):
        """Confirm payment and mark application as paid"""
        user = get_current_user()
        application = PassportApplication.query.filter_by(id=app_id, user_id=user.id).first_or_404()

        data = request.json
        payment_intent_id = data.get('payment_intent_id')

        if not payment_intent_id:
            return jsonify({'error': 'Payment intent ID required'}), 400

        try:
            # Verify payment with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if payment_intent.status == 'succeeded':
                # Mark application as paid
                application.mark_paid(payment_intent_id)

                # Create transaction record
                transaction = DocumentProcessingTransaction(
                    user_id=user.id,
                    document_type='passport',
                    document_id=application.id,
                    amount=payment_intent.amount / 100,  # Convert from cents
                    stripe_payment_intent_id=payment_intent_id,
                    stripe_charge_id=payment_intent.charges.data[0].id if payment_intent.charges.data else None,
                    payment_status='succeeded',
                    description=f'Passport Application - {application.full_name}',
                    paid_at=datetime.utcnow()
                )
                db.session.add(transaction)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Payment confirmed',
                    'application': application.to_dict()
                })
            else:
                return jsonify({'error': 'Payment not completed'}), 400

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/passport/applications/<int:app_id>/generate-pdf', methods=['POST'])
    @login_required
    @subscription_required_for_doc_processing
    def generate_passport_pdf(app_id):
        """Generate PDF for paid passport application"""
        from pdf_generator import PassportPDFGenerator
        import os

        user = get_current_user()
        application = PassportApplication.query.filter_by(id=app_id, user_id=user.id).first_or_404()

        # Must be paid
        if application.payment_status != 'paid':
            return jsonify({'error': 'Application must be paid before generating PDF'}), 400

        try:
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(app.root_path, 'static', 'uploads', 'passports')
            os.makedirs(uploads_dir, exist_ok=True)

            # Generate PDF
            generator = PassportPDFGenerator()
            pdf_elements = generator.generate(application.to_dict())

            # Save PDF
            filename = f"passport_application_{application.id}_{user.id}.pdf"
            filepath = os.path.join(uploads_dir, filename)
            generator.save_to_file(pdf_elements, filepath)

            # Update application with PDF URL
            application.pdf_url = f"/static/uploads/passports/{filename}"
            application.status = 'completed'
            application.completed_at = datetime.utcnow()
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'PDF generated successfully',
                'pdf_url': application.pdf_url,
                'application': application.to_dict()
            })

        except Exception as e:
            return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
