# PDF File Compressor Feature - Complete Documentation

## Overview
A new PDF file compression feature has been added to your immigration SaaS platform, allowing users to compress PDF files for immigration applications that have strict file size limits (DS-260, DS-160, I-485, etc.).

---

## Feature Highlights

### Free Tier
- **5 compressions per month**
- **2MB max file size**
- **50-60% compression ratio** (file reduces to about 50-60% of original size)
- Available to all users (no subscription required)

### Premium Tier ($5 one-time payment)
- **Unlimited compressions** for that file
- **50MB max file size**
- **70-85% compression ratio** (file reduces to 25% of original size)
- One-time $5 payment per file

### Subscription Benefits
Users with **Professional, Team, or Business** subscriptions get:
- **Unlimited premium compression** at no extra charge
- All premium features included in subscription

---

## Files Created/Modified

### New Files
1. **`file_compressor_routes.py`** - All API endpoints and routes
2. **`pdf_compressor.py`** - PDF compression utility with free/premium logic
3. **`templates/file_compressor.html`** - User interface for file upload and compression
4. **`STRIPE_SETUP_INSTRUCTIONS.md`** - Instructions for Stripe setup

### Modified Files
1. **`document_models.py`** - Added `FileCompressionJob` model (line 185)
2. **`config.py`** - Added file compressor configuration (lines 41, 146-175)
3. **`app.py`** - Registered file compressor routes (lines 71-73)
4. **`init_db.py`** - Import FileCompressionJob model (line 3)
5. **`requirements.txt`** - Added dependencies (lines 15-16)
6. **Navigation menus** - Added "File Compressor" link to:
   - `templates/index.html` (line 740)
   - `templates/home.html` (line 438)
   - `templates/dashboard.html` (line 133)
   - `templates/templates_browse.html` (line 206)

---

## Database Schema

### FileCompressionJob Table
```sql
CREATE TABLE file_compression_jobs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    compression_tier VARCHAR(20) DEFAULT 'free',
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    stripe_payment_intent_id VARCHAR(255),
    original_filename VARCHAR(500) NOT NULL,
    original_file_size INTEGER,
    compressed_file_size INTEGER,
    compression_ratio FLOAT,
    original_file_path VARCHAR(500),
    compressed_file_path VARCHAR(500),
    target_quality VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API Endpoints

### 1. File Compressor Page
```
GET /file-compressor
```
- Returns the file compressor UI
- Shows usage limits for free users
- Accessible to all (login required to use)

### 2. Get Usage Info
```
GET /api/file-compressor/usage
```
- Returns user's compression usage (remaining compressions, tier, limits)
- Requires authentication

### 3. Get Compression Jobs
```
GET /api/file-compressor/jobs
```
- Lists user's recent compression jobs (last 50)
- Shows status, file sizes, compression ratios
- Requires authentication

### 4. Upload and Queue File
```
POST /api/file-compressor/upload
Form Data:
  - file: PDF file
  - tier: 'free' or 'premium'
```
- Uploads PDF file
- Creates compression job record
- Returns job ID
- Checks file size and monthly limits

### 5. Compress File
```
POST /api/file-compressor/jobs/{job_id}/compress
```
- Triggers compression for uploaded file
- Uses PyPDF2 or Ghostscript (if available)
- Returns compressed file info
- Updates job status

### 6. Create Premium Payment
```
POST /api/file-compressor/jobs/{job_id}/checkout
```
- Creates Stripe Payment Intent for $5
- Returns client secret for Stripe Elements
- Requires unpaid job

### 7. Confirm Payment
```
POST /api/file-compressor/jobs/{job_id}/confirm-payment
Body: { "payment_intent_id": "pi_xxx" }
```
- Verifies payment with Stripe
- Upgrades compression job to premium tier
- Marks payment as complete

### 8. Download Compressed File
```
GET /api/file-compressor/jobs/{job_id}/download
```
- Downloads compressed PDF file
- Requires completed compression job
- Returns PDF file

### 9. Delete Compression Job
```
DELETE /api/file-compressor/jobs/{job_id}
```
- Deletes compression job and files
- Removes original and compressed files from disk

---

## Configuration

### Environment Variables Required
Add to `.env`:
```bash
# Stripe Price ID for $5 premium compression
STRIPE_PRICE_ID_FILE_COMPRESSOR=price_xxxxxxxxxxxxx
```

### Config Settings (config.py)
```python
DOCUMENT_TYPES = {
    'file_compressor_premium': {
        'name': 'Premium File Compression',
        'description': 'Compress PDF files to 70-85% of original size',
        'price': 5.00,
        'price_id': os.getenv('STRIPE_PRICE_ID_FILE_COMPRESSOR'),
        'required_tier': 'free'  # Available to all
    }
}

