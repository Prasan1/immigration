# Production Deployment Checklist

Use this checklist when you're ready to deploy to DigitalOcean and go live.

## ✅ Pre-Deployment (Do This First)

### 1. Test Everything in Test Mode
- [ ] Test Complete Package purchase ($199 one-time)
- [ ] Test Agency subscription ($79/month)
- [ ] Test dashboard access after payment
- [ ] Test PDF compressor
- [ ] Test all features with different tier levels
- [ ] Test manual sync button (Refresh) works

### 2. Create Stripe Products in LIVE MODE
- [ ] Switch Stripe Dashboard to **LIVE MODE** (toggle top-right)
- [ ] Create product: "Complete Marriage Green Card Package"
  - Price: $199.00 USD
  - Billing: **One time**
  - Copy Price ID: `price_live_...`
- [ ] Create product: "Immigration Preparer Plan"
  - Price: $79.00 USD
  - Billing: **Monthly**
  - Copy Price ID: `price_live_...`

### 3. Set Up Stripe Webhook (LIVE MODE)
- [ ] In Stripe Dashboard (LIVE MODE): Developers → Webhooks → Add destination
- [ ] Webhook URL: `https://your-app-name.ondigitalocean.app/api/stripe/webhook`
- [ ] Select events:
  - [ ] `checkout.session.completed`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
- [ ] Click "Add destination"
- [ ] Copy Signing Secret: `whsec_live_...`

---

## 🚀 DigitalOcean Deployment

### 4. Deploy App to DigitalOcean
- [ ] Push latest code to GitHub: `git push origin main`
- [ ] Connect GitHub repo to DigitalOcean App Platform
- [ ] App Platform will auto-deploy
- [ ] Get production URL: `https://your-app-name.ondigitalocean.app`

### 5. Configure Environment Variables in DigitalOcean
Go to: App Platform → Your App → Settings → App-Level Environment Variables

Add these variables:

```bash
# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">

# Database (DigitalOcean will auto-populate if using managed database)
DATABASE_URL=postgresql://...

# Clerk Authentication (LIVE MODE)
CLERK_SECRET_KEY=sk_live_...
CLERK_PUBLISHABLE_KEY=pk_live_...

# Stripe (LIVE MODE)
STRIPE_SECRET_KEY=sk_live_51...
STRIPE_PUBLISHABLE_KEY=pk_live_51...
STRIPE_WEBHOOK_SECRET=whsec_live_...

# Stripe Price IDs (LIVE MODE)
STRIPE_PRICE_ID_COMPLETE=price_live_...
STRIPE_PRICE_ID_AGENCY=price_live_...

# Optional: Legacy price IDs (only if you have existing subscribers)
# STRIPE_PRICE_ID_BASIC=price_live_...
# STRIPE_PRICE_ID_PRO=price_live_...
# STRIPE_PRICE_ID_ENTERPRISE=price_live_...
```

- [ ] Click "Save"
- [ ] App will automatically redeploy with new environment variables

---

## 🧪 Post-Deployment Testing

### 6. Test Production App
- [ ] Visit production URL: `https://your-app-name.ondigitalocean.app`
- [ ] Test user signup (Clerk)
- [ ] Test login/logout
- [ ] **Make a REAL purchase with your own credit card** (you can refund it later)
  - [ ] Purchase Complete Package ($199)
  - [ ] Verify webhook fired (check user upgraded automatically)
  - [ ] Verify dashboard shows "Complete Package" badge
  - [ ] Test all features (PDF compressor, checklists, etc.)
- [ ] Refund your test purchase in Stripe Dashboard

### 7. Verify Webhooks Are Working
- [ ] Go to Stripe Dashboard → Developers → Webhooks → Your endpoint
- [ ] Click "View logs" tab
- [ ] Should see recent events with ✅ green checkmarks (200 responses)
- [ ] If you see ❌ errors, check your app logs in DigitalOcean

### 8. Test User Experience
- [ ] Sign up as a new user
- [ ] Purchase Complete Package
- [ ] Verify instant access (no manual refresh needed)
- [ ] Test PDF compressor (unlimited use)
- [ ] Test evidence organizer
- [ ] Test cover letter templates

