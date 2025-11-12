# Complete Setup Guide - ExamShield Licensing System

## 🎉 All Features Implemented!

### ✅ Completed Features

1. **Registration System**
   - Individual name / Organization name fields
   - Email validation
   - Duplicate prevention
   - Auto-redirect to payment

2. **Payment Integration**
   - Razorpay payment gateway
   - Stripe integration (placeholder)
   - Test payment option
   - Payment verification

3. **License Email (After Payment)**
   - Sent only after payment confirmation
   - Includes: Name, License Key, Activation Date, Expiry Date
   - Transaction details
   - Download link to portfolio

4. **Admin Dashboard**
   - Purchase reports
   - Statistics (Total, Active, Pending, Revenue)
   - Search functionality
   - CSV export
   - Public/private report toggle

5. **Success Page**
   - Shows license key
   - Download instructions
   - Links to portfolio

## 📁 File Structure

```
server/
├── license_server.py      # Main Flask server
├── register.html          # Registration page
├── payment.html           # Payment page
├── success.html           # Success page
├── admin_dashboard.html   # Admin dashboard
├── config.env             # Configuration template
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `server/.env`:

```env
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Webhook Security
WEBHOOK_SECRET=your-strong-secret-here

# Admin Secret
ADMIN_SECRET=your-admin-secret-here

# Razorpay (for payment)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Public Reports (optional)
PUBLIC_REPORTS_ENABLED=false

# Data Directory
ES_DATA_DIR=./data

# Flask Server
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
```

### 3. Start Server

```bash
python license_server.py
```

### 4. Access Pages

- **Registration**: http://localhost:8080/register-page
- **Payment**: http://localhost:8080/payment?key=ES-XXXXX
- **Success**: http://localhost:8080/success?key=ES-XXXXX
- **Admin**: http://localhost:8080/admin

## 🔄 Complete User Flow

### Step 1: Registration
1. User visits `/register-page`
2. Selects Individual or Organization
3. Enters Name/Organization Name
4. Enters Email
5. Submits → Redirects to payment

### Step 2: Payment
1. User sees license details
2. Chooses payment method:
   - Razorpay (real payment)
   - Stripe (coming soon)
   - Test Payment (simulation)
3. Completes payment
4. Redirects to success page

### Step 3: License Activation
1. Payment webhook triggers
2. License activated in database
3. Email sent with full details
4. User receives license key

### Step 4: Installation
1. User downloads from portfolio
2. Enters license key during install
3. License verified online
4. System activated

## 📧 Email Template

After payment, users receive:

```
Subject: Your ExamShield License is Activated - ES-XXXXX

Dear [Name/Organization],

LICENSE DETAILS:
- License Key: ES-XXXXX
- License Type: Individual/Organization
- Activation Date: January 1, 2025
- Expiry Date: January 1, 2026
- Transaction ID: xxxxx
- Payment Amount: $99.99

NEXT STEPS:
1. Download from: https://adulsportfolio.vercel.app
2. Enter License Key during installation
3. License auto-verified
```

## 🔐 Admin Dashboard Features

### Statistics
- Total Licenses
- Active Licenses
- Pending Payments
- Total Revenue

### Actions
- Search by email/name/key
- Export to CSV
- Revoke licenses
- Toggle public reports

### Access
- URL: `/admin`
- Authentication: Admin secret required

## 🔗 Portfolio Integration

### Add to Your Portfolio

```html
<!-- Purchase Count Widget -->
<div id="purchase-count">
  <script>
    fetch('https://your-server.com/public/reports')
      .then(res => res.json())
      .then(data => {
        document.getElementById('purchase-count').innerHTML = 
          data.active_licenses + ' licenses sold';
      });
  </script>
</div>

<!-- Buy Button -->
<a href="https://your-server.com/register-page" class="buy-btn">
  Buy ExamShield License
</a>
```

## 🧪 Testing

### Test Registration
```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "device_type": "individual"
  }'
```

### Test Payment (Simulate)
```bash
python activate_license.py test@example.com
```

### Test Admin Reports
```bash
curl "http://localhost:8080/admin/reports?secret=YOUR_SECRET"
```

## 📊 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register new license |
| `/register-page` | GET | Registration form |
| `/payment` | GET | Payment page |
| `/success` | GET | Success page |
| `/admin` | GET | Admin dashboard |
| `/license-info` | GET | Get license details |
| `/verify` | POST | Verify license key |
| `/webhook/payment` | POST | Payment webhook |
| `/create-razorpay-order` | POST | Create Razorpay order |
| `/verify-payment` | POST | Verify payment |
| `/admin/reports` | GET | Get purchase reports |
| `/public/reports` | GET | Public purchase count |
| `/admin/revoke` | GET | Revoke license |
| `/admin/extend` | GET | Extend license |

## 🎯 Production Deployment

### 1. Set Strong Secrets
```env
WEBHOOK_SECRET=$(openssl rand -hex 32)
ADMIN_SECRET=$(openssl rand -hex 32)
```

### 2. Enable HTTPS
- Use Nginx reverse proxy
- Get SSL certificate (Let's Encrypt)
- Update URLs in emails

### 3. Configure Razorpay
- Get production API keys
- Set webhook URL in Razorpay dashboard
- Test payment flow

### 4. Update Portfolio Links
- Change localhost URLs to production
- Update email templates
- Test all links

## 📝 Notes

- **Email**: Only sent after payment confirmation
- **Duplicate Prevention**: Same email can't register twice
- **Trial**: Free trial blocked if email already registered
- **Reports**: Admin can toggle public/private viewing
- **Export**: CSV export includes all purchase data

## 🆘 Troubleshooting

### Payment Not Working
- Check Razorpay API keys in `.env`
- Verify webhook URL in Razorpay dashboard
- Check server logs

### Email Not Sending
- Verify SMTP credentials
- Check firewall (port 587)
- Test SMTP connection

### Admin Dashboard Access Denied
- Check `ADMIN_SECRET` in `.env`
- Ensure secret matches when accessing

## ✅ All Done!

Your complete licensing system is ready:
- ✅ Registration with name/email
- ✅ Payment integration
- ✅ Email after payment
- ✅ Admin dashboard
- ✅ Purchase reports
- ✅ Public/private reports
- ✅ Success page
- ✅ Portfolio integration ready

Just add your Razorpay keys and deploy! 🚀