FILE_COMPRESSOR_LIMITS = {
    'free': {
        'monthly_limit': 5,
        'max_file_size_mb': 2,
        'compression_quality': 'basic',
        'target_compression_ratio': 0.55  # 45% reduction
    },
    'basic': {  # Professional+ subscriptions
        'monthly_limit': None,  # Unlimited
        'max_file_size_mb': 50,
        'compression_quality': 'premium',
        'target_compression_ratio': 0.25  # 75% reduction
    },
    'premium_onetime': {  # $5 payment
        'monthly_limit': None,
        'max_file_size_mb': 50,
        'compression_quality': 'premium',
        'target_compression_ratio': 0.25  # 75% reduction
    }
}
```

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
python init_db.py
```
This creates the `file_compression_jobs` table.

### 3. Set Up Stripe Product
Follow instructions in `STRIPE_SETUP_INSTRUCTIONS.md`:
1. Go to Stripe Dashboard → Products
2. Create new product: "Premium File Compression"
3. Set price: $5.00 (one-time payment)
4. Copy the Price ID (starts with `price_`)
5. Add to `.env`: `STRIPE_PRICE_ID_FILE_COMPRESSOR=price_xxxxx`

### 4. Create Upload Directory
```bash
mkdir -p static/uploads/compressed-files
```

### 5. Restart Application
```bash
# If using gunicorn
gunicorn app:app

# If running locally
python app.py
```

---

## User Flow

### Free Compression Flow
1. User navigates to `/file-compressor`
2. Sees "5 of 5 compressions remaining this month"
3. Uploads PDF file (up to 2MB)
4. Clicks "Use Free Compression"
5. File compresses automatically
6. Downloads compressed file (50-60% of original size)

### Premium Compression Flow ($5 Payment)
1. User navigates to `/file-compressor`
2. Uploads PDF file (up to 50MB)
3. Clicks "Pay $5 for Premium"
4. Payment modal opens with Stripe Elements
5. Enters payment info and pays $5
6. File compresses with premium quality
7. Downloads compressed file (70-85% reduction)

### Subscription Users (Professional+)
1. User navigates to `/file-compressor`
2. Sees "Unlimited Premium Compression Available"
3. Uploads PDF file (up to 50MB)
4. File automatically uses premium compression (no charge)
5. Downloads compressed file

---

## Testing Checklist

### Manual Testing
- [ ] Navigate to `/file-compressor` page
- [ ] Upload PDF file as free user
- [ ] Check monthly limit counter
- [ ] Test free compression (file < 2MB)
- [ ] Verify compressed file downloads
- [ ] Test file size limit enforcement (try file > 2MB)
- [ ] Test monthly limit (do 6 compressions to hit limit)
- [ ] Test premium payment flow with Stripe test cards
- [ ] Test premium compression (better quality)
- [ ] Test as Professional+ subscriber (should be free premium)
- [ ] Test recent compressions list
- [ ] Test delete compression job
- [ ] Verify files are deleted from disk

### Test Data
**Stripe Test Cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Any future expiry, any CVC

---

## File Storage

Compressed files are stored at:
```
static/uploads/compressed-files/
  ├── {user_id}_{timestamp}_{original_filename}.pdf  (original)
  └── compressed_{job_id}_{original_filename}.pdf    (compressed)
```

**Note:** Consider implementing file cleanup for old files (e.g., delete after 7 days).

---

## Compression Technical Details

