# Deployment Guide - DigitalOcean App Platform

This guide will walk you through deploying your Immigration Documents Portal to DigitalOcean App Platform.

## Prerequisites

- DigitalOcean account
- Domain name (you mentioned you already have one)
- Stripe account with API keys
- Clerk account for authentication
- Git repository (GitHub, GitLab, or Bitbucket)

## Cost Estimate

- **App Platform (Basic):** ~$12/month
- **PostgreSQL Database (Basic):** ~$15/month
- **Total:** ~$27/month

## Step-by-Step Deployment

### 1. Prepare Your Code

First, ensure your code is in a Git repository:

```bash
cd /home/ppaudyal/Documents/immigrations

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - production-ready immigration app"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/immigration-app.git

# Push
git push -u origin main
```

### 2. Create Stripe Products

Before deploying, create your Stripe products:

1. Go to https://dashboard.stripe.com/products
2. Create the following products:

**Subscription Products:**
- Professional Plan: $39/month recurring
- Team Plan: $149/month recurring
- Business Plan: $299/month recurring

**One-Time Products:**
- Passport Processing: $12.00 one-time

3. Copy the Price IDs for each product (they look like `price_xxxxxxxxxxxxx`)

### 3. Deploy to DigitalOcean App Platform

#### A. Create a New App

1. Log in to https://cloud.digitalocean.com
2. Click **"Create"** → **"Apps"**
3. Connect your Git repository:
   - Select your repository provider (GitHub/GitLab/Bitbucket)
   - Authorize DigitalOcean
   - Select your repository
   - Select the branch (usually `main`)

#### B. Configure Your App

1. **Source Directory:** Leave as root `/`
2. **Environment:** Select **Python**
3. **Build Command:** (Auto-detected from requirements.txt)
4. **Run Command:** `gunicorn -c gunicorn.conf.py app:app`

#### C. Add a Database

1. In the Resources section, click **"Add Resource"**
2. Select **"Database"**
3. Choose **PostgreSQL**
4. Select **Basic Plan ($15/month)**
5. Name it: `immigration-db`
6. Click **"Add Database"**

**Important:** DigitalOcean will automatically set the `DATABASE_URL` environment variable.

#### D. Configure Environment Variables

Click on **Settings** → **Environment Variables** and add:

```bash
# Environment
FLASK_ENV=production
PORT=8000

# Security - CRITICAL: Generate a strong secret
# Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
FLASK_SECRET_KEY=<your-generated-secret-key>

# Clerk Authentication
CLERK_SECRET_KEY=<your-clerk-secret-key>
CLERK_PUBLISHABLE_KEY=<your-clerk-publishable-key>

# Stripe
STRIPE_SECRET_KEY=<your-stripe-secret-key>
STRIPE_PUBLISHABLE_KEY=<your-stripe-publishable-key>
STRIPE_WEBHOOK_SECRET=<your-stripe-webhook-secret>

# Stripe Price IDs (from step 2)
STRIPE_PRICE_ID_BASIC=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_PRO=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_PASSPORT=price_xxxxxxxxxxxxx

# CORS - Use your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### E. Configure Your Domain

1. Go to **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain name
4. Follow DNS configuration instructions:
   - Add a CNAME record pointing to your app's URL
   - Wait for DNS propagation (up to 24 hours)
5. SSL certificate will be automatically provisioned

### 4. Configure Stripe Webhooks

1. Go to https://dashboard.stripe.com/webhooks
2. Click **"Add Endpoint"**
3. **Endpoint URL:** `https://yourdomain.com/api/stripe/webhook`
4. **Events to listen for:**
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `payment_intent.succeeded`
5. Copy the **Signing Secret** and update the `STRIPE_WEBHOOK_SECRET` environment variable in DigitalOcean

### 5. Initialize Production Database

After first deployment, run database initialization:

1. In DO App Platform, go to **Console**
2. Run:
```bash
python init_db.py
```

### 6. Test Your Deployment

1. Visit your domain: `https://yourdomain.com`
2. Test the following:
   - Homepage loads
   - User signup/login works
   - Pricing page displays correctly
   - Free forms are accessible
   - Subscription checkout works
   - Passport application form loads (for paid users)

## Monitoring & Maintenance

### View Logs

In DigitalOcean App Platform:
- **Runtime Logs:** Monitor real-time application logs
- **Build Logs:** Check deployment and build issues

### Database Backups

DigitalOcean automatically backs up your database daily. To configure:
1. Go to your database in DO
2. **Settings** → **Backups**
3. Daily backups are included

### Scaling

As your app grows, you can scale:
1. **App Resources:** Go to app settings → Resources → Upgrade plan
2. **Database:** Go to database settings → Resize

Recommended scaling path:
- Start: Basic ($12 + $15)
- Growth: Professional ($24 + $15)
- High Traffic: Production ($48 + $60)

## Troubleshooting

### App Won't Start

Check logs for:
- Missing environment variables
- Database connection errors
- Import errors

### Database Connection Issues

Ensure:
- DATABASE_URL is set (auto-set by DO)
- Database is running
- App and database are in the same region

### Stripe Webhook Not Working

Verify:
- Webhook URL is correct
- STRIPE_WEBHOOK_SECRET is set
- Events are selected correctly

## Security Checklist

✅ Strong SECRET_KEY generated
✅ All environment variables set in DO (not in code)
✅ HTTPS enabled (automatic with DO)
✅ CORS origins restricted to your domain
✅ Rate limiting enabled
✅ Security headers configured (Talisman)
✅ Database credentials secured

## Post-Deployment

1. **Update Clerk:** Add your production domain to allowed origins
2. **Test payments:** Use Stripe test mode first, then switch to live
3. **Monitor errors:** Check logs regularly
4. **Set up alerts:** Configure DO alerts for app health

## Support

If you encounter issues:
- Check DigitalOcean logs first
- Review this deployment guide
- Check Stripe dashboard for payment issues
- Verify all environment variables are set

---

**Deployment completed!** Your app should now be live at your custom domain with SSL, production database, and all security features enabled.
