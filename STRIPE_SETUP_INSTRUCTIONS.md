# Stripe Setup for File Compressor

## Create the Premium Compression Product

1. **Go to Stripe Dashboard**: https://dashboard.stripe.com/products

2. **Create New Product**:
   - Click "+ Add product"
   - Product name: "Premium File Compression"
   - Description: "Compress PDF files with 70-85% size reduction for immigration applications"
   - One-time payment (NOT subscription)

3. **Set Pricing**:
   - Price: $5.00 USD
   - Billing period: One time
   - Click "Save product"

4. **Copy the Price ID**:
   - After saving, you'll see a price ID like `price_xxxxxxxxxxxxx`
   - Copy this ID

5. **Add to .env file**:
   ```bash
   STRIPE_PRICE_ID_FILE_COMPRESSOR=price_xxxxxxxxxxxxx
   ```

6. **Restart your application** for the changes to take effect

## Testing the Payment Flow

Once configured, test:
1. Upload a PDF file
2. Select "Premium Compression"
3. Complete the $5 payment
4. Verify compression completes
5. Download the compressed file