### Basic Compression (Free Tier)
- Uses PyPDF2 library
- Compresses content streams
- Target: 55% of original size
- JPEG quality: 75
- Best for: Documents under 5MB

### Premium Compression
- Tries Ghostscript first (if installed), falls back to PyPDF2
- More aggressive image downsampling
- Target: 25% of original size (75% reduction)
- JPEG quality: 60
- Image resolution: 72 DPI
- Best for: Large scanned documents, image-heavy PDFs

### Ghostscript Installation (Optional, for better compression)
```bash
# Ubuntu/Debian
sudo apt-get install ghostscript

# macOS
brew install ghostscript

# The app will automatically use it if available
```

---

## Pricing Page Integration

The pricing page automatically shows file compressor features because they're in `config.py`:

**Solo (Free):**
- File compressor (5 files/month, up to 2MB)

**Professional ($39/mo):**
- File compressor (unlimited, premium quality)

**Team ($149/mo):**
- File compressor (unlimited, premium quality)

**Business ($299/mo):**
- File compressor (unlimited, premium quality)

---

## Security Considerations

1. **File Upload Validation**
   - Only accepts `.pdf` files
   - File size limits enforced
   - Secure filename sanitization using `werkzeug.utils.secure_filename`

2. **Authentication**
   - All endpoints require login (`@login_required`)
   - Users can only access their own compression jobs

3. **Rate Limiting**
   - Upload: 10 requests/minute
   - Download: 30 requests/minute
   - List jobs: 20 requests/minute

4. **Payment Security**
   - Uses Stripe Payment Intents API
   - Payment verification before compression
   - No credit card data stored locally

---

## Monitoring & Analytics

Track these metrics:
- Total compressions (free vs premium)
- Revenue from premium compressions
- Average file size reduction
- Most common file sizes
- Conversion rate (free → premium)

Query examples:
```python
# Total compressions this month
FileCompressionJob.query.filter(
    FileCompressionJob.created_at >= month_start
).count()

# Premium compression revenue this month
FileCompressionJob.query.filter(
    FileCompressionJob.payment_status == 'paid',
    FileCompressionJob.created_at >= month_start
).count() * 5  # $5 per compression

# Average compression ratio
db.session.query(
    func.avg(FileCompressionJob.compression_ratio)
).scalar()
```

---

## Troubleshooting

### Issue: "File too large" error
**Solution:** 
- Free users: File must be under 2MB
- Premium: File must be under 50MB
- Check actual file size before upload

### Issue: "Monthly limit reached"
**Solution:**
- Wait until next month (resets on 1st)
- Upgrade to Professional subscription
- Pay $5 for premium compression

### Issue: Compression fails
**Possible causes:**
- Corrupted PDF file
- Password-protected PDF
- Invalid PDF format
- Insufficient disk space

**Solution:**
- Verify PDF opens in Adobe Reader
- Remove password protection
- Check server disk space
- Check application logs

### Issue: Payment succeeds but compression doesn't start
**Solution:**
- Check Stripe webhook is configured
- Manually call compress endpoint
- Check payment_status in database
- Verify Stripe customer ID matches user

---

## Future Enhancements

Consider adding:
1. **Batch Compression** - Upload multiple files at once
2. **Auto-Cleanup** - Delete files older than 7 days
3. **Email Notifications** - Send email when compression completes
4. **Compression Presets** - Let users choose target file size
5. **Image Extraction** - Extract images from PDFs separately
6. **Watermark Removal** - Premium tier removes any watermarks
7. **API Access** - Allow programmatic compression via API key
8. **Analytics Dashboard** - Show compression stats to users

---

## Support Resources

- **User Guide:** `/file-compressor` page has built-in help text
- **API Documentation:** See API Endpoints section above
- **Stripe Dashboard:** https://dashboard.stripe.com
- **PyPDF2 Docs:** https://pypdf2.readthedocs.io

---

## Success! 🎉

The file compressor feature is now fully integrated into your immigration SaaS. Users can:
- Compress PDFs for free (5/month)
- Pay $5 for premium compression
- Get unlimited premium compression with Professional+ subscriptions

This feature addresses a real pain point for immigration applicants dealing with strict file size limits!