---

## 🔒 Security Checklist

### 9. Production Security
- [ ] HTTPS is enabled (DigitalOcean App Platform does this automatically)
- [ ] `FLASK_ENV=production` is set
- [ ] Database uses strong password
- [ ] All secrets are in environment variables (not in code)
- [ ] `.env` file is in `.gitignore` (never committed to Git)

### 10. Stripe Security
- [ ] Using LIVE MODE keys (not test keys)
- [ ] Webhook signing secret is configured
- [ ] Test mode is disabled in production

---

## 💰 Going Live Checklist

### 11. Enable Real Payments
- [ ] Stripe account is verified (business documents, bank account)
- [ ] Payouts are enabled
- [ ] Tax settings configured (if required)
- [ ] Email receipts enabled in Stripe settings

### 12. Legal & Compliance
- [ ] Terms of Service page created
- [ ] Privacy Policy page created
- [ ] Refund policy documented (30-day money-back guarantee)
- [ ] Legal disclaimers added ("not a law firm", etc.)

### 13. Customer Support
- [ ] Support email set up (e.g., support@yourdomain.com)
- [ ] FAQ page created
- [ ] Help documentation written

---

## 📊 Monitoring & Analytics

### 14. Set Up Monitoring
- [ ] DigitalOcean app insights enabled
- [ ] Error logging configured
- [ ] Stripe webhook logs monitored
- [ ] Database backups enabled

### 15. Optional: Analytics
- [ ] Google Analytics installed (optional)
- [ ] Stripe Dashboard → Analytics reviewed regularly
- [ ] User signup/conversion tracking

---

## 🎉 Launch!

### 16. Soft Launch
- [ ] Test with friends/family first
- [ ] Collect feedback
- [ ] Fix any bugs
- [ ] Monitor for 24-48 hours

### 17. Public Launch
- [ ] Announce on social media
- [ ] Update marketing materials
- [ ] Monitor support requests
- [ ] Celebrate! 🎉

---

## 🆘 Troubleshooting Production Issues

### Webhook Not Working
1. Check Stripe Dashboard → Webhooks → Logs for errors
2. Check DigitalOcean logs for errors
3. Verify webhook URL is correct
4. Verify `STRIPE_WEBHOOK_SECRET` is set correctly
5. Test webhook manually:
   ```bash
   curl -X POST https://your-app.ondigitalocean.app/api/stripe/webhook
   ```
   Should return: `{"error": "Invalid signature"}` (this is good!)

### User Not Getting Upgraded
1. Check Stripe Dashboard → Payments - payment succeeded?
2. Check Stripe Dashboard → Webhooks → Logs - webhook fired?
3. Check DigitalOcean app logs - errors?
4. Manually sync: User clicks "Refresh" button on dashboard

### Database Connection Issues
1. Verify `DATABASE_URL` in environment variables
2. Check DigitalOcean database is running
3. Check database credentials are correct
4. Check database firewall allows app to connect

### Payments Failing
1. Check Stripe is in LIVE MODE
2. Check LIVE keys are configured (not test keys)
3. Check price IDs are correct (live, not test)
4. Test with your own card first

---

## 📞 Support Resources

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **Stripe Docs**: https://stripe.com/docs
- **Stripe Support**: support@stripe.com or live chat
- **Your App Logs**: DigitalOcean → App → Runtime Logs

---

## ✅ Final Checklist Before Launch

- [ ] All environment variables set in production
- [ ] Webhooks working (tested with real payment)
- [ ] Database connected and migrations run
- [ ] HTTPS working
- [ ] User signup/login working
- [ ] Payments working (tested with real card)
- [ ] User gets upgraded automatically after payment
- [ ] All features accessible to paid users
- [ ] Email receipts working
- [ ] Support email set up
- [ ] Legal pages created (Terms, Privacy)
- [ ] Monitoring enabled

**When all boxes are checked, you're ready to launch! 🚀**
