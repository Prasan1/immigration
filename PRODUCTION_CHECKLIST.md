# Production Deployment Checklist

Complete this checklist before and during deployment to ensure everything is properly configured.

## Pre-Deployment (Do These First)

### 1. Stripe Setup
- [ ] Create Stripe account (if not already done)
- [ ] Switch to Live mode (not Test mode)
- [ ] Create Products:
  - [ ] Professional Plan - $39/month recurring
  - [ ] Team Plan - $149/month recurring
  - [ ] Business Plan - $299/month recurring
  - [ ] Passport Processing - $12 one-time
- [ ] Copy all Price IDs (save them for later)
- [ ] Note down Publishable Key and Secret Key

### 2. Clerk Setup
- [ ] Create Clerk account/application
- [ ] Get Publishable Key
- [ ] Get Secret Key
- [ ] Configure allowed origins (add your domain later)

### 3. Code Repository
- [ ] Create GitHub/GitLab repository
- [ ] Initialize git in project directory
- [ ] Commit all code
- [ ] Push to remote repository

### 4. Generate Secrets
Run this command and save the output:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
This will be your FLASK_SECRET_KEY.

## Deployment Steps

### 5. DigitalOcean Account
- [ ] Create DigitalOcean account
- [ ] Add payment method
- [ ] Verify you have ~$30/month budget

### 6. Create App Platform App
- [ ] Go to cloud.digitalocean.com
- [ ] Click "Create" → "Apps"
- [ ] Connect your Git repository
- [ ] Select repository and branch
- [ ] Review detected settings:
  - [ ] Build command: `pip install -r requirements.txt`
  - [ ] Run command: `gunicorn -c gunicorn.conf.py app:app`

### 7. Add PostgreSQL Database
- [ ] Click "Add Resource" → "Database"
- [ ] Select PostgreSQL
- [ ] Choose Basic plan ($15/month)
- [ ] Name: `immigration-db`
- [ ] Same region as app
- [ ] Click "Add Database"

### 8. Configure Environment Variables

In App Platform Settings → Environment Variables, add:

#### Required Variables
- [ ] `FLASK_ENV` = `production`
- [ ] `PORT` = `8000`
- [ ] `FLASK_SECRET_KEY` = `<your-generated-secret-from-step-4>`
- [ ] `CLERK_SECRET_KEY` = `<from-step-2>`
- [ ] `CLERK_PUBLISHABLE_KEY` = `<from-step-2>`
- [ ] `STRIPE_SECRET_KEY` = `<from-step-1>`
- [ ] `STRIPE_PUBLISHABLE_KEY` = `<from-step-1>`

#### Stripe Price IDs (from step 1)
- [ ] `STRIPE_PRICE_ID_BASIC` = `price_xxxxx`
- [ ] `STRIPE_PRICE_ID_PRO` = `price_xxxxx`
- [ ] `STRIPE_PRICE_ID_ENTERPRISE` = `price_xxxxx`
- [ ] `STRIPE_PRICE_ID_PASSPORT` = `price_xxxxx`

#### CORS (use your domain)
- [ ] `CORS_ORIGINS` = `https://yourdomain.com,https://www.yourdomain.com`

#### Optional (can add later)
- [ ] `STRIPE_WEBHOOK_SECRET` (configure after webhooks setup)

### 9. Deploy App
- [ ] Review configuration
- [ ] Click "Create Resources"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Check deployment logs for errors
- [ ] Note the temporary app URL (app-name.ondigitalocean.app)

### 10. Initialize Database
- [ ] Open App Platform Console
- [ ] Run: `python init_db.py`
- [ ] Verify: "Database tables created successfully!"

### 11. Test Basic Functionality
Using the temporary .ondigitalocean.app URL:
- [ ] Homepage loads correctly
- [ ] Can browse forms
- [ ] Pricing page displays
- [ ] Can create account (Clerk login)
- [ ] Dashboard loads for logged-in user

## Domain Configuration

### 12. Configure Your Domain
- [ ] In DO App Platform: Settings → Domains
- [ ] Click "Add Domain"
- [ ] Enter your domain name
- [ ] Add CNAME record to your DNS:
  - Name: `@` or `www`
  - Value: `<your-app>.ondigitalocean.app`
- [ ] Wait for DNS propagation (5 minutes - 24 hours)
- [ ] SSL certificate auto-provisions

### 13. Update Clerk Settings
- [ ] Add production domain to Clerk allowed origins
- [ ] Add both `https://yourdomain.com` and `https://www.yourdomain.com`

### 14. Configure Stripe Webhooks
- [ ] Go to stripe.com/dashboard/webhooks
- [ ] Click "Add Endpoint"
- [ ] URL: `https://yourdomain.com/api/stripe/webhook`
- [ ] Select events:
  - [ ] `checkout.session.completed`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
  - [ ] `payment_intent.succeeded`
- [ ] Copy Webhook Signing Secret
- [ ] Add to DO environment variables: `STRIPE_WEBHOOK_SECRET`
- [ ] Redeploy app to apply new env var

## Final Testing

### 15. End-to-End Testing on Production Domain
- [ ] Homepage loads on custom domain with HTTPS
- [ ] User signup works
- [ ] User login works
- [ ] Free forms accessible without subscription
- [ ] Subscription checkout flow works (use test card: 4242 4242 4242 4242)
- [ ] After subscribing, can access paid forms
- [ ] Passport application page loads (for paid users)
- [ ] Passport form submission works
- [ ] Payment for passport processing works
- [ ] Dashboard shows subscription status
- [ ] Team features work (Team/Business plans)
- [ ] Enterprise branding works (Business plan)

### 16. Stripe Live Mode
After testing with test cards:
- [ ] Switch Stripe to Live mode
- [ ] Update STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY in DO
- [ ] Redeploy app
- [ ] Test ONE real payment to verify

## Monitoring Setup

### 17. Set Up Monitoring
- [ ] Enable DO App Platform alerts
- [ ] Set up health check alerts
- [ ] Configure Slack/email notifications (optional)
- [ ] Review logs regularly for first week

### 18. Backups
- [ ] Verify database backups are enabled (auto-enabled)
- [ ] Test database restore process (optional but recommended)

## Post-Deployment

### 19. Documentation
- [ ] Share deployment URL with stakeholders
- [ ] Document admin credentials securely
- [ ] Note Stripe customer portal link for users

### 20. Launch Preparation
- [ ] Prepare marketing materials
- [ ] Set up support email
- [ ] Create user documentation
- [ ] Plan soft launch vs public launch

## Troubleshooting

If something doesn't work:

1. **Check logs:** App Platform → Runtime Logs
2. **Verify env vars:** All required variables set correctly?
3. **Database connection:** Is DATABASE_URL set? Is DB running?
4. **Stripe webhooks:** Is webhook secret correct?
5. **DNS:** Has DNS propagated? (use dnschecker.org)

## Estimated Timeline

- **Stripe & Clerk setup:** 30 minutes
- **Repository setup:** 15 minutes
- **DO deployment:** 30 minutes
- **Domain configuration:** 15 minutes + DNS wait time
- **Testing:** 1-2 hours
- **Total:** 3-4 hours (plus DNS propagation)

## Success Criteria

✅ App accessible on custom domain with HTTPS
✅ Users can sign up and log in
✅ Payments work in live mode
✅ Passport processing feature works
✅ No errors in production logs
✅ All subscription tiers function correctly

---

**You're ready for production!** 🎉

For issues, refer to:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [README.md](README.md) - Project documentation
- DigitalOcean docs: docs.digitalocean.com/products/app-platform/
