# Immigration Documents Portal - SaaS Platform

A comprehensive SaaS platform for accessing immigration forms, checklists, and related information with tiered subscription access.

## Features

- **Immigration Forms Database**: 11+ immigration forms with detailed information
- **User Authentication**: Clerk-based authentication system
- **Subscription Tiers**: Free, Basic ($19.99/mo), Pro ($49.99/mo), Enterprise ($199.99/mo)
- **Payment Processing**: Stripe integration for subscriptions
- **Access Control**: Premium content protection based on subscription tier
- **Admin Panel**: Form management for Enterprise users
- **Responsive Design**: Works on all devices

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Authentication**: Clerk
- **Payments**: Stripe
- **Frontend**: Bootstrap 5, jQuery
- **ORM**: SQLAlchemy

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd /path/to/immigrations

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Database
DATABASE_URL=sqlite:///immigration.db

# Clerk Authentication (https://clerk.com)
CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# Stripe (https://stripe.com)
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Stripe Price IDs (create products in Stripe Dashboard)
STRIPE_PRICE_ID_BASIC=price_xxx
STRIPE_PRICE_ID_PRO=price_xxx
STRIPE_PRICE_ID_ENTERPRISE=price_xxx

# Flask
FLASK_SECRET_KEY=your_random_secret_key_here
FLASK_ENV=development
```

### 4. Set Up Clerk Authentication

1. Go to [Clerk.com](https://clerk.com) and create an account
2. Create a new application
3. Copy your **Publishable Key** and **Secret Key**
4. Add them to your `.env` file
5. In Clerk Dashboard, configure:
   - Allowed redirect URLs: `http://localhost:5000/*`
   - Sign-in/Sign-up pages

### 5. Set Up Stripe

1. Go to [Stripe.com](https://stripe.com) and create an account
2. Get your API keys from the Dashboard (use Test mode for development)
3. Create subscription products and prices:
   - **Basic Plan**: $19.99/month
   - **Pro Plan**: $49.99/month
   - **Enterprise Plan**: $199.99/month
4. Copy the Price IDs and add them to `.env`
5. Set up webhook endpoint:
   - Endpoint URL: `https://your-domain.com/api/stripe/webhook`
   - Events to listen: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copy the webhook secret to `.env`

### 6. Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Migrate the 11 immigration forms with access levels

### 7. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Subscription Tiers

### Free Tier
- Access to 3 basic immigration forms
- Basic checklists
- Filing fee information

### Basic Tier ($19.99/month)
- Access to ALL immigration forms
- Detailed checklists
- Processing time estimates
- Email support

### Pro Tier ($49.99/month)
- Everything in Basic
- Priority updates on form changes
- Document templates
- Priority email support
- API access

### Enterprise Tier ($199.99/month)
- Everything in Pro
- White-label option
- Custom integrations
- Dedicated account manager
- Phone support
- Team collaboration features
- Admin panel access

## API Endpoints

### Public Endpoints
- `GET /` - Home page with forms list
- `GET /pricing` - Pricing page
- `GET /api/documents` - List all documents (access-controlled)
- `GET /api/documents/<id>` - Get single document
- `GET /api/categories` - Get all categories

### Protected Endpoints (Requires Login)
- `GET /dashboard` - User dashboard
- `GET /api/user/profile` - Get user profile
- `POST /api/create-checkout-session` - Create Stripe checkout
- `POST /api/create-portal-session` - Create Stripe customer portal
- `POST /api/auth/logout` - Logout user

### Admin Endpoints (Enterprise Only)
- `GET /api/admin/forms` - List all forms
- `POST /api/admin/forms` - Create new form
- `PUT /api/admin/forms/<id>` - Update form
- `DELETE /api/admin/forms/<id>` - Delete form

### Webhooks
- `POST /api/stripe/webhook` - Stripe webhook handler

## Database Schema

### Users Table
- `id` - Primary key
- `clerk_user_id` - Clerk user ID (unique)
- `email` - User email
- `full_name` - User's full name
- `subscription_tier` - free/basic/pro/enterprise
- `subscription_status` - active/inactive/cancelled/past_due
- `stripe_customer_id` - Stripe customer ID
- `stripe_subscription_id` - Stripe subscription ID
- `subscription_ends_at` - Subscription end date
- `created_at`, `updated_at` - Timestamps

### Immigration Forms Table
- `id` - Primary key
- `title` - Form title
- `category` - Form category
- `description` - Form description
- `pdf_url` - Link to PDF
- `info_url` - Link to more info
- `processing_time` - Estimated processing time
- `fee` - Filing fee
- `last_updated` - Last form update date
- `access_level` - free/basic/pro/enterprise
- `checklist` - JSON array of checklist items
- `created_at`, `updated_at` - Timestamps

### Subscriptions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `tier` - Subscription tier
- `status` - Subscription status
- `stripe_subscription_id` - Stripe subscription ID
- `started_at`, `ended_at` - Date range

## Development

### Adding New Forms

Use the admin API or add directly to database:

```python
from models import db, ImmigrationForm
from datetime import date

form = ImmigrationForm(
    title="Form I-XXX - Description",
    category="Category Name",
    description="Detailed description...",
    pdf_url="https://...",
    info_url="https://...",
    processing_time="X-Y months",
    fee="$XXX",
    last_updated=date.today(),
    access_level="basic"  # free, basic, pro, or enterprise
)
form.set_checklist([
    "Item 1",
    "Item 2",
    "Item 3"
])

db.session.add(form)
db.session.commit()
```

### Updating Subscription Tiers

Edit `config.py` to modify subscription tiers, pricing, and features.

## Deployment

### Production Checklist

1. **Environment**:
   - Set `FLASK_ENV=production`
   - Use PostgreSQL instead of SQLite
   - Generate strong `FLASK_SECRET_KEY`

2. **Clerk**:
   - Update redirect URLs to production domain
   - Use production keys

3. **Stripe**:
   - Switch to live mode
   - Update webhook URL
   - Create live products and prices

4. **Server**:
   - Use gunicorn: `gunicorn -w 4 -b 0.0.0.0:8000 app:app`
   - Set up nginx reverse proxy
   - Enable HTTPS with SSL certificate

5. **Database**:
   - Migrate to PostgreSQL
   - Set up regular backups
   - Use connection pooling

## Support

For issues or questions:
- Check the documentation
- Review API endpoints
- Contact support at your-email@example.com

## License

All rights reserved.
