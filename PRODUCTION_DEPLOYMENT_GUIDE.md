# ExamShield License Server - Production Deployment Guide

Complete guide for deploying ExamShield License Server to production on Render.

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ GitHub account
- ✅ Render account (free tier available)
- ✅ Gmail account (for email delivery)
- ✅ Razorpay account (for payments)
- ✅ Vercel account (for shop integration)
- ✅ Domain/portfolio site: `adulsportfolio.vercel.app`

## 🚀 Quick Start (5 Minutes)

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: ExamShield License Server"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. **Go to Render Dashboard**
   - Visit: https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Select repository: `YOUR_USERNAME/YOUR_REPO`

3. **Configure Service**
   ```
   Name: examshield-license-server
   Region: Choose closest to you
   Branch: main
   Root Directory: server
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python license_server.py
   ```

4. **Set Environment Variables**
   - Click **Environment Variables** tab
   - Add all variables from the checklist below

5. **Create Persistent Disk (Recommended)**
   - Go to **Infrastructure** → **Disks**
   - Create new disk (1GB minimum)
   - Mount to: `/opt/render/project/src/server/data`

6. **Deploy**
   - Click **Create Web Service**
   - Wait for deployment (2-5 minutes)
   - Get your URL: `https://examshield-license-erver.onrender.com`

## 🔧 Environment Variables

Set these in Render Dashboard → Environment Variables:

### Required Variables

```env
# SMTP Configuration (Email Delivery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Security Secrets (Generate strong random strings)
WEBHOOK_SECRET=your-strong-webhook-secret-32-chars-min
ADMIN_SECRET=your-strong-admin-secret-32-chars-min

# Data Directory (Render Persistent Disk)
ES_DATA_DIR=/opt/render/project/src/server/data

# Flask Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=10000

# Payment Provider (Razorpay)
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Optional Settings
PUBLIC_REPORTS_ENABLED=false
```

### How to Get Values

#### 1. Gmail App Password
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate password for "Mail"
5. Use that password (not your regular password)

#### 2. Generate Secrets
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

#### 3. Razorpay API Keys
1. Go to Razorpay Dashboard
2. Settings → API Keys
3. Copy Key ID and Key Secret
4. Use test keys for testing: `rzp_test_xxxxx`
5. Use live keys for production: `rzp_live_xxxxx`

## 🔐 Razorpay Webhook Configuration

### Step 1: Configure Webhook in Razorpay

1. **Go to Razorpay Dashboard**
   - Settings → Webhooks
   - Click **Add New Webhook**

2. **Configure Webhook**
   - **URL:** `https://examshield-license-erver.onrender.com/webhook/payment`
   - **Events:** Select `payment.captured`
   - **Secret:** Copy the webhook secret

3. **Update Render Environment Variable**
   - Go to Render Dashboard
   - Update `WEBHOOK_SECRET` with the webhook secret from Razorpay

### Step 2: Test Webhook

1. Make a test payment
2. Check Render logs for webhook delivery
3. Verify license is activated
4. Check email is sent

## 🌐 Vercel Integration

### Step 1: Deploy vercel.json

1. **Push vercel.json to GitHub**
   ```bash
   git add vercel.json
   git commit -m "Add Vercel configuration"
   git push
   ```

2. **Deploy to Vercel**
   - Go to Vercel Dashboard
   - Import your GitHub repository
   - Vercel will auto-detect `vercel.json`
   - Deploy

### Step 2: Verify Proxy

Test all endpoints through Vercel:
- Registration: `https://https://examshield-license-server.onrender.com/register-page`
- Payment: `https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX`
- Verify: `https://adulsportfolio.vercel.app/verify`
- Admin: `https://https://examshield-license-server.onrender.com/admin`

## 🛍️ Shop Integration

### Step 1: Update Shop Page

Add "Buy Now" buttons to your shop page:

```html
<!-- Individual License -->
<a href="https://https://examshield-license-server.onrender.com/register-page?type=individual" 
   class="buy-button">
   Buy Individual License ($99.99)
</a>

<!-- Organization License -->
<a href="https://https://examshield-license-server.onrender.com/register-page?type=organization" 
   class="buy-button">
   Buy Organization License ($299.99)
</a>
```

### Step 2: Test Shop Flow

