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

    # Stripe Price IDs (Old - deprecated)
    STRIPE_PRICE_ID_BASIC = os.getenv('STRIPE_PRICE_ID_BASIC')
    STRIPE_PRICE_ID_PRO = os.getenv('STRIPE_PRICE_ID_PRO')
    STRIPE_PRICE_ID_ENTERPRISE = os.getenv('STRIPE_PRICE_ID_ENTERPRISE')

    # New Stripe Price IDs (Marriage-based Immigration Model)
    STRIPE_PRICE_ID_COMPLETE = os.getenv('STRIPE_PRICE_ID_COMPLETE')  # $199 one-time payment
    STRIPE_PRICE_ID_AGENCY = os.getenv('STRIPE_PRICE_ID_AGENCY')  # $79/month subscription

    # Document Processing Pricing (one-time charges)
    STRIPE_PRICE_ID_PASSPORT = os.getenv('STRIPE_PRICE_ID_PASSPORT')  # $12 per passport application
    STRIPE_PRICE_ID_FILE_COMPRESSOR = os.getenv('STRIPE_PRICE_ID_FILE_COMPRESSOR')  # $5 per premium compression
    STRIPE_PRICE_ID_PDF_EVIDENCE_PACK = os.getenv('STRIPE_PRICE_ID_PDF_EVIDENCE_PACK')  # $29 PDF & Evidence Pack
    STRIPE_PRICE_ID_TRAVEL_HISTORY = os.getenv('STRIPE_PRICE_ID_TRAVEL_HISTORY')  # $19 I-94 Travel History

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

    # Subscription Tiers (Marriage-Based Immigration Focus)
    SUBSCRIPTION_TIERS = {
        'free': {
            'name': 'Free Starter',
            'price': 0,
            'pricing_type': 'free',
            'max_users': 1,
            'forms_access': 'basic',
            'forms_included': 'Basic I-130 checklist',
            'tagline': 'Get your feet wet with a basic I-130 checklist',
            'features': [
                'Basic I-130 checklist (view only)',
                'Sample cover letter template',
                'Required forms list',
                'Evidence categories overview'
            ],
            'document_processing': False
        },
        'complete': {
            'name': 'Complete Package',
            'price': 199,
            'pricing_type': 'one_time',
            'price_id': os.getenv('STRIPE_PRICE_ID_COMPLETE'),
            'max_users': 1,
            'forms_access': 'all',
            'forms_included': 'I-130, I-485, I-864, I-765, I-131',
            'tagline': 'Everything you need to file I-130, I-485, I-864, I-765, I-131 with confidence',
            'features': [
                'Complete I-130 & I-485 checklists',
                'Professional cover letter templates',
                'Evidence organizer (photos, texts, financial docs)',
                'PDF compressor (unlimited use—beat USCIS 10MB limits)',
                'I-94 travel history generator',
                'Document review checklist (before filing)',
                'Interview prep guide',
                'RFE response templates (if needed)',
                '30-day money-back guarantee'
            ],
            'document_processing': True
        },
        'agency': {
            'name': 'Immigration Preparer',
            'price': 79,
            'pricing_type': 'subscription',
            'price_id': os.getenv('STRIPE_PRICE_ID_AGENCY'),
            'max_users': 5,
            'forms_access': 'all',
            'forms_included': 'Unlimited client cases',
            'tagline': 'For immigration consultants, preparers, and agencies filing multiple cases',
            'features': [
                'Unlimited client cases',
                'All Complete Package features (for every client)',
                'White-label branding (your logo, colors, site name)',
                'Team collaboration (up to 5 team members)',
                'Client workspace management',
                'Remove "Powered by" footer',
                'Priority support'
            ],
            'document_processing': True
        },
        # OLD TIERS (Keep for backward compatibility with existing subscriptions)
        'basic': {
            'name': 'Professional (Legacy)',
            'price': 39,
            'pricing_type': 'subscription',
            'price_id': os.getenv('STRIPE_PRICE_ID_BASIC'),
            'max_users': 1,
            'forms_access': 'all',
            'forms_included': 'All 11+ forms',
            'tagline': 'For individuals & immigration consultants',
            'features': [
                'Avoid mistakes with expert-level checklists',
                'Access every immigration form without restrictions',
                'Unlimited PDF compression included (premium quality)',
                'Passport processing available ($12 per application)'
            ],
            'document_processing': True
        },
        'pro': {
            'name': 'Team (Legacy)',
            'price': 149,
            'pricing_type': 'subscription',
            'price_id': os.getenv('STRIPE_PRICE_ID_PRO'),
            'max_users': 5,
            'forms_access': 'all',
            'forms_included': 'All 11+ forms',
            'tagline': 'Perfect for small legal teams & NGOs',
            'features': [
                'Everything in Professional, plus:',
                'Work together safely with up to 5 team members',
                'Unlimited PDF compression for entire team'
            ],
            'document_processing': True
        },
        'enterprise': {
            'name': 'Business (Legacy)',
            'price': 299,
            'pricing_type': 'subscription',
            'price_id': os.getenv('STRIPE_PRICE_ID_ENTERPRISE'),
            'max_users': 15,
            'forms_access': 'all',
            'forms_included': 'All 11+ forms',
            'tagline': 'For law firms & universities',
            'features': [
                'Everything in Team, plus:',
                'Scale to 15 team members as you grow',
                'Your brand, your clients - white-label platform',
                'Unlimited PDF compression for all members'
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
            'required_tier': None,  # Available as standalone purchase
            'redirect_url': '/documents/passport'
        },
        'pdf_evidence_pack': {
            'name': 'USCIS PDF & Evidence Pack',
            'description': 'Compress and organize large evidence files to meet USCIS upload limits',
            'price': 29.00,
            'price_id': os.getenv('STRIPE_PRICE_ID_PDF_EVIDENCE_PACK'),
            'form_type': 'pdf_tools',
            'required_tier': None,  # Available as standalone purchase
            'redirect_url': '/file-compressor'
        },
        'travel_history': {
            'name': 'I-94 Travel History Worksheet',
            'description': 'Turn I-94 travel records into clean, USCIS-ready travel history worksheet',
            'price': 19.00,
            'price_id': os.getenv('STRIPE_PRICE_ID_TRAVEL_HISTORY'),
            'form_type': 'i94_history',
            'required_tier': None,  # Available as standalone purchase
            'redirect_url': '/documents/i94-history'
        }
        # NOTE: PDF Compression is now bundled into PAID subscriptions ONLY
        # No longer offered as separate $5 purchase or free tier access
    }

    # File Compressor Configuration (PAID PLANS ONLY)
    FILE_COMPRESSOR_LIMITS = {
        'free': {
            'monthly_limit': 0,  # NO ACCESS - Paid plans only
            'max_file_size_mb': 0,
            'compression_quality': None,
            'target_compression_ratio': 0
        },
        'complete': {
            'monthly_limit': None,  # Not monthly - see lifetime_limit
            'lifetime_limit': 100,  # 100 compressions total (one-time payment plan)
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        },
        'agency': {
            'monthly_limit': None,  # Unlimited - bundled into Agency subscription
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        },
        'pdf_evidence_pack': {
            'monthly_limit': None,  # Not monthly - see lifetime_limit
            'lifetime_limit': 100,  # 100 compressions total (standalone purchase)
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        },
        # Legacy tiers (backward compatibility)
        'basic': {
            'monthly_limit': None,  # Unlimited - bundled into Professional subscription
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        },
        'pro': {
            'monthly_limit': None,  # Unlimited - bundled into Team subscription
            'max_file_size_mb': 50,  # 50MB max file size
            'compression_quality': 'premium',  # 70-85% compression
            'target_compression_ratio': 0.25  # Target 25% of original size (75% reduction)
        },
        'enterprise': {
            'monthly_limit': None,  # Unlimited - bundled into Business subscription
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
        'Remove "Powered by ImmigrationTemplates.com"',
        'Branded checklist exports with your logo',
        'Custom footer text and legal disclaimers',
        'Deploy on your own domain (standard hosting)'
    ]
