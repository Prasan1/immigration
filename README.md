# Immigration Documents Portal

A production-ready web application for managing immigration forms, templates, and document processing with integrated payments.

## Features

### Core Features
- **11+ Immigration Forms** with comprehensive checklists
- **Fillable Templates** for common immigration documents
- **Multi-tier Subscriptions** (Solo, Professional, Team, Business)
- **Team Management** for collaborative access
- **White-label Branding** for enterprise users
- **Document Processing** - Passport applications with auto-filled forms

### Security & Production-Ready
- ✅ PostgreSQL database support
- ✅ HTTPS enforcement with security headers
- ✅ Rate limiting to prevent abuse
- ✅ Secure session management
- ✅ CORS protection
- ✅ Environment-based configuration
- ✅ Production-ready Gunicorn server

### Payment Processing
- Stripe integration for subscriptions
- Per-document processing fees
- Customer portal for subscription management
- Webhook support for payment events

## Tech Stack

- **Backend:** Flask 3.0, SQLAlchemy
- **Database:** PostgreSQL (production), SQLite (development)
- **Authentication:** Clerk
- **Payments:** Stripe
- **Server:** Gunicorn (production)
- **Security:** Flask-Talisman, Flask-Limiter

## Quick Start (Development)

### Prerequisites
- Python 3.10+
- Stripe account (optional for testing)
- Clerk account (optional for testing)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd immigrations

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys (or leave blank for basic testing)
nano .env

# Initialize database
python init_db.py

# Run development server
./start.sh
```

The app will be available at http://localhost:5000

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions to DigitalOcean App Platform.

### Quick Deploy Checklist

- [ ] Create Stripe products and copy Price IDs
- [ ] Set up Clerk application
- [ ] Push code to Git repository
- [ ] Create DigitalOcean App Platform app
- [ ] Add PostgreSQL database
- [ ] Configure environment variables
- [ ] Set up custom domain
- [ ] Configure Stripe webhooks
- [ ] Initialize production database
- [ ] Test all features

## Environment Variables

See `.env.example` for all required and optional environment variables.

### Critical Variables (Production)
```bash
FLASK_ENV=production
FLASK_SECRET_KEY=<strong-random-secret>
DATABASE_URL=<auto-set-by-digitalocean>
CLERK_SECRET_KEY=<your-clerk-key>
STRIPE_SECRET_KEY=<your-stripe-key>
```

## Subscription Tiers

| Tier | Price | Users | Features |
|------|-------|-------|----------|
| **Solo** | Free | 1 | 3 essential forms, 10+ templates |
| **Professional** | $39/mo | 1 | All forms, passport processing |
| **Team** | $149/mo | 5 | Professional + team workspace |
| **Business** | $299/mo | 15 | Team + white-label branding |

## Document Processing

### Passport Applications ($12/application)
- Auto-filled DS-11 form
- Comprehensive checklist
- Step-by-step submission guidance
- PDF generation (coming soon)

Available to Professional tier and above.

## Project Structure

```
immigrations/
├── app.py                      # Main Flask application
├── config.py                   # Configuration & settings
├── models.py                   # Database models (users, forms, etc.)
├── document_models.py          # Passport processing models
├── team_models.py              # Team management models
├── passport_routes.py          # Passport processing routes
├── team_routes.py              # Team management routes
├── form_guides.py              # Form filling guides
├── init_db.py                  # Database initialization
├── gunicorn.conf.py            # Production server config
├── requirements.txt            # Python dependencies
├── Procfile                    # Deploy configuration
├── runtime.txt                 # Python version
├── templates/                  # HTML templates
│   ├── passport_application.html
│   ├── dashboard.html
│   └── ...
└── static/                     # CSS, JS, images
```

## Development

### Adding New Forms

Edit `init_db.py` to add new immigration forms:

```python
{
    "title": "Form I-XXX - Description",
    "category": "Category Name",
    "description": "Detailed description",
    "access_level": "free",  # or "basic", "pro", "enterprise"
    "checklist": [
        "Item 1",
        "Item 2"
    ]
}
```

### Adding New Templates

Create new template file in `templates/` and add route in `app.py`.

### Testing Locally

```bash
# Run with debug mode
FLASK_ENV=development python app.py

# Test with Gunicorn (production-like)
gunicorn -c gunicorn.conf.py app:app
```

## Security

- All passwords and secrets stored in environment variables
- HTTPS enforced in production
- CSRF protection enabled
- Rate limiting on API endpoints
- SQL injection protection via SQLAlchemy ORM
- XSS protection with template escaping

## Monitoring

### Logs
Production logs available in DigitalOcean App Platform console.

### Database
Daily automated backups included with DigitalOcean PostgreSQL.

## Support & Issues

For deployment issues, see [DEPLOYMENT.md](DEPLOYMENT.md).

## License

Proprietary - All rights reserved

## Version

**v1.0.0** - Production-ready release with passport processing
