import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database - PostgreSQL URL compatibility fix for SQLAlchemy
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///instance/immigration.db')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'

    # Clerk
    CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
    CLERK_PUBLISHABLE_KEY = os.getenv('CLERK_PUBLISHABLE_KEY')

    # Stripe
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

    # Stripe Price IDs
    STRIPE_PRICE_ID_BASIC = os.getenv('STRIPE_PRICE_ID_BASIC')
    STRIPE_PRICE_ID_PRO = os.getenv('STRIPE_PRICE_ID_PRO')
    STRIPE_PRICE_ID_ENTERPRISE = os.getenv('STRIPE_PRICE_ID_ENTERPRISE')

    # Document Processing Pricing (one-time charges)
    STRIPE_PRICE_ID_PASSPORT = os.getenv('STRIPE_PRICE_ID_PASSPORT')  # $12 per passport application
    STRIPE_PRICE_ID_FILE_COMPRESSOR = os.getenv('STRIPE_PRICE_ID_FILE_COMPRESSOR')  # $5 per premium compression

    # Security Settings
    SESSION_COOKIE_SECURE = ENV == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',') if ENV == 'production' else '*'

    # Rate Limiting
    RATELIMIT_ENABLED = ENV == 'production'
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_HEADERS_ENABLED = True

    # Subscription Tiers
    SUBSCRIPTION_TIERS = {
        'free': {
            'name': 'Solo',
            'price': 0,
            'max_users': 1,
            'forms_access': 3,
            'forms_included': 'I-130, I-485, N-400',
            'tagline': 'Perfect for first-time filers',
            'features': [
                'Try key forms for free',
                'Avoid common filing mistakes',
                'Know exactly what documents to include',
                'Get estimated processing times',
                '10+ professional fillable templates',
                'Compress PDFs for USCIS portals (5/month)',
                'No credit card required to start'
            ],
            'document_processing': False
        },
        'basic': {
            'name': 'Professional',
            'price': 39,
            'price_id': os.getenv('STRIPE_PRICE_ID_BASIC'),
            'max_users': 1,
            'forms_access': 'all',
            'forms_included': 'All 11+ forms',
            'tagline': 'For individuals & immigration consultants',
            'features': [
                'Avoid mistakes with expert-level checklists',
                'Access every immigration form without restrictions',
                'Get guidance, not just blank forms',
                'Never miss a form update or deadline',
                'File-ready templates save hours of work',
                'Professional support when you need help',
                'Unlimited PDF compression (premium quality)',
                'Auto-filled passport applications ($12 each)'
            ],
            'document_processing': True
        },
        'pro': {
            'name': 'Team',
            'price': 149,
            'price_id': os.getenv('STRIPE_PRICE_ID_PRO'),
            'max_users': 5,
            'forms_access': 'all',
            'forms_included': 'All 11+ forms',
            'tagline': 'Perfect for small legal teams & NGOs',
            'features': [
                'Everything in Professional, plus:',
                'Work together safely with up to 5 team members',
                'Centralized case management saves time',
                'Faster processing with team collaboration',
                'Invite colleagues and manage permissions',
                'Priority support when deadlines are tight',
                'Everyone has full access to all tools',
                'One bill for your entire team'
            ],
            'document_processing': True
        },
        'enterprise': {
            'name': 'Business',
            'price': 299,
            'price_id': os.getenv('STRIPE_PRICE_ID_ENTERPRISE'),
            'max_users': 15,
            'forms_access': 'all',
            'forms_included': 'All 11+ forms',
            'tagline': 'For law firms & universities',
            'features': [
                'Everything in Team, plus:',
                'Scale to 15 team members as you grow',
                'Your brand, your clients - white-label platform',
                'Custom logo and colors match your firm',
                'Professional appearance without "Powered by"',
                'Build trust with branded immigration tools',
                'Complete control over your client experience',
                'Enterprise-grade support and reliability'
            ],
            'document_processing': True
        }
    }

    # Document Processing Features
    DOCUMENT_TYPES = {
        'passport': {
            'name': 'US Passport Application (DS-11)',
            'description': 'Complete passport application with auto-filled form and checklist',
            'price': 12.00,
            'price_id': os.getenv('STRIPE_PRICE_ID_PASSPORT'),
            'form_type': 'DS-11',
            'required_tier': 'basic'
        },
        'file_compressor_premium': {
            'name': 'Premium File Compression',
            'description': 'Compress PDF files to 70-85% of original size with premium quality',
            'price': 5.00,
            'price_id': os.getenv('STRIPE_PRICE_ID_FILE_COMPRESSOR'),
            'required_tier': 'free'  # Available to all, but charges for premium
        }
    }

    # File Compressor Configuration
    FILE_COMPRESSOR_LIMITS = {
        'free': {
            'monthly_limit': 5,  # 5 compressions per month
            'max_file_size_mb': 2,  # 2MB max file size
            'compression_quality': 'basic',  # 50-60% compression
            'target_compression_ratio': 0.55  # Target 55% of original size
        },
        'basic': {
            'monthly_limit': None,  # Unlimited
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        },
        'premium_onetime': {
            'monthly_limit': None,  # Unlimited after paying $5
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        }
    }

    # Passport Application Data Model
    PASSPORT_REQUIRED_FIELDS = [
        'full_name', 'date_of_birth', 'place_of_birth', 'ssn',
        'mailing_address', 'phone', 'email', 'emergency_contact',
        'height', 'hair_color', 'eye_color', 'occupation', 'employer'
    ]

    # Admin Panel Features
    ADMIN_FEATURES = [
        'Add, edit, and delete immigration forms',
        'Update form information (fees, processing times, requirements)',
        'Manage form checklists',
        'View user access statistics',
        'Control form access levels',
        'Generate usage reports'
    ]

    # White-Label Features
    WHITE_LABEL_FEATURES = [
        'Custom branding with your logo and colors',
        'Custom site name and branding text',
        'Remove "Powered by ImmigrationForms.io"',
        'Branded checklist exports with your logo',
        'Custom footer text and legal disclaimers',
        'Deploy on your own domain (standard hosting)'
    ]