1. Visit shop page
2. Click "Buy Now"
3. Complete registration
4. Complete payment
5. Verify email received
6. Verify download link works

## 🧪 Testing

### 1. Health Check

```bash
curl https://examshield-license-erver.onrender.com/health
# Expected: {"status": "ok", "service": "ExamShield License Server"}
```

### 2. Registration Test

```bash
curl -X POST https://examshield-license-erver.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "device_type": "individual"
  }'
```

### 3. Payment Test

1. Register a license
2. Go to payment page: `https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX`
3. Click "Test Payment (Simulate)"
4. Verify license is activated
5. Verify email is sent

### 4. License Verification Test

```bash
curl -X POST https://examshield-license-erver.onrender.com/verify \
  -H "Content-Type: application/json" \
  -d '{
    "key": "ES-XXXXX",
    "device_fingerprint": "test_fingerprint"
  }'
```

## 📊 Admin Dashboard

### Access Admin Dashboard

1. **URL:** `https://https://examshield-license-server.onrender.com/admin`
2. **Enter Admin Secret:** (from `ADMIN_SECRET` environment variable)
3. **View Reports:** License statistics, revenue, etc.

### Admin Features

- View all licenses
- See revenue statistics
- Revoke licenses
- Extend license expiry
- Export reports to CSV

## 🔄 Client Build Configuration

### Update Client Build

Before building the client installer:

```bash
# Set verify URL
export ES_VERIFY_URL="https://examshield-license-erver.onrender.com/verify"

# Build installer
./build_examshield_full.sh
```

The installer will use this URL for license verification.

## 📧 Email Configuration

### Email Templates

All email templates include:
- License key
- Activation date
- Expiry date
- Download link: `https://adulsportfolio.vercel.app/shop`
- Installation instructions

### Testing Email Delivery

1. Register a test license
2. Complete payment
3. Check email inbox
4. Verify all links work
5. Verify license key is correct

## 🔍 Monitoring

### Render Logs

- View logs in Render Dashboard
- Check for errors
- Monitor email delivery
- Monitor webhook delivery

### Health Checks

Set up a cron job to ping the health endpoint:
- URL: `https://examshield-license-erver.onrender.com/health`
- Frequency: Every 10 minutes
- Service: https://cron-job.org

### Backup Strategy

1. **Render Persistent Disk**
   - License database stored on persistent disk
   - Automatic backups (Render handles this)

2. **Manual Backup**
   - Download `license_db.json` periodically
   - Store backups securely

## 🐛 Troubleshooting

### Service Not Starting

1. Check Render logs
2. Verify all environment variables are set
3. Verify `PORT` environment variable (Render sets this automatically)
4. Check Python version (should be 3.x)

### Email Not Sending

1. Verify SMTP credentials
2. Check Gmail App Password is correct
3. Verify 2-Step Verification is enabled
4. Check Render logs for SMTP errors

### Payment Not Activating License

1. Check Razorpay webhook configuration
2. Verify `WEBHOOK_SECRET` matches Razorpay
3. Check Render logs for webhook delivery
4. Verify webhook URL is correct

### License Verification Failing

1. Verify `ES_VERIFY_URL` is correct
2. Check license is activated
3. Verify device fingerprint
4. Check Render logs for verification errors

## ✅ Production Checklist

Use `DEPLOYMENT_CHECKLIST.md` for complete checklist.

### Quick Checklist

- [ ] All environment variables set
- [ ] Razorpay webhook configured
- [ ] Email delivery working
- [ ] Payment processing working
- [ ] License verification working
- [ ] Shop integration working
- [ ] Admin dashboard accessible
- [ ] All tests passing

## 🎉 Deployment Complete!

Your ExamShield License Server is now live and ready for production!

### Production URLs

- **License Server:** `https://examshield-license-erver.onrender.com`
- **Shop:** `https://adulsportfolio.vercel.app/shop`
- **Registration:** `https://https://examshield-license-server.onrender.com/register-page`
- **Admin:** `https://https://examshield-license-server.onrender.com/admin`

### Next Steps

1. ✅ Test complete customer journey
2. ✅ Monitor logs for errors
3. ✅ Set up backup strategy
4. ✅ Configure monitoring
5. ✅ Update documentation

---

**Need Help?** Check `DEPLOYMENT_CHECKLIST.md` for detailed checklist.

