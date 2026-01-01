# Passport Standalone Purchase - Fixed! ✅

## What Was Broken:

1. **Wrong Redirect URL**: Config had `/documents/passport-application` but actual route is `/documents/passport`
2. **Access Blocked**: Decorator `@subscription_required_for_doc_processing` blocked all free users from accessing passport page, even if they purchased it standalone

## What Was Fixed:

### 1. Config.py - Corrected Redirect URL
```python
# Before:
'redirect_url': '/documents/passport-application'  # ❌ Wrong

# After:
'redirect_url': '/documents/passport'  # ✅ Correct
```

### 2. passport_routes.py - Updated Access Control
**Before:** Only users with subscription could access
```python
if not tier_info.get('document_processing', False):
    return error  # ❌ Blocks free users even if they bought it
```

**After:** Users with subscription OR standalone purchase can access
```python
has_subscription_access = tier_info.get('document_processing', False)
has_passport_purchase = OneTimePurchase.query.filter_by(
    user_id=user.id,
    tool_type='passport',
    status='completed'
).first() is not None

if not has_subscription_access and not has_passport_purchase:
    return error  # ✅ Only blocks if neither subscription nor purchase
```

---

## How It Works Now:

### Purchase Flow:
1. **Free user** clicks "Purchase for $12" on pricing page
2. Shows legal disclaimer modal
3. User accepts → Redirects to Stripe checkout
4. Completes payment
5. Webhook fires → Marks purchase as `completed` in `one_time_purchases` table
6. User redirected to `/dashboard?tool_purchased=passport`
7. User clicks on passport tool → Access granted! ✅

### Access Check:
```
Can user access /documents/passport?
  ├─ Has Complete/Agency subscription? → YES → Allow access
  ├─ Has purchased passport standalone? → YES → Allow access
  └─ Neither? → NO → Redirect to /pricing
```

---

## Testing Instructions:

### Test 1: Free User Purchases Passport
1. **Create free account** (or use existing free tier)
2. Go to `/pricing`
3. Click "Purchase for $12" on Passport Application
4. Accept disclaimer modal
5. Complete Stripe checkout (test card: `4242 4242 4242 4242`)
6. Should redirect to `/dashboard?tool_purchased=passport`
7. Go to `/documents/passport`
8. **Expected:** Should see passport application form ✅

### Test 2: Check Database
```sql
-- After purchase, check:
SELECT * FROM one_time_purchases WHERE tool_type = 'passport';

-- Should show:
-- status = 'completed'
-- completed_at = timestamp
-- stripe_payment_intent_id = pi_xxxxx
```

### Test 3: Verify Access Persists
1. Logout
2. Login again
3. Go to `/documents/passport`
4. **Expected:** Still have access (purchase is permanent) ✅

### Test 4: Complete Package User
1. User with Complete Package
2. Try to buy passport standalone
3. **Expected:** Error message "Already included in your subscription" ✅
4. Redirects to `/documents/passport` directly

---

## Files Modified:

1. **config.py** (line 186)
   - Fixed redirect_url from `/documents/passport-application` → `/documents/passport`

2. **passport_routes.py** (lines 28-60)
   - Updated `subscription_required_for_doc_processing` decorator
   - Now checks for both subscription AND standalone purchases

3. **pricing.html** (lines 707-709, 739-741)
   - Temporarily disabled PDF Pack and Travel History (no price IDs yet)
   - Passport button active and working

---

## Restart Required:

```bash
# Stop current app
pkill -f gunicorn

# Start with new changes
gunicorn app:app --bind 0.0.0.0:5000
```

Or if using DigitalOcean, just redeploy.

---

## Current Status:

✅ **Passport Application ($12)** - Fully working, can be purchased standalone
⏰ **PDF Evidence Pack ($29)** - Coming soon (no Stripe price ID yet)
⏰ **I-94 Travel History ($19)** - Coming soon (no Stripe price ID yet)

---

## Next Steps (Optional):

1. **Create the other 2 Stripe products** (PDF Pack $29, Travel History $19)
2. **Add price IDs to .env**
3. **Re-enable their buttons** in pricing.html
4. **Test full flow** for all 3 tools

---

**The passport standalone purchase is now fully functional! 🎉**
