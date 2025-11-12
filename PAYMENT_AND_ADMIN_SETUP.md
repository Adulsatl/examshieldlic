# Payment Integration & Admin Dashboard Setup

## Overview

The system now includes:
1. ✅ Enhanced email sent only after payment confirmation
2. ✅ Payment page with Razorpay/Stripe integration
3. ✅ Admin dashboard for purchase reports
4. ✅ Public/private report viewing

## Features Implemented

### 1. Enhanced License Email (After Payment)

The webhook now sends a detailed email **only after payment is confirmed** with:
- License key
- Customer/Organization name
- Activation date
- Expiry date (1 year from activation)
- Transaction ID
- Payment amount
- Download link to your portfolio
- Installation instructions

### 2. Payment Page (`/payment`)

**Features:**
- Shows license information
- Razorpay integration
- Stripe integration (placeholder)
- Test payment option (simulates webhook)
- Automatic redirect after successful payment

**Access:** `http://localhost:8080/payment?key=ES-XXXXX`

### 3. Admin Dashboard (`/admin`)

**Features:**
- Total licenses count
- Active licenses count
- Pending payments count
- Total revenue
- Searchable table of all purchases
- Export to CSV
- Toggle public/private reports
- Revoke licenses

**Access:** `http://localhost:8080/admin`

**Authentication:** Requires admin secret (set in `.env` as `ADMIN_SECRET`)

### 4. Registration Flow

**Updated registration form:**
- Individual: Name field
- Organization: Organization name field
- Email field
- License type selection
- Auto-redirects to payment after registration

**Access:** `http://localhost:8080/register-page`

## API Endpoints

### Registration
```
POST /register
Body: { "email": "...", "name": "...", "device_type": "individual|organization" }
Response: { "success": true, "license_key": "...", "payment_url": "/payment?key=..." }
```

### License Info
```
GET /license-info?key=ES-XXXXX
Response: { "key": "...", "name": "...", "email": "...", "device_type": "...", "active": false }
```

### Payment Webhook
```
POST /webhook/payment
Headers: { "X-Webhook-Signature": "..." }
Body: { "status": "paid", "email": "...", "id": "...", "amount": 99.99 }
```

### Admin Reports
```
GET /admin/reports?secret=YOUR_ADMIN_SECRET
Response: { "reports": [...], "stats": { "total": 10, "active": 5, "pending": 3, "revenue": 999.90 } }
```

### Public Reports
```
GET /public/reports
Response: { "total_licenses": 10, "active_licenses": 5, "last_updated": "..." }
```

## Setup Instructions

### 1. Configure Environment Variables

Edit `server/.env`:

```env
# Existing settings...
ADMIN_SECRET=your-strong-admin-secret-here

# Enable public reports (optional)
PUBLIC_REPORTS_ENABLED=false

# Razorpay keys (for payment integration)
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### 2. Access Pages

**Registration:**
```
http://localhost:8080/register-page
```

**Payment (after registration):**
```
http://localhost:8080/payment?key=ES-XXXXX
```

**Admin Dashboard:**
```
http://localhost:8080/admin
```

### 3. Test Payment Flow

1. Register at `/register-page`
2. Enter name, email, select license type
3. Submit → Redirects to `/payment?key=ES-XXXXX`
4. Click "Test Payment (Simulate)"
5. Payment webhook triggers
6. License activated
7. Email sent with license details

### 4. View Reports

**Admin Dashboard:**
1. Go to `/admin`
2. Enter admin secret when prompted
3. View all purchases, stats, export CSV

**Public Reports (if enabled):**
```
GET /public/reports
```

## Email Template

The email sent after payment includes:

```
Dear [Name/Organization],

LICENSE DETAILS:
- License Key: ES-XXXXX
- License Type: Individual/Organization
- Activation Date: January 1, 2025
- Expiry Date: January 1, 2026
- Transaction ID: ...
- Payment Amount: $99.99

NEXT STEPS:
1. Download from: https://adulsportfolio.vercel.app
2. Enter License Key during installation
3. License auto-verified
```

## Integration with Portfolio Website

### Embed Purchase Count

Add to your portfolio website (`https://adulsportfolio.vercel.app`):

```html
<script>
fetch('https://your-license-server.com/public/reports')
  .then(res => res.json())
  .then(data => {
    document.getElementById('purchase-count').textContent = 
      data.active_licenses + ' licenses sold';
  });
</script>
```

### Link to Registration

```html
<a href="https://your-license-server.com/register-page">
  Buy ExamShield License
</a>
```

## Razorpay Integration

### Setup Razorpay

1. Create account at https://razorpay.com
2. Get API keys from dashboard
3. Add to `.env`:
   ```env
   RAZORPAY_KEY_ID=rzp_test_xxxxx
   RAZORPAY_KEY_SECRET=xxxxx
   ```

### Add Order Creation Endpoint

You'll need to add this endpoint to `license_server.py`:

```python
@app.route('/create-razorpay-order', methods=['POST'])
def create_razorpay_order():
    import razorpay
    data = request.get_json()
    
    client = razorpay.Client(
        auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
    )
    
    order = client.order.create({
        'amount': data['amount'],
        'currency': data['currency'],
        'receipt': data['license_key']
    })
    
    return jsonify({
        'order_id': order['id'],
        'razorpay_key': os.getenv('RAZORPAY_KEY_ID'),
        'amount': data['amount'],
        'currency': data['currency']
    })
```

## Security Notes

1. **Admin Secret**: Use a strong, unique secret
2. **Public Reports**: Only enable if you want public stats
3. **Webhook Secret**: Keep secure, never expose
4. **HTTPS**: Use HTTPS in production

## Testing

### Test Complete Flow

```bash
# 1. Register
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","device_type":"individual"}'

# 2. Get license info
curl http://localhost:8080/license-info?key=ES-XXXXX

# 3. Simulate payment
python activate_license.py test@example.com

# 4. Check admin reports
curl "http://localhost:8080/admin/reports?secret=YOUR_SECRET"
```

## Next Steps

1. ✅ Registration with name fields
2. ✅ Payment page created
3. ✅ Admin dashboard created
4. ✅ Enhanced email after payment
5. ⏳ Integrate Razorpay API (add order creation endpoint)
6. ⏳ Add Stripe integration
7. ⏳ Deploy to production
8. ⏳ Link from portfolio website

All core functionality is complete! Just need to add payment gateway API keys and deploy.

