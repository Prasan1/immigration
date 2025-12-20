# Quick Start Guide

## What's Been Built

Your immigration forms app is now a full SaaS platform with:

✅ **Database-driven architecture** (SQLAlchemy + SQLite)
✅ **User authentication** (Clerk integration ready)
✅ **Subscription system** with 4 tiers (Free, Basic, Pro, Enterprise)
✅ **Stripe payment integration** for recurring subscriptions
✅ **Access control** - premium forms locked behind subscriptions
✅ **User dashboard** - manage subscription and view available forms
✅ **Pricing page** - beautiful tier comparison
✅ **Admin panel** - Enterprise users can manage forms
✅ **Responsive UI** - works on all devices

## File Structure

```
immigrations/
├── app.py                 # Main Flask application
├── models.py              # Database models (User, Form, Subscription)
├── config.py              # Configuration and subscription tiers
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── start.sh              # Quick start script
├── README.md             # Full documentation
└── templates/
    ├── index.html        # Main forms listing page
    ├── pricing.html      # Pricing/subscription page
    └── dashboard.html    # User dashboard
```

## Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /home/ppaudyal/Documents/immigrations
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment

Copy and edit the environment file:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Minimum required for testing:**
- `FLASK_SECRET_KEY` - Any random string
- For full functionality, you'll need Clerk and Stripe keys (see README.md)

### Step 3: Initialize Database & Run

```bash
python init_db.py  # Creates database with 11 forms
python app.py       # Start the server
```

Or use the quick start script:

```bash
./start.sh
```

Visit: **http://localhost:5000**

## Subscription Tiers

### Free (Default)
- Access to 3 forms: I-130, I-485, N-400
- Basic checklists

### Basic - $19.99/month
- All 11 immigration forms
- Full checklists
- Forms: I-765, I-129, I-539 + all free forms

### Pro - $49.99/month
- Everything in Basic
- Priority support
- Forms: I-131, I-90, DS-160 + all Basic forms

### Enterprise - $199.99/month
- Everything in Pro
- Admin panel access
- Forms: DS-260, I-407 + all Pro forms

## Next Steps

### For Development/Testing:

1. **Test without authentication**: The app works without Clerk setup - forms will show but subscription features won't work

2. **Add Clerk Authentication**:
   - Sign up at https://clerk.com
   - Get your API keys
   - Add to `.env` file
   - Users can then sign up/login

3. **Add Stripe Payments**:
   - Sign up at https://stripe.com
   - Create subscription products
   - Add price IDs to `.env`
   - Test with Stripe test cards

### For Production:

1. Switch to PostgreSQL database
2. Use production Clerk keys
3. Use live Stripe keys
4. Deploy to cloud (Heroku, Railway, AWS, etc.)
5. Set up custom domain
6. Configure SSL certificate

## Key Features Implemented

### Access Control
- Forms are tagged with access levels (free/basic/pro/enterprise)
- Users can only view checklists for forms they have access to
- Premium forms show "Upgrade" button

### Stripe Integration
- Checkout sessions for subscriptions
- Customer portal for managing subscriptions
- Webhook handling for subscription updates
- Automatic access control based on subscription status

### Admin Panel (Enterprise only)
- `POST /api/admin/forms` - Create new form
- `PUT /api/admin/forms/<id>` - Update form
- `DELETE /api/admin/forms/<id>` - Delete form

### API Endpoints
- `/api/documents` - List all documents (with access control)
- `/api/user/profile` - Get current user info
- `/api/create-checkout-session` - Start subscription
- `/api/create-portal-session` - Manage subscription

## Testing the App

1. **Browse forms**: Visit homepage to see all 11 forms
2. **Check access control**: Notice only 3 forms are unlocked (free tier)
3. **View pricing**: Click "Pricing" to see subscription tiers
4. **Try checklist**: Click on a premium form - see upgrade prompt

## Troubleshooting

**Database issues?**
```bash
rm immigration.db
python init_db.py
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Port already in use?**
Edit app.py and change port: `app.run(debug=True, port=5001)`

## Need Help?

Check the full README.md for:
- Complete API documentation
- Detailed setup instructions
- Deployment guide
- Database schema details
