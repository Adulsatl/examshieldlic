# ExamShield License Server - Deployment Checklist

Complete checklist for deploying ExamShield License Server to production.

## ✅ Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code changes committed to Git
- [ ] Code tested locally
- [ ] No hardcoded secrets in code
- [ ] All URLs updated to production values
- [ ] `.gitignore` configured correctly
- [ ] `requirements.txt` updated with pinned versions

### 2. Configuration Files
- [ ] `server/config.env` template updated
- [ ] `render.yaml` configured (if using Render)
- [ ] `vercel.json` updated with production URLs
- [ ] Environment variables documented

### 3. Security
- [ ] Strong `WEBHOOK_SECRET` generated (32+ characters)
- [ ] Strong `ADMIN_SECRET` generated (32+ characters)
- [ ] Gmail App Password obtained (not regular password)
- [ ] No secrets committed to Git
- [ ] `.env` file in `.gitignore`

### 4. Payment Provider
- [ ] Razorpay account created
- [ ] Razorpay API keys obtained
- [ ] Razorpay webhook URL configured
- [ ] Webhook secret from Razorpay saved
- [ ] Test payment verified (if using test keys)

### 5. Email Configuration
- [ ] Gmail 2-Step Verification enabled
- [ ] Gmail App Password generated
- [ ] SMTP credentials tested
- [ ] Email templates reviewed
- [ ] Shop URL in email templates: `https://adulsportfolio.vercel.app/shop`

## 🚀 Deployment Steps

### Step 1: GitHub Repository
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] Repository is public or has Render access
- [ ] Main branch is `main` or `master`

### Step 2: Render Deployment

#### Service Configuration
- [ ] Render account created
- [ ] GitHub repository connected
- [ ] New Web Service created
- [ ] Service name: `examshield-license-server`
- [ ] Root Directory: `server`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python license_server.py`
- [ ] Runtime: Python 3

#### Environment Variables (Set in Render Dashboard)
- [ ] `SMTP_HOST=smtp.gmail.com`
- [ ] `SMTP_PORT=587`
- [ ] `SMTP_USER=your-email@gmail.com`
- [ ] `SMTP_PASSWORD=your-gmail-app-password`
- [ ] `WEBHOOK_SECRET=your-strong-webhook-secret`
- [ ] `ADMIN_SECRET=your-strong-admin-secret`
- [ ] `ES_DATA_DIR=/opt/render/project/src/server/data`
- [ ] `FLASK_HOST=0.0.0.0`
- [ ] `FLASK_PORT=10000`
- [ ] `RAZORPAY_KEY_ID=rzp_live_xxxxx` (or test)
- [ ] `RAZORPAY_KEY_SECRET=xxxxx`
- [ ] `PUBLIC_REPORTS_ENABLED=false` (or true if needed)

#### Persistent Disk (Optional but Recommended)
- [ ] Persistent disk created in Render
- [ ] Disk mounted to: `/opt/render/project/src/server/data`
- [ ] Disk size: 1GB (minimum)

#### Deploy
- [ ] Service deployed successfully
- [ ] Build logs checked (no errors)
- [ ] Service is running
- [ ] URL obtained: `https://examshield-license-erver.onrender.com`

### Step 3: Testing Deployment

#### Health Check
- [ ] Health endpoint works: `https://examshield-license-erver.onrender.com/health`
- [ ] Returns: `{"status": "ok", "service": "ExamShield License Server"}`

#### Registration Test
- [ ] Registration page loads: `https://examshield-license-erver.onrender.com/register-page`
- [ ] Registration form works
- [ ] License key generated
- [ ] Redirects to payment page

#### Payment Test
- [ ] Payment page loads: `https://examshield-license-erver.onrender.com/payment?key=ES-XXXXX`
- [ ] License info displays correctly
- [ ] Price shows correctly (Individual: $99.99, Organization: $299.99)
- [ ] Test payment works
- [ ] License activated after payment

#### Email Test
- [ ] Test registration and payment
- [ ] Email received with license details
- [ ] Email contains correct shop URL: `https://adulsportfolio.vercel.app/shop`
- [ ] License key in email is correct

