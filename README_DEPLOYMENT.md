# ExamShield License Server - Deployment Ready! 🚀

This repository contains the ExamShield License Server, ready for production deployment.

## 📋 Quick Start

1. **Read the Deployment Guide:** `PRODUCTION_DEPLOYMENT_GUIDE.md`
2. **Follow the Checklist:** `DEPLOYMENT_CHECKLIST.md`
3. **Deploy to Render:** See `QUICK_DEPLOY_RENDER.md`

## 🎯 Production URLs

- **License Server:** `https://examshield-license-erver.onrender.com`
- **Shop:** `https://adulsportfolio.vercel.app/shop`
- **Registration:** `https://https://examshield-license-server.onrender.com/register-page`
- **Payment:** `https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX`
- **Admin:** `https://https://examshield-license-server.onrender.com/admin`

## 📁 Important Files

### Configuration
- `server/config.env` - Environment variables template
- `render.yaml` - Render deployment configuration
- `vercel.json` - Vercel proxy configuration

### Documentation
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Deployment checklist
- `SHOP_INTEGRATION.md` - Shop integration guide
- `QUICK_DEPLOY_RENDER.md` - Quick Render deployment guide

### Server Files
- `server/license_server.py` - Main Flask server
- `server/requirements.txt` - Python dependencies
- `server/register.html` - Registration page
- `server/payment.html` - Payment page
- `server/success.html` - Success page

## 🔧 Environment Variables

Required environment variables (set in Render Dashboard):

```env
# SMTP (Email Delivery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Security
WEBHOOK_SECRET=your-strong-webhook-secret
ADMIN_SECRET=your-strong-admin-secret

# Data Directory
ES_DATA_DIR=/opt/render/project/src/server/data

# Flask Server
FLASK_HOST=0.0.0.0
FLASK_PORT=10000

# Payment Provider (Razorpay)
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Optional
PUBLIC_REPORTS_ENABLED=false
```

## 🚀 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy to Render
1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Set Root Directory: `server`
5. Set environment variables
6. Deploy

### 3. Configure Razorpay Webhook
1. Razorpay Dashboard → Settings → Webhooks
2. Add URL: `https://examshield-license-erver.onrender.com/webhook/payment`
3. Select event: `payment.captured`
4. Copy webhook secret to Render

### 4. Deploy to Vercel
1. Push `vercel.json` to GitHub
2. Import repository in Vercel
3. Deploy

### 5. Update Shop Page
1. Add "Buy Now" buttons to shop
2. Link to: `https://https://examshield-license-server.onrender.com/register-page?type=individual`
3. Test complete flow

## ✅ Pre-Deployment Checklist

- [ ] All code committed to Git
- [ ] Environment variables documented
- [ ] Gmail App Password obtained
- [ ] Razorpay API keys obtained
- [ ] Strong secrets generated
- [ ] Render account created
- [ ] Vercel account created
- [ ] Shop page ready

## 📚 Documentation

- **Complete Setup:** `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **Deployment Checklist:** `DEPLOYMENT_CHECKLIST.md`
- **Shop Integration:** `SHOP_INTEGRATION.md`
- **Quick Deploy:** `QUICK_DEPLOY_RENDER.md`
- **Getting Secrets:** `HOW_TO_GET_SECRETS.md`

## 🔐 Security

- ✅ All secrets in environment variables
- ✅ No hardcoded credentials
- ✅ Webhook signature verification
- ✅ Admin dashboard protected
- ✅ `.env` in `.gitignore`

## 🧪 Testing

### Health Check
```bash
curl https://examshield-license-erver.onrender.com/health
```

### Registration Test
```bash
curl -X POST https://examshield-license-erver.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User", "device_type": "individual"}'
```

## 📞 Support

For issues or questions:
1. Check `DEPLOYMENT_CHECKLIST.md`
2. Review Render logs
3. Check Razorpay dashboard
4. Verify environment variables

## 🎉 Ready for Production!

Your ExamShield License Server is ready for deployment. Follow the deployment guide to get started!

---

**Last Updated:** 2024
**Version:** 2.4
**Status:** Production Ready ✅

