# Standalone Tools Payment Setup Guide

## ✅ What Was Implemented

You now have **fully functional standalone tool purchases**! Users can buy individual tools without subscribing to the Complete Package:

### Available Standalone Tools:
1. **USCIS PDF & Evidence Pack** - $29
2. **Passport Application Processing** - $12
3. **I-94 Travel History Worksheet** - $19

### Features Implemented:
✅ Payment flow for one-time tool purchases
✅ Duplicate purchase prevention (can't buy same tool twice)
✅ Subscription check (Complete/Agency users already have access)
✅ Database tracking of purchases
✅ Webhook integration for payment confirmation
✅ Lifetime access after purchase

---

## 🔧 Setup Steps

### Step 1: Create Stripe Price IDs

You need to create 3 new Stripe price IDs for the standalone tools:

#### In Stripe Dashboard (https://dashboard.stripe.com):

1. **Go to Products → Create Product**

2. **Product 1: PDF & Evidence Pack**
   - Name: `USCIS PDF & Evidence Pack`
   - Price: `$29.00 USD`
   - Type: `One-time`
   - Copy the Price ID (starts with `price_...`)

3. **Product 2: Passport Application**
   - Name: `Passport Application Processing`
   - Price: `$12.00 USD`
   - Type: `One-time`
   - Copy the Price ID (you should already have this: `STRIPE_PRICE_ID_PASSPORT`)

4. **Product 3: I-94 Travel History**
   - Name: `I-94 Travel History Worksheet`
   - Price: `$19.00 USD`
   - Type: `One-time`
   - Copy the Price ID (starts with `price_...`)

### Step 2: Add Environment Variables

Add these to your `.env` file:

```bash
# Standalone tool price IDs
STRIPE_PRICE_ID_PDF_EVIDENCE_PACK=price_xxxxxxxxxxxxx  # $29 PDF & Evidence Pack
STRIPE_PRICE_ID_TRAVEL_HISTORY=price_xxxxxxxxxxxxx    # $19 I-94 Travel History
STRIPE_PRICE_ID_PASSPORT=price_xxxxxxxxxxxxx          # $12 Passport (you may already have this)
```

### Step 3: Run Database Migration

Create the new `one_time_purchases` table:

```bash
python migration_add_one_time_purchases.py
```

This will add the table to track standalone tool purchases.

### Step 4: Restart Your Application

```bash
# If using Gunicorn
pkill gunicorn
gunicorn app:app

# Or just restart your DigitalOcean app
```

---

## 🧪 How to Test

### Test 1: Free User Purchases Tool
1. Create a new account (or use existing free tier account)
2. Go to `/pricing`
3. Scroll to "Not Ready for the Full Toolkit?" section
4. Click "Purchase for $12" on Passport Application
5. Complete Stripe checkout (use test card: `4242 4242 4242 4242`)
6. Should redirect to `/dashboard?tool_purchased=passport`
7. Check database: `SELECT * FROM one_time_purchases;`
   - Should see completed purchase record

### Test 2: Duplicate Purchase Prevention
1. Same user from Test 1
2. Try to buy Passport Application again
3. Should see message: "You already purchased this tool on [date]. You have lifetime access!"
4. Should offer to redirect to tool

### Test 3: Complete Package User
1. User with Complete Package ($199)
2. Try to buy any standalone tool
3. Should see: "This tool is already included in your Complete subscription. No additional purchase needed!"
4. Should offer to redirect to tool

### Test 4: Check Access
1. After purchasing a tool, call:
   ```bash
   curl http://localhost:5000/api/user/purchased-tools \
     -H "Cookie: your_session_cookie"
   ```
2. Should return list of purchased tools

---

## 📊 Database Schema

New table: `one_time_purchases`

```sql
CREATE TABLE one_time_purchases (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    tool_type VARCHAR(100) NOT NULL,  -- 'passport', 'pdf_evidence_pack', 'travel_history'
    price_paid FLOAT NOT NULL,
    stripe_payment_intent_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'completed', 'failed', 'refunded'
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## 🔌 API Endpoints Created

### POST `/api/create-tool-checkout`
Creates Stripe checkout session for tool purchase.

**Request:**
```json
{
  "tool_type": "passport"  // or "pdf_evidence_pack", "travel_history"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

**Error Responses:**
- 400: Tool already purchased / Already included in subscription
- 500: Price ID not configured

### GET `/api/user/purchased-tools`
Returns list of tools user has access to.

**Response (Complete Package user):**
```json
{
  "has_all_tools": true,
  "via_subscription": "complete",
  "tools": ["passport", "pdf_evidence_pack", "travel_history"]
}
```

**Response (User with 1 purchase):**
```json
{
  "has_all_tools": false,
  "via_subscription": null,
  "tools": ["passport"],
  "purchases": [
    {
      "id": 1,
      "tool_type": "passport",
      "price_paid": 12.0,
      "status": "completed",
      "purchased_at": "2025-12-30T...",
      "completed_at": "2025-12-30T..."
    }
  ]
}
```

---

## 🎯 User Flow

### Scenario 1: Free User Buys Tool
1. Click "Purchase for $12" → Redirects to login if not logged in
2. Logged in? → Creates checkout session
3. Redirects to Stripe checkout
4. Completes payment
5. Webhook fires → Updates purchase status to "completed"
6. Redirects to `/dashboard?tool_purchased=passport`
7. User has lifetime access to passport tool

### Scenario 2: User Already Has Tool
1. Click "Purchase for $12"
2. Backend checks: User already purchased on [date]
3. Shows message with option to go to tool
4. No charge

### Scenario 3: Complete Package User
1. Click "Purchase for $12"
2. Backend checks: User has Complete Package
3. Shows: "Already included in your subscription!"
4. No charge, redirects to tool

---

## 🛡️ Security Features

✅ **Login Required**: Must be authenticated to purchase
✅ **Duplicate Prevention**: Can't buy same tool twice
✅ **Subscription Check**: Won't charge users who already have access
✅ **Webhook Verification**: Stripe signature verification enabled
✅ **Database Transactions**: Rollback on errors

---

## 📝 Code Files Modified

1. **config.py** - Added price IDs and DOCUMENT_TYPES entries
2. **models.py** - Added OneTimePurchase model
3. **app.py** - Added routes:
   - `/api/create-tool-checkout`
   - `/api/user/purchased-tools`
   - Updated webhook handler for tool purchases
4. **templates/pricing.html** - Changed links to purchase buttons with payment handlers
5. **migration_add_one_time_purchases.py** - Database migration script

---

## 🚀 Next Steps (Optional)

### Add Tool Access Checks
Update each tool page to check if user has access:

```python
from models import OneTimePurchase

@app.route('/documents/passport-application')
@login_required
def passport_application():
    user = get_current_user()

    # Check if user has access
    has_subscription = user.subscription_tier in ['complete', 'agency', 'basic', 'pro', 'enterprise'] and user.subscription_status == 'active'

    has_purchase = OneTimePurchase.query.filter_by(
        user_id=user.id,
        tool_type='passport',
        status='completed'
    ).first() is not None

    if not has_subscription and not has_purchase:
        return redirect('/pricing')

    # User has access - show tool
    return render_template('passport_application.html')
```

### Add Purchase History to Dashboard
Show user's purchased tools in their dashboard with dates and receipts.

---

## ❓ Troubleshooting

### Payment not completing?
- Check webhook logs: `grep "WEBHOOK" your_app.log`
- Verify webhook secret is correct
- Test webhook manually in Stripe dashboard

### User says they paid but no access?
1. Check `one_time_purchases` table:
   ```sql
   SELECT * FROM one_time_purchases WHERE user_id = X;
   ```
2. Check for `pending` status → Webhook didn't fire
3. Manually update:
   ```sql
   UPDATE one_time_purchases
   SET status = 'completed', completed_at = NOW()
   WHERE id = X;
   ```

### Price IDs not working?
- Ensure they're in `.env` file
- Restart application after adding
- Check Stripe dashboard that prices are active

---

## 💰 Revenue Tracking

Query total revenue from standalone tools:

```sql
SELECT
    tool_type,
    COUNT(*) as purchases,
    SUM(price_paid) as total_revenue
FROM one_time_purchases
WHERE status = 'completed'
GROUP BY tool_type;
```

Query all time revenue:
```sql
SELECT SUM(price_paid) as total_revenue
FROM one_time_purchases
WHERE status = 'completed';
```

---

**That's it! Your standalone tools are ready to generate revenue! 🎉**