#### Admin Dashboard
- [ ] Admin dashboard loads: `https://examshield-license-erver.onrender.com/admin`
- [ ] Admin secret authentication works
- [ ] Reports show correct data
- [ ] License statistics correct

### Step 4: Payment Provider Configuration

#### Razorpay Webhook
- [ ] Razorpay Dashboard → Settings → Webhooks
- [ ] Webhook URL added: `https://examshield-license-erver.onrender.com/webhook/payment`
- [ ] Event selected: `payment.captured`
- [ ] Webhook secret copied
- [ ] Webhook secret updated in Render: `WEBHOOK_SECRET`
- [ ] Webhook tested (make test payment)
- [ ] License activated via webhook

### Step 5: Vercel Integration

#### Vercel Configuration
- [ ] `vercel.json` updated with Render URL
- [ ] Vercel project created
- [ ] Vercel deployment successful
- [ ] All endpoints proxied correctly:
  - `/register-page` → Render
  - `/payment` → Render
  - `/verify` → Render
  - `/webhook/payment` → Render
  - `/admin` → Render

#### Testing Vercel Proxy
- [ ] Registration via Vercel: `https://https://examshield-license-server.onrender.com/register-page`
- [ ] Payment via Vercel: `https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX`
- [ ] All endpoints work through Vercel

### Step 6: Shop Integration

#### Shop Page Updates
- [ ] Shop page created/updated: `https://adulsportfolio.vercel.app/shop`
- [ ] "Buy Now" buttons added:
  - Individual: `https://https://examshield-license-server.onrender.com/register-page?type=individual`
  - Organization: `https://https://examshield-license-server.onrender.com/register-page?type=organization`
- [ ] Download section added
- [ ] Pricing displayed correctly

#### Testing Shop Flow
- [ ] Customer clicks "Buy Now" from shop
- [ ] Registration page pre-fills license type
- [ ] Payment flow works
- [ ] Success page links back to shop
- [ ] Email contains shop download link

### Step 7: Client Build Configuration

#### Update Client Build
- [ ] `build_examshield_full.sh` updated with Render URL
- [ ] `ES_VERIFY_URL` set to: `https://examshield-license-erver.onrender.com/verify`
- [ ] Client build tested
- [ ] License verification works from client

## 📋 Post-Deployment Checklist

### Monitoring
- [ ] Render logs monitored (no errors)
- [ ] Email delivery working
- [ ] Payment processing working
- [ ] Webhook delivery working
- [ ] License verification working

### Documentation
- [ ] Deployment guide updated
- [ ] URLs documented
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Troubleshooting guide created

### Security
- [ ] All secrets are secure (not in code)
- [ ] Admin dashboard protected
- [ ] Webhook signature verification working
- [ ] HTTPS enabled (Render provides automatically)

### Backup
- [ ] Backup strategy in place
- [ ] License database backed up
- [ ] Render persistent disk configured
- [ ] Backup script tested (if using)

## 🔧 Troubleshooting

### Common Issues
- [ ] Service sleeping (free tier) - use cron job to ping
- [ ] Email not sending - check SMTP credentials
- [ ] Payment not activating - check webhook configuration
- [ ] License verification failing - check verify URL
- [ ] Data not persisting - check persistent disk

### Support Resources
- [ ] Render logs checked
- [ ] Razorpay dashboard checked
- [ ] Gmail account checked
- [ ] Vercel deployment logs checked

## ✅ Final Verification

### End-to-End Test
- [ ] Complete customer journey tested:
  1. Visit shop page
  2. Click "Buy Now"
  3. Register license
  4. Complete payment
  5. Receive email
  6. Download from shop
  7. Install ExamShield
  8. Verify license

### Production Readiness
- [ ] All tests passing
- [ ] No errors in logs
- [ ] All endpoints working
- [ ] Email delivery working
- [ ] Payment processing working
- [ ] License verification working
- [ ] Admin dashboard working
- [ ] Shop integration working

## 🎉 Deployment Complete!

Once all items are checked:
- ✅ System is ready for production
- ✅ Customers can purchase licenses
- ✅ Licenses are activated automatically
- ✅ Email delivery is working
- ✅ Shop integration is complete

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Production URL:** `https://examshield-license-erver.onrender.com`
**Shop URL:** `https://adulsportfolio.vercel.app/shop`

