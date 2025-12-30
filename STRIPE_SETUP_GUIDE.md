# Stripe Setup Guide - Marriage-Based Immigration Pricing

This guide will walk you through setting up your Stripe products and price IDs for the new marriage-focused pricing model.

## Overview

You need to create **2 products** in Stripe:

1. **Complete Package** - $199 one-time payment
2. **Immigration Preparer** - $79/month subscription

---

## Step 1: Log into Stripe Dashboard

1. Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Log in to your account
3. Make sure you're in **TEST MODE** first (toggle in top right)

---

## Step 2: Create Complete Package (One-Time Payment)

### Create the Product

1. Click **Products** in the left sidebar
2. Click **+ Add product** button
3. Fill in the details:
   - **Name**: `Complete Marriage Green Card Package`
   - **Description**: `Everything you need to file I-130, I-485, I-864, I-765, I-131 with confidence. Lifetime access to checklists, cover letter templates, PDF compressor, and more.`
   - **Image**: (Optional) Upload a product image

### Create the Price

4. Under **Pricing**, configure:
   - **Pricing model**: `Standard pricing`
   - **Price**: `$199.00 USD`
   - **Billing period**: `One time`
   - **Payment type**: `One-time payment`

5. Click **Save product**

6. **Copy the Price ID**:
   - After saving, you'll see a **Price ID** that looks like `price_1AbCdEfGhIjKlMnO`
   - Copy this ID - you'll need it for your `.env` file

---

## Step 3: Create Immigration Preparer (Subscription)

### Create the Product

1. Click **+ Add product** again
2. Fill in the details:
   - **Name**: `Immigration Preparer Plan`
   - **Description**: `For immigration consultants, preparers, and agencies filing multiple cases. Unlimited client cases, white-label branding, team collaboration.`
   - **Image**: (Optional) Upload a product image

### Create the Price

3. Under **Pricing**, configure:
   - **Pricing model**: `Standard pricing`
   - **Price**: `$79.00 USD`
   - **Billing period**: `Monthly`
   - **Payment type**: `Recurring`
   - **Trial period**: (Optional) Leave blank or set trial days

4. Click **Save product**

5. **Copy the Price ID**:
   - After saving, copy the **Price ID** (e.g., `price_1XyZaBcDeFgHiJkL`)

---

## Step 4: Update Your .env File

Add the new price IDs to your `.env` file:

```bash
# New Stripe Price IDs (Marriage-Based Immigration Model)
STRIPE_PRICE_ID_COMPLETE=price_1AbCdEfGhIjKlMnO
STRIPE_PRICE_ID_AGENCY=price_1XyZaBcDeFgHiJkL
```

**Full Stripe Configuration Example:**

```bash
# Stripe Keys
STRIPE_SECRET_KEY=sk_test_51...your_test_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_51...your_test_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_...your_webhook_secret

# New Stripe Price IDs (Marriage-Based Immigration Model)
STRIPE_PRICE_ID_COMPLETE=price_1AbCdEfGhIjKlMnO
STRIPE_PRICE_ID_AGENCY=price_1XyZaBcDeFgHiJkL

# Old Price IDs (Keep for backward compatibility with existing subscribers)
STRIPE_PRICE_ID_BASIC=price_old_basic_id
STRIPE_PRICE_ID_PRO=price_old_pro_id
STRIPE_PRICE_ID_ENTERPRISE=price_old_enterprise_id
```

---

## Step 5: Test the Integration

### Test Complete Package (One-Time Payment)

1. Start your Flask app: `python app.py` or `gunicorn -c gunicorn.conf.py app:app`
2. Go to `/pricing`
3. Click **Get Complete Package - $199**
4. You should be redirected to Stripe Checkout
5. Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits
6. Complete the payment
7. Verify you're redirected to `/dashboard?success=true`
8. Check Stripe Dashboard → Payments to see the one-time payment

### Test Immigration Preparer (Subscription)

