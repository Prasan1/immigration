# Production Deployment Checklist

## 🔑 Environment Variables to Change

### 1. Clerk Keys (REQUIRED)
```bash
# ❌ Development (current)
CLERK_SECRET_KEY=sk_test_Du66qDATL9d2QakIauN0fJqSxrRP5BjQHmI7gg4kRH
CLERK_PUBLISHABLE_KEY=pk_test_a25vd24tYWtpdGEtNDIuY2xlcmsuYWNjb3VudHMuZGV2JA

# ✅ Production (need to get from Clerk Dashboard)
CLERK_SECRET_KEY=sk_live_YOUR_PRODUCTION_KEY_HERE
CLERK_PUBLISHABLE_KEY=pk_live_YOUR_PRODUCTION_KEY_HERE
```

**Where to get:**
1. Go to https://dashboard.clerk.com
2. Switch to "Production" environment (toggle at top)
3. Go to API Keys
4. Copy both keys

---

### 2. Stripe Keys (REQUIRED for payments)
```bash
# ❌ Development (current)
STRIPE_SECRET_KEY=sk_test_51SeimP6jJK13wtE7...
STRIPE_PUBLISHABLE_KEY=pk_test_51SeimP6jJK13wtE7...

# ✅ Production (need to get from Stripe Dashboard)
STRIPE_SECRET_KEY=sk_live_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
```

**Where to get:**
1. Go to https://dashboard.stripe.com/apikeys
2. Switch to "Production" mode (toggle at top)
3. Reveal and copy "Secret key" and "Publishable key"

---

### 3. Stripe Webhook Secret (CRITICAL for production)
```bash
# ❌ Development (currently blank)
STRIPE_WEBHOOK_SECRET=

# ✅ Production (must set up webhook)
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
```

**How to set up:**
1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter URL: `https://yourdomain.com/api/webhooks/stripe`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Click "Add endpoint"
6. Copy the "Signing secret" (starts with `whsec_`)

**⚠️ IMPORTANT:** Without webhook, subscriptions won't sync automatically!

---

### 4. Stripe Price IDs (REQUIRED - different in production)
```bash
# ❌ Development (current test price IDs)
STRIPE_PRICE_ID_BASIC=price_1SeioK6jJK13wtE7agzR9g1m
STRIPE_PRICE_ID_PRO=price_1Seip46jJK13wtE76R75MmMU
STRIPE_PRICE_ID_ENTERPRISE=price_1SeipZ6jJK13wtE7ZkGM8svP

# ✅ Production (create new products in production mode)
STRIPE_PRICE_ID_BASIC=price_XXXXX_PRODUCTION
STRIPE_PRICE_ID_PRO=price_XXXXX_PRODUCTION
STRIPE_PRICE_ID_ENTERPRISE=price_XXXXX_PRODUCTION
```

**How to create:**
1. Switch Stripe to Production mode
2. Go to Products → Create Product
3. Create 3 products:
   - **Basic Plan** - $19.99/month recurring
   - **Pro Plan** - $49.99/month recurring
   - **Enterprise Plan** - $199.99/month recurring
4. Copy each Price ID

---

### 5. Flask Secret Key (CRITICAL for security)
```bash
# ❌ Development (current - EXPOSED in repo)
FLASK_SECRET_KEY=add08a535fbb97c94f4617c3ec70876179e98d7472294de1573a5a8feb64e621

# ✅ Production (generate NEW random key)
FLASK_SECRET_KEY=YOUR_COMPLETELY_NEW_RANDOM_SECRET_KEY
```

**Generate new key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**⚠️ NEVER reuse development secret in production!**

---

### 6. Flask Environment
```bash
# ❌ Development
FLASK_ENV=development

# ✅ Production
FLASK_ENV=production
```

---

### 7. Database (Recommended for production)
```bash
# ❌ Development (SQLite - not ideal for production)
DATABASE_URL=sqlite:///immigration.db

# ✅ Production (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@host:5432/database_name
```

**Why change:**
- SQLite is file-based, not ideal for concurrent users
- PostgreSQL is production-ready, scalable
- Most hosting platforms (Heroku, Render, Railway) provide PostgreSQL

---

## 🌐 Clerk Dashboard Production Settings

### Allowed Origins (Production URLs)
Go to Clerk Dashboard → Settings → Allowed origins

Add your production domain:
```
https://yourdomain.com
https://yourdomain.com/*
https://www.yourdomain.com
https://www.yourdomain.com/*
```

### Redirect URLs
Go to Settings → Paths

Set:
- **After sign-in URL**: `/dashboard`
- **After sign-up URL**: `/dashboard`
- **Sign-in URL**: `/login`
- **Sign-up URL**: `/signup`

### Email Settings (Optional but recommended)
- Add your custom email domain
- Configure email templates
- Set up "From" email address

---

## 🔒 Security Checklist

### Before Deploying:

- [ ] Generate new FLASK_SECRET_KEY (never reuse dev key)
- [ ] Switch to Clerk production keys (pk_live_, sk_live_)
- [ ] Switch to Stripe production keys (sk_live_, pk_live_)
- [ ] Create production Stripe products and price IDs
- [ ] Set up Stripe webhook with production endpoint
- [ ] Update DATABASE_URL to PostgreSQL (if using)
- [ ] Set FLASK_ENV=production
- [ ] Add production domain to Clerk allowed origins
- [ ] Remove any hardcoded secrets from code
- [ ] Ensure .env is in .gitignore (DON'T commit to git)
- [ ] Set up SSL/HTTPS (required by Clerk and Stripe)
- [ ] Test authentication flow in production
- [ ] Test payment flow with real card (then refund)
- [ ] Verify webhook is receiving events

---

## 📁 Environment File Structure

### Development (.env)
```bash
# Use for local development
FLASK_ENV=development
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
DATABASE_URL=sqlite:///immigration.db
```

### Production (.env.production or platform environment variables)
```bash
# Use on production server
FLASK_ENV=production
CLERK_SECRET_KEY=sk_live_...
CLERK_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_BASIC=price_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...
DATABASE_URL=postgresql://...
FLASK_SECRET_KEY=<NEW_RANDOM_KEY>
```

---

## 🚀 Deployment Platforms

### Recommended Platforms:

**1. Render.com** (Easiest)
- Free tier available
- Auto-deploy from GitHub
- Built-in PostgreSQL
- Set environment variables in dashboard

**2. Railway.app**
- Simple setup
- PostgreSQL included
- GitHub integration
- Usage-based pricing

**3. Heroku**
- Well-documented
- PostgreSQL add-on
- Free tier (with limitations)
- Dyno-based pricing

**4. DigitalOcean App Platform**
- More control
- PostgreSQL managed database
- Scalable infrastructure

### Setting Environment Variables:

All platforms support environment variables through their dashboard:
- Don't use .env file in production
- Set each variable individually in platform settings
- Platform will inject them at runtime

---

## ⚠️ Common Production Mistakes

### ❌ DON'T:
- Use test keys in production
- Commit .env file to git
- Reuse development FLASK_SECRET_KEY
- Skip webhook setup (subscriptions won't work)
- Use SQLite in production (unless very low traffic)
- Deploy without HTTPS/SSL

### ✅ DO:
- Use separate production keys for everything
- Set environment variables in platform dashboard
- Test payment flow before going live
- Monitor Stripe webhook events
- Use PostgreSQL for production database
- Enable HTTPS (required by Clerk and Stripe)
- Set up error monitoring (Sentry, etc.)

---

## 🧪 Testing Production Setup

### Before Launch:

1. **Test Authentication:**
   ```
   - Visit /login
   - Create new account
   - Verify redirect to /dashboard
   - Check user appears in Clerk dashboard
   - Test logout flow
   ```

2. **Test Payments:**
   ```
   - Use Stripe test card: 4242 4242 4242 4242
   - Subscribe to Basic plan
   - Verify redirect to success page
   - Check subscription in Stripe dashboard
   - Verify webhook received (check /api/webhooks/stripe logs)
   - Confirm user tier updated in database
   ```

3. **Test Access Control:**
   ```
   - As logged-out user: access free forms only
   - As free user: verify upgrade prompts on premium forms
   - As basic subscriber: access basic tier forms
   - As pro subscriber: access pro tier forms
   ```

4. **Test Checklist Preview:**
   ```
   - As anonymous user: see first 3 items + signup CTA
   - As logged-in user: see full checklist
   - Verify all tabs work correctly
   ```

---

## 📊 Post-Deployment Monitoring

### What to Monitor:

1. **Stripe Dashboard**
   - Successful checkouts
   - Failed payments
   - Webhook deliveries
   - Subscription status

2. **Clerk Dashboard**
   - User signups
   - Authentication errors
   - Active sessions

3. **Application Logs**
   - Server errors (500s)
   - Authentication failures
   - Database errors

4. **Database**
   - User records syncing from Clerk
   - Subscription tiers updating from Stripe
   - Data integrity

---

## 🆘 Troubleshooting

### Webhooks Not Working
- Check webhook URL is correct: `https://yourdomain.com/api/webhooks/stripe`
- Verify STRIPE_WEBHOOK_SECRET is set correctly
- Check webhook endpoint is accessible (not behind auth)
- Review Stripe webhook logs for delivery failures

### Authentication Errors
- Verify production keys are set correctly (sk_live_, pk_live_)
- Check allowed origins in Clerk dashboard
- Ensure redirect URLs are configured
- Verify HTTPS is enabled

### Payment Flow Breaking
- Confirm using production Stripe keys
- Verify price IDs match production products
- Check CORS settings if errors on checkout
- Test with Stripe test cards first

---

## 📞 Support Resources

- **Clerk Docs**: https://clerk.com/docs
- **Stripe Docs**: https://stripe.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/

---

**Last Updated:** 2025-12-16
**Version:** 1.0
