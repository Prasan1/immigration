# Clerk Authentication Setup Guide

## What's Been Implemented

✅ **Freemium Model** - 3 forms free without login
✅ **Auth Pages** - /login and /signup routes
✅ **Session Management** - User session handling
✅ **Access Control** - Premium forms require authentication
✅ **Redirect Flow** - Sign in buttons redirect to /login

## What You Need to Do

To enable full authentication, set up Clerk (takes ~10 minutes):

### Step 1: Create Clerk Account

1. Go to **https://clerk.com**
2. Click "Start Building for Free"
3. Sign up with your email or GitHub

### Step 2: Create Application

1. Once logged in, click "Create Application"
2. Name it: `Immigration Forms SaaS`
3. Choose authentication methods:
   - ✅ Email + Password (recommended)
   - ✅ Google OAuth (optional, increases conversions)
   - ✅ GitHub OAuth (optional, for developers)
4. Click "Create Application"

### Step 3: Get Your API Keys

In your Clerk Dashboard:

1. Go to **"API Keys"** in the left sidebar
2. You'll see:
   - **Publishable Key** (starts with `pk_test_...`)
   - **Secret Key** (starts with `sk_test_...`)
3. Copy both keys

### Step 4: Add Keys to .env File

Edit `/home/ppaudyal/Documents/immigrations/.env`:

```bash
# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE
```

Replace `YOUR_KEY_HERE` with your actual keys from Step 3.

### Step 5: Configure Clerk Settings

In Clerk Dashboard → **Settings**:

#### Allowed Redirect URLs
Add these URLs (for local development):
```
http://localhost:5000
http://localhost:5000/*
http://localhost:5000/dashboard
```

#### Sign-in/Sign-up Pages
- **After sign-in URL**: `/dashboard`
- **After sign-up URL**: `/dashboard`
- **Sign-in URL**: `/login`
- **Sign-up URL**: `/signup`

### Step 6: Install Clerk Frontend (Choose One Option)

#### Option A: Use Clerk Components (Recommended)

Add to `templates/auth.html` (replace the current setup notice):

```html
<div id="clerk-sign-in"></div>

<script>
    const clerk = new Clerk('{{ config.CLERK_PUBLISHABLE_KEY }}');
    await clerk.load();

    clerk.mountSignIn(document.getElementById('clerk-sign-in'), {
        afterSignInUrl: '/dashboard',
        signUpUrl: '/signup'
    });
</script>
```

#### Option B: Use Clerk Hosted Pages

Update `app.py` to redirect to Clerk's hosted pages:

```python
@app.route('/login')
def login():
    # Redirect to Clerk's hosted sign-in
    redirect_url = f"https://accounts.clerk.dev/sign-in?redirect_url={request.host_url}dashboard"
    return redirect(redirect_url)
```

### Step 7: Handle User Sessions

Update `app.py` authentication to verify Clerk tokens:

```python
import requests
from functools import wraps

def verify_clerk_session():
    """Verify Clerk session token"""
    token = request.cookies.get('__session')  # Clerk's session cookie

    if not token:
        return None

    # Verify with Clerk API
    headers = {'Authorization': f'Bearer {Config.CLERK_SECRET_KEY}'}
    response = requests.get(
        f'https://api.clerk.dev/v1/sessions/{token}',
        headers=headers
    )

    if response.status_code == 200:
        session_data = response.json()
        return session_data.get('user_id')

    return None
```

### Step 8: Create User on First Sign-In

Add webhook handler for new users:

```python
@app.route('/api/clerk/webhook', methods=['POST'])
def clerk_webhook():
    """Handle Clerk webhooks for user creation"""
    data = request.json

    if data['type'] == 'user.created':
        user_data = data['data']

        # Create user in database
        user = User(
            clerk_user_id=user_data['id'],
            email=user_data['email_addresses'][0]['email_address'],
            full_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        )
        db.session.add(user)
        db.session.commit()

    return jsonify({'success': True})
```

### Step 9: Configure Webhooks in Clerk

1. In Clerk Dashboard → **Webhooks**
2. Click "Add Endpoint"
3. **Endpoint URL**: `https://your-domain.com/api/clerk/webhook`
4. **Events to listen to**:
   - `user.created`
   - `user.updated`
   - `user.deleted`
5. Copy the webhook secret
6. Add to `.env`: `CLERK_WEBHOOK_SECRET=whsec_...`

### Step 10: Test Authentication

1. Restart your Flask app:
   ```bash
   python app.py
   ```

2. Visit **http://localhost:5000/forms**

3. Click a premium form → Click "Sign Up"

4. You should see Clerk's sign-up form

5. Create an account → Should redirect to `/dashboard`

6. Verify you can access premium forms

## Current State (Without Clerk)

Right now, the app works with:

✅ **Free Forms** - Fully accessible (I-130, I-485, N-400)
✅ **Premium Forms** - Shows "Sign Up" button
✅ **Auth Page** - Shows setup instructions
✅ **Freemium Flow** - Complete UX without auth

Users can:
- Browse all forms
- Use 3 free forms without login
- See what they're missing
- Click to sign up (shows setup page)

## Alternative: Mock Authentication (For Testing)

If you want to test without Clerk, add a demo login:

```python
@app.route('/demo-login')
def demo_login():
    """Demo login for testing"""
    # Create or get demo user
    user = User.query.filter_by(email='demo@example.com').first()

    if not user:
        user = User(
            clerk_user_id='demo_user_001',
            email='demo@example.com',
            full_name='Demo User',
            subscription_tier='pro',  # Give Pro access for testing
            subscription_status='active'
        )
        db.session.add(user)
        db.session.commit()

    # Set session
    session['clerk_user_id'] = user.clerk_user_id

    return redirect('/dashboard')
```

Then add a button on `/login` page to trigger demo login.

## Production Checklist

When deploying to production:

- [ ] Switch Clerk to production keys (pk_live_... and sk_live_...)
- [ ] Update allowed redirect URLs to production domain
- [ ] Configure custom domain in Clerk
- [ ] Set up proper webhook endpoint (HTTPS required)
- [ ] Test full authentication flow
- [ ] Test subscription upgrades
- [ ] Monitor Clerk dashboard for usage

## Support

**Clerk Documentation**: https://clerk.com/docs
**Clerk Discord**: https://clerk.com/discord
**API Reference**: https://clerk.com/docs/reference/backend-api

**Need Help?**
- Check Clerk's quickstart guide
- Ask in their Discord community
- Review example implementations on GitHub

---

## Summary

**What Works Now:**
- ✅ Freemium model (3 free forms, no login)
- ✅ Beautiful UI with access controls
- ✅ Premium form previews
- ✅ Auth page with setup instructions

**What Needs Clerk:**
- ⏳ Actual sign-up/login functionality
- ⏳ User sessions and dashboard access
- ⏳ Subscription management
- ⏳ Premium form unlocking

**Time to Set Up:** ~10-15 minutes with this guide

Once Clerk is configured, your SaaS will have:
- Professional authentication
- User management
- Session handling
- Social logins
- Security out of the box

Ready to launch! 🚀