1. Go to `/pricing`
2. Click **Start Agency Plan**
3. Use Stripe test card: `4242 4242 4242 4242`
4. Complete the subscription
5. Check Stripe Dashboard → Subscriptions to see the recurring subscription

---

## Step 6: Set Up Webhooks (Important!)

For production, you need to handle Stripe webhooks to automatically update user subscriptions.

### Create Webhook Endpoint

1. In Stripe Dashboard, go to **Developers → Webhooks**
2. Click **+ Add endpoint**
3. Enter your webhook URL:
   - **Test mode**: `https://your-app.com/api/stripe-webhook`
   - **Live mode**: `https://your-production-domain.com/api/stripe-webhook`
4. Select events to listen to:
   - `checkout.session.completed` (for both one-time and subscriptions)
   - `payment_intent.succeeded` (for one-time payments)
   - `invoice.payment_succeeded` (for subscription renewals)
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Webhook signing secret** (looks like `whsec_...`)
6. Add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

---

## Step 7: Go Live (Production)

### Switch to Live Mode

1. Toggle Stripe Dashboard to **LIVE MODE**
2. Repeat Steps 2-3 to create products in **Live Mode**
3. Update `.env` with **live** price IDs and keys:

```bash
# Live Stripe Keys (for production)
STRIPE_SECRET_KEY=sk_live_51...your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_51...your_live_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_...your_live_webhook_secret

# Live Price IDs
STRIPE_PRICE_ID_COMPLETE=price_live_complete_id
STRIPE_PRICE_ID_AGENCY=price_live_agency_id
```

### Important Production Notes

- **Test thoroughly** in test mode before going live
- Set up **tax collection** if required (Stripe Tax)
- Enable **payment method types**: Card, Apple Pay, Google Pay
- Set up **email receipts** in Stripe settings
- Configure **refund policy** (30-day money-back guarantee)

---

## Pricing Summary

| Plan | Price | Type | Stripe Mode |
|------|-------|------|-------------|
| Free Starter | $0 | Free | N/A |
| Complete Package | $199 | One-time | `mode='payment'` |
| Immigration Preparer | $79/month | Subscription | `mode='subscription'` |

---

## Troubleshooting

### Error: "Price ID not configured"

- **Cause**: Missing price ID in `.env`
- **Fix**: Add `STRIPE_PRICE_ID_COMPLETE` and `STRIPE_PRICE_ID_AGENCY` to `.env`

### Error: "No such price"

- **Cause**: Wrong price ID or using test ID in live mode
- **Fix**: Verify you're using the correct price ID for your mode (test vs live)

### Checkout session not redirecting

- **Cause**: Incorrect success/cancel URLs
- **Fix**: Verify URLs in `app.py` match your domain

### User not getting access after payment

- **Cause**: Webhooks not working
- **Fix**:
  1. Check webhook is created in Stripe Dashboard
  2. Verify webhook secret in `.env`
  3. Test webhook with Stripe CLI: `stripe listen --forward-to localhost:5000/api/stripe-webhook`

---

## Testing with Stripe CLI (Optional but Recommended)

Install Stripe CLI:

```bash
# Mac
brew install stripe/stripe-cli/stripe

# Linux
curl -s https://stripe.com/cli | bash

# Windows
Download from https://github.com/stripe/stripe-cli/releases
```

Test webhooks locally:

```bash
# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to http://localhost:5000/api/stripe-webhook

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger payment_intent.succeeded
```

---

## Next Steps

After completing this setup:

1. ✅ Test both payment flows (one-time and subscription)
2. ✅ Verify user access is granted after payment
3. ✅ Test webhook handling
4. ✅ Test refund flow (if implementing 30-day guarantee)
5. ✅ Set up Stripe Tax (if required for your jurisdiction)
6. ✅ Configure email notifications
7. ✅ Add Stripe customer portal for subscription management

---

## Support

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: https://support.stripe.com
- **Test Cards**: https://stripe.com/docs/testing#cards

---

**Important**: Never commit your `.env` file to Git! Add it to `.gitignore`:

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```
