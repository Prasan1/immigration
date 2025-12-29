# Quick Testing Guide - File Compressor

## Session Fix Applied ✅

I've fixed the session persistence issue. The session will now properly persist for 24 hours after login.

---

## Easiest Way to Test (Development Mode Only)

### Option 1: One-Click Dev Login
Simply visit:
```
http://localhost:5000/dev-login
```

This will:
1. Create a test user (if doesn't exist)
2. Log you in automatically
3. Redirect you to `/file-compressor`
4. Give you Professional tier access (unlimited premium compression)

**Note:** This endpoint only works in development mode (`FLASK_ENV=development`).

---

## Test the File Compressor

Once logged in via `/dev-login`, you should see:
- **"Unlimited Premium Compression Available"** badge
- Upload zone with drag & drop
- No payment required (you have Professional tier)

### Test Steps:

1. **Find a test PDF**
   - Any PDF file will work
   - Can be up to 50MB (you have premium access)

2. **Upload the PDF**
   - Drag & drop onto the upload zone
   - OR click to browse

3. **Compress the file**
   - Click "Use Free Compression" (will actually use premium since you're Professional tier)
   - Wait for compression to complete (~2-5 seconds)

4. **Download compressed file**
   - Click the Download button
   - Compare file sizes

5. **Check recent compressions**
   - Scroll down to see your compression history
   - View file sizes and compression ratios

---

## Testing Premium Payment ($5)

To test the payment flow:

1. **Logout first** (to become a free user):
   ```javascript
   // In browser console:
   fetch('/api/auth/logout', {method: 'POST'})
     .then(() => window.location.reload());
   ```

2. **Visit `/dev-login` again** but this time modify test user:
   ```bash
   # In terminal:
   python -c "
   from app import app, db
   from models import User
   with app.app_context():
       user = User.query.filter_by(email='test@example.com').first()
       if user:
           user.subscription_tier = 'free'
           user.subscription_status = 'inactive'
           db.session.commit()
           print('Test user set to free tier')
   "
   ```

3. **Upload a PDF and click "Pay $5 for Premium"**

4. **Use Stripe test card**:
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/30`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)

5. **Complete payment** and verify compression works

---

## Troubleshooting

### "Authentication required" error after login:
✅ **FIXED!** Added `session.permanent = True`
- Sessions now persist for 24 hours
- Try: Visit `/dev-login` again

### Can't access `/file-compressor`:
- Make sure you're logged in: `/dev-login`
- Check browser console for errors
- Verify session cookie exists (F12 → Application → Cookies)

### Payment doesn't work:
- Check `.env` has `STRIPE_PRICE_ID_FILE_COMPRESSOR`
- Use test card: `4242 4242 4242 4242`
- Check browser console for Stripe errors

### Compression fails:
- Check PDF is valid (opens in Adobe Reader)
- Check it's not password-protected
- Check file size (2MB for free, 50MB for premium)
- Check server logs for errors

---

## Quick Test Checklist

- [ ] Visit `http://localhost:5000/dev-login`
- [ ] Verify you're logged in (see user name in nav)
- [ ] See "Unlimited Premium Compression" badge
- [ ] Upload a PDF file
- [ ] Click "Use Free Compression" (uses premium automatically)
- [ ] Wait for compression
- [ ] Download compressed file
- [ ] Verify file size is smaller
- [ ] Check recent compressions list shows the job
- [ ] Try deleting a compression job
- [ ] Visit `/pricing` and verify file compressor is listed in features

---

## Ready to Test!

Restart your app (if it's running):
```bash
# Stop the current server (Ctrl+C)

# Start it again
python app.py
```

Then visit:
👉 **http://localhost:5000/dev-login**

Have fun! 🚀
