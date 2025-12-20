# Stripe Webhooks Explained (Simple Version)

## What are Webhooks?

Webhooks are like text messages from Stripe to your app saying "Hey, something happened!"

## Example Scenario

**Without Webhooks:**
1. User subscribes on your site
2. Stripe charges them
3. ❌ Your app doesn't know they paid
4. ❌ User still can't access premium forms
5. 😞 User is confused and upset

**With Webhooks:**
1. User subscribes on your site
2. Stripe charges them
3. ✅ Stripe tells your app "Payment successful!"
4. ✅ Your app unlocks premium forms
5. 😊 User is happy

## Do You Need Webhooks Right Away?

### For Testing Locally: **NO**
- You can manually grant access
- Good for development
- Skip webhooks for now

### For Production: **YES**
- Automatic subscription management
- Better user experience
- Professional SaaS

## When Do You Get the Webhook Secret?

**Only when you set up webhooks in Stripe:**

1. Log into Stripe Dashboard
2. Go to **Developers → Webhooks**
3. Click **"Add endpoint"**
4. Enter your URL: `https://yourdomain.com/api/stripe/webhook`
5. Select events to listen for
6. Stripe generates a webhook secret: `whsec_...`
7. Copy that secret to your `.env` file

**Before you do this:** You don't have a webhook secret, and that's fine!

## What Can You Do Without Webhooks?

### ✅ Still Works:
- Users browse free forms
- Users can sign up (with Clerk)
- Stripe checkout page opens
- Users can pay
- You get the money in Stripe

### ❌ Doesn't Work Automatically:
- User access isn't granted automatically
- Subscription cancellations don't update
- Subscription upgrades don't sync

### 🔧 Manual Workaround:
You can manually update users in the database:

```sql
-- Grant user Pro access
UPDATE users
SET subscription_tier = 'pro',
    subscription_status = 'active'
WHERE email = 'user@example.com';
```

## Simple Setup When Ready (5 minutes)

### Step 1: Get to Production
First deploy your app to a real domain (not localhost):
- Heroku
- Railway
- DigitalOcean
- Vercel
- Any hosting

### Step 2: Set Up Webhook in Stripe

1. **Stripe Dashboard** → **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. **Endpoint URL**: `https://yourapp.com/api/stripe/webhook`
4. **Events to send**:
   - `checkout.session.completed` ← User paid
   - `customer.subscription.updated` ← Subscription changed
   - `customer.subscription.deleted` ← User cancelled

5. Click **"Add endpoint"**

### Step 3: Get Webhook Secret

After creating the endpoint:
1. Click on your new webhook
2. Click **"Reveal"** next to "Signing secret"
3. Copy the secret (starts with `whsec_...`)
4. Add to `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
   ```

### Step 4: Restart Your App

```bash
python app.py
```

Done! Now webhooks work automatically.

## Testing Webhooks Locally (Advanced)

If you want to test webhooks on localhost:

1. Install Stripe CLI:
   ```bash
   brew install stripe/stripe-cli/stripe
   # or download from stripe.com/docs/stripe-cli
   ```

2. Login to Stripe:
   ```bash
   stripe login
   ```

3. Forward webhooks to localhost:
   ```bash
   stripe listen --forward-to localhost:5000/api/stripe/webhook
   ```

4. Stripe CLI will show you a webhook secret
5. Use that secret in your `.env`
6. Test by making a payment
7. See webhook events in your terminal

## Summary

**For Policygen:** You probably didn't use webhooks because:
- You handled subscriptions manually, OR
- You used a simpler payment flow, OR
- It was for testing only

**For This App:**
- ✅ App works now without webhooks
- ✅ Free forms accessible
- ⏳ Set up webhooks when you deploy
- ⏳ Takes 5 minutes in Stripe Dashboard
- ✅ Copy one secret to `.env`

**Bottom Line:** Don't worry about webhooks until you're ready to launch. Your app works fine for testing without them!

---

## Quick Reference

```bash
# .env file - What you need NOW
FLASK_SECRET_KEY=anything_random_here_123456

# .env file - What you need LATER (when deploying)
CLERK_SECRET_KEY=sk_test_...          # From clerk.com
STRIPE_SECRET_KEY=sk_test_...         # From stripe.com
STRIPE_WEBHOOK_SECRET=whsec_...       # From Stripe webhook setup
```

Start with just `FLASK_SECRET_KEY`, add the rest when ready! 🚀
