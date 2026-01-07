from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    clerk_user_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255))

    # Subscription info
    subscription_tier = db.Column(db.String(50), default='free')  # free, complete, agency (+ legacy: basic, pro, enterprise)
    subscription_status = db.Column(db.String(50), default='inactive')  # active, inactive, cancelled, past_due
    stripe_customer_id = db.Column(db.String(255), unique=True)
    stripe_subscription_id = db.Column(db.String(255))
    subscription_ends_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'clerk_user_id': self.clerk_user_id,
            'email': self.email,
            'full_name': self.full_name,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'subscription_ends_at': self.subscription_ends_at.isoformat() if self.subscription_ends_at else None,
            'created_at': self.created_at.isoformat(),
        }

    def has_active_subscription(self):
        """Check if user has an active subscription"""
        return self.subscription_status == 'active' and self.subscription_tier != 'free'

    def can_access_form(self, form):
        """Check if user can access a specific form based on their subscription"""
        if form.access_level == 'free':
            return True

        tier_hierarchy = {
            'free': 0,
            'complete': 2,      # Complete Package: full access (one-time payment)
            'agency': 3,        # Immigration Preparer: full access + team features
            # Legacy tiers (backward compatibility)
            'basic': 1,
            'pro': 2,
            'enterprise': 3
        }

        user_tier = tier_hierarchy.get(self.subscription_tier, 0)
        required_tier = tier_hierarchy.get(form.access_level, 0)

        return user_tier >= required_tier and self.has_active_subscription()

    def can_access_template(self, template):
        """Check if user can access a specific template based on their subscription"""
        if template.access_level == 'free':
            return True

        tier_hierarchy = {
            'free': 0,
            'complete': 2,      # Complete Package: full access (one-time payment)
            'agency': 3,        # Immigration Preparer: full access + team features
            # Legacy tiers (backward compatibility)
            'basic': 1,
            'pro': 2,
            'enterprise': 3
        }

        user_tier = tier_hierarchy.get(self.subscription_tier, 0)
        required_tier = tier_hierarchy.get(template.access_level, 0)

        return user_tier >= required_tier and self.has_active_subscription()


class ImmigrationForm(db.Model):
    __tablename__ = 'immigration_forms'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    pdf_url = db.Column(db.String(500))
    info_url = db.Column(db.String(500))

    # Form details
    processing_time = db.Column(db.String(100))
    fee = db.Column(db.String(100))
    last_updated = db.Column(db.Date)

    # Access control (what tier is required to access this form)
    access_level = db.Column(db.String(50), default='free')  # free, basic (paid access)

    # Checklist stored as JSON
    checklist = db.Column(db.Text)  # JSON array of checklist items

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ImmigrationForm {self.title}>'

    def get_checklist(self):
        """Parse checklist JSON to Python list"""
        if self.checklist:
            return json.loads(self.checklist)
        return []

    def set_checklist(self, checklist_items):
        """Convert Python list to JSON for storage"""
        self.checklist = json.dumps(checklist_items)

    def to_dict(self, include_checklist=True):
        """Convert form to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'pdf_url': self.pdf_url,
            'info_url': self.info_url,
            'processing_time': self.processing_time,
            'fee': self.fee,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'access_level': self.access_level,
        }

        if include_checklist:
            data['checklist'] = self.get_checklist()

        return data


class Subscription(db.Model):
    """Track subscription history and changes"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tier = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    stripe_subscription_id = db.Column(db.String(255))

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('subscription_history', lazy=True))

    def __repr__(self):
        return f'<Subscription {self.tier} for User {self.user_id}>'


class OneTimePurchase(db.Model):
    """Track one-time purchases of standalone tools (passport, travel history, etc.)"""
    __tablename__ = 'one_time_purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tool_type = db.Column(db.String(100), nullable=False)  # passport, pdf_evidence_pack, travel_history
    price_paid = db.Column(db.Float, nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed, refunded

    # Timestamps
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('one_time_purchases', lazy=True))

    def __repr__(self):
        return f'<OneTimePurchase {self.tool_type} for User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tool_type': self.tool_type,
            'price_paid': self.price_paid,
            'status': self.status,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class EnterpriseSettings(db.Model):
    """Store custom branding settings for Enterprise users"""
    __tablename__ = 'enterprise_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Branding
    site_name = db.Column(db.String(255), default='Immigration Forms and Templates')
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(7), default='#667eea')  # Hex color
    secondary_color = db.Column(db.String(7), default='#764ba2')  # Hex color

    # Footer customization
    footer_text = db.Column(db.Text)
    show_powered_by = db.Column(db.Boolean, default=True)

    # Custom domain (optional)
    custom_domain = db.Column(db.String(255))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('enterprise_settings', uselist=False))

    def __repr__(self):
        return f'<EnterpriseSettings for User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'site_name': self.site_name,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'footer_text': self.footer_text,
            'show_powered_by': self.show_powered_by,
            'custom_domain': self.custom_domain,
            'updated_at': self.updated_at.isoformat()
        }


class FormTemplate(db.Model):
    """Blank fillable form templates for lawyers"""
    __tablename__ = 'form_templates'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    template_url = db.Column(db.String(500))  # URL to the template page

    # Access control (what tier is required to access this form)
    access_level = db.Column(db.String(50), default='free')  # free, basic (paid access)

    # Metadata
    use_case = db.Column(db.String(500))  # e.g., "Client intake", "Court filing"

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FormTemplate {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'template_url': self.template_url,
            'access_level': self.access_level,
            'use_case': self.use_case,
            'created_at': self.created_at.isoformat()
        }


class EmailLead(db.Model):
    """Email leads captured from landing pages"""
    __tablename__ = 'email_leads'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    source = db.Column(db.String(100))  # e.g., 'free-i130-checklist', 'homepage', 'blog-post'

    # UTM tracking
    utm_source = db.Column(db.String(100))  # e.g., 'facebook', 'reddit', 'google'
    utm_medium = db.Column(db.String(100))  # e.g., 'social', 'cpc', 'organic'
    utm_campaign = db.Column(db.String(100))  # e.g., 'free-checklist-campaign'

    # Status tracking
    status = db.Column(db.String(50), default='subscribed')  # subscribed, unsubscribed, converted_to_paid
    converted_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<EmailLead {self.email} from {self.source}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'source': self.source,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
