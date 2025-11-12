# Quick Deploy to Render - Step by Step

## ✅ GitHub Push Complete!

Your code is now at: **https://github.com/Adulsatl/examshieldlic.git**

## Deploy to Render (5 minutes)

### Step 1: Sign Up / Sign In
1. Go to https://render.com
2. Click **Get Started for Free**
3. Sign up with GitHub (recommended) - it will auto-connect your repo

### Step 2: Create Web Service
1. Click **New +** button (top right)
2. Select **Web Service**
3. Find and select your repository: **Adulsatl/examshieldlic**
4. Click **Connect**

### Step 3: Configure Service

**Basic Settings:**
- **Name:** `examshield-license-server`
- **Region:** Choose closest to you (Oregon, Frankfurt, etc.)
- **Branch:** `main`
- **Root Directory:** `server` ⚠️ **IMPORTANT!**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python license_server.py`

### Step 4: Add Environment Variables

Click **Environment Variables** section and add these:

```env
# SMTP Gmail (replace with your values)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Security Secrets (generate new ones or use existing)
WEBHOOK_SECRET=your-webhook-secret-here
ADMIN_SECRET=your-admin-secret-here

# Data Directory
ES_DATA_DIR=/opt/render/project/src/server/data

# Flask Server (Render sets PORT automatically)
FLASK_HOST=0.0.0.0
FLASK_PORT=10000

# Razorpay (optional - add when ready)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Public Reports
PUBLIC_REPORTS_ENABLED=false
```

**How to get these values:**
- See `HOW_TO_GET_SECRETS.md` for SMTP and secrets
- Generate secrets: `python generate_secrets.py`
- Get Razorpay keys from Razorpay dashboard

### Step 5: Deploy

1. Scroll down and click **Create Web Service**
2. Wait for deployment (2-5 minutes)
3. Render will show build logs in real-time

### Step 6: Get Your URL

After deployment, Render gives you:
- **URL:** `https://examshield-license-server.onrender.com`

**Your API endpoints:**
- Registration: `https://examshield-license-erver.onrender.com/register-page`
- Payment: `https://examshield-license-erver.onrender.com/payment?key=...`
- Verify: `https://examshield-license-erver.onrender.com/verify` ⭐ **Use this for ES_VERIFY_URL**
- Admin: `https://examshield-license-erver.onrender.com/admin`

**Note:** Replace `examshield-license-erver` with your actual Render service name.

### Step 7: Test Deployment

```bash
# Test health endpoint (replace with your Render URL)
curl https://examshield-license-erver.onrender.com/health

# Should return: {"status": "ok", "service": "ExamShield License Server"}
```

### Step 8: Update Client Build

Before building `.deb` package for customers:

**Windows PowerShell:**
```powershell
$env:ES_VERIFY_URL="https://examshield-license-erver.onrender.com/verify"
```

**Linux/Mac:**
```bash
export ES_VERIFY_URL="https://examshield-license-erver.onrender.com/verify"
```

**Note:** Replace `examshield-license-erver` with your actual Render service name.

Then build:
```bash
./build_examshield_full.sh
```

## Important Notes

### Free Tier Limitations
- ⚠️ Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- For production, consider paid plan ($7/month)

### Keep Server Awake (Free Tier)
- Use https://cron-job.org or similar
- Ping `https://examshield-license-erver.onrender.com/health` every 10 minutes
- Replace URL with your actual Render service URL

### Data Persistence
- Free tier: Data is ephemeral (lost on restart)
- **Solution:** Use Render persistent disk OR upgrade to paid plan
- To add disk: **Infrastructure** → **Disks** → Create new disk

### Razorpay Webhook
After deployment:
1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://examshield-license-erver.onrender.com/webhook/payment`
3. Select event: `payment.captured`
4. Copy webhook secret → Update `WEBHOOK_SECRET` in Render
5. Replace URL with your actual Render service URL

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Check Python version (should be 3.x)

### Server Won't Start
- Check logs in Render dashboard
- Verify `PORT` environment variable (Render sets it automatically)
- Check all environment variables are set correctly

### Email Not Sending
- Verify SMTP credentials
- Check Gmail App Password is correct
- Check Render logs for SMTP errors

### 502 Bad Gateway
- Service might be sleeping (free tier)
- Wait 30-60 seconds and try again
- Check Render logs for errors

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test endpoints
3. ✅ Update client build with Render URL
4. ✅ Configure Razorpay webhook
5. ✅ Update Vercel proxy (if using)
6. ✅ Link from portfolio: https://adulsportfolio.vercel.app

---

**Your license server will be live at:** `https://examshield-license-erver.onrender.com` 🚀
**Note:** Replace `examshield-license-erver` with your actual Render service name.

**Deploy now:** https://render.com

