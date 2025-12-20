# Setting Up Stripe Webhooks for Production

## The Problem

When testing locally, Stripe webhooks **don't work** because Stripe can't reach `http://localhost:5000`.

That's why subscriptions don't update automatically after payment.

---

## TEMPORARY SOLUTION (For Testing)

✅ **"Sync Subscription" Button** - Added to Dashboard

After someone subscribes, they can click **"Sync Subscription"** on their dashboard to manually pull their subscription from Stripe and update their tier.

**This works for local testing but is NOT a long-term solution.**

---

## PRODUCTION SOLUTION (When You Deploy)

### Step 1: Deploy Your App

Deploy to any hosting platform:
- Railway
- Heroku
- DigitalOcean
- AWS
- Vercel (if using serverless)

Your app will have a public URL like: `https://yourdomain.com`

### Step 2: Set Up Webhook in Stripe Dashboard

1. Go to: https://dashboard.stripe.com/webhooks
2. Click **"Add endpoint"**
3. **Endpoint URL**: `https://yourdomain.com/api/stripe/webhook`
4. **Events to send**:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
5. Click **"Add endpoint"**

### Step 3: Get Webhook Secret

1. Click on the webhook you just created
2. Click **"Reveal"** next to "Signing secret"
3. Copy the secret (starts with `whsec_...`)
4. Add to your `.env` file:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
   ```
5. Restart your app

### Step 4: Test It

1. Make a test purchase
2. Check your app logs - you should see webhook events
3. User's subscription tier should update automatically
4. No manual "Sync" needed!

---

## For Local Testing (Optional - Advanced)

If you want to test webhooks locally before deploying:

### Install Stripe CLI

```bash
# Mac
brew install stripe/stripe-cli/stripe

# Linux
wget https://github.com/stripe/stripe-cli/releases/download/v1.17.0/stripe_1.17.0_linux_x86_64.tar.gz
tar -xvf stripe_1.17.0_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin
```

### Forward Webhooks to Localhost

```bash
stripe login
stripe listen --forward-to localhost:5000/api/stripe/webhook
```

You'll see output like:
```
> Ready! Your webhook signing secret is whsec_1234567890abcdef (^C to quit)
```

Copy that secret to your `.env`:
```
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef
```

Restart your Flask app. Now webhooks work locally!

### Test a Payment

Make a test purchase. You'll see webhook events in the terminal where `stripe listen` is running.

---

## Summary

| Environment | Solution |
|------------|----------|
| **Local Testing (Current)** | Click "Sync Subscription" button after purchase |
| **Local Testing (Advanced)** | Use Stripe CLI to forward webhooks |
| **Production (Required)** | Set up webhook endpoint in Stripe Dashboard |

---

## What the Webhook Does

When someone subscribes, Stripe sends a webhook event to your app:

```json
{
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "customer": "cus_...",
      "subscription": "sub_...",
      "metadata": {
        "user_id": "123",
        "tier": "enterprise"
      }
    }
  }
}
```

Your app's webhook handler (`/api/stripe/webhook`) receives this and:
1. Finds the user by `user_id`
2. Updates their `subscription_tier` to "enterprise"
3. Sets `subscription_status` to "active"
4. Saves to database

**This happens automatically in production once webhooks are configured!**
