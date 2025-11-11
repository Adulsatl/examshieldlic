# Deploy ExamShield License Server to Render

## Step 1: Push to GitHub

Your code is already committed! Now push to GitHub:

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub (recommended)

### 2. Create New Web Service
- Click **New +** → **Web Service**
- Connect your GitHub repository
- Select the repository you just pushed

### 3. Configure Service

**Basic Settings:**
- **Name:** `examshield-license-server` (or any name)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** `server` (if server/ is at root) OR `.` (if repo root has server/)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python license_server.py`

### 4. Set Environment Variables

Click **Environment** tab and add:

```env
# SMTP Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Security
WEBHOOK_SECRET=your-webhook-secret-here
ADMIN_SECRET=your-admin-secret-here

# Data Directory (Render persistent disk)
ES_DATA_DIR=/opt/render/project/src/server/data

# Flask Server (Render sets PORT automatically)
FLASK_HOST=0.0.0.0
FLASK_PORT=10000

# Razorpay (when ready)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Public Reports (optional)
PUBLIC_REPORTS_ENABLED=false
```

**Important Notes:**
- Render automatically sets `PORT` environment variable
- The server code reads `PORT` if available, otherwise uses `FLASK_PORT`
- `ES_DATA_DIR` should point to Render's persistent disk path

### 5. Create Persistent Disk (Optional but Recommended)

For data persistence:
- Go to **Infrastructure** → **Disks**
- Create new disk
- Mount to: `/opt/render/project/src/server/data`
- This ensures `license_db.json` persists across deployments

### 6. Deploy

- Click **Create Web Service**
- Render will build and deploy automatically
- Wait for deployment to complete (2-5 minutes)

### 7. Get Your API URL

After deployment, Render gives you:
- **URL:** `https://examshield-license-server.onrender.com`

Your endpoints:
- Registration: `https://examshield-license-server.onrender.com/register-page`
- Payment: `https://examshield-license-server.onrender.com/payment?key=...`
- Verify: `https://examshield-license-server.onrender.com/verify`
- Admin: `https://examshield-license-server.onrender.com/admin`

## Step 3: Update Client Build

### Set ES_VERIFY_URL

Before building the `.deb` package:

**Linux/Mac:**
```bash
export ES_VERIFY_URL="https://examshield-license-server.onrender.com/verify"
./build_examshield_full.sh
```

**Windows PowerShell:**
```powershell
$env:ES_VERIFY_URL="https://examshield-license-server.onrender.com/verify"
.\build_examshield_full.sh
```

Or edit `build_examshield_full.sh` and change the default:
```bash
VERIFY_URL=os.getenv("ES_VERIFY_URL","https://examshield-license-server.onrender.com/verify")
```

## Step 4: Configure Razorpay Webhook

1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://examshield-license-server.onrender.com/webhook/payment`
3. Select event: `payment.captured`
4. Copy webhook secret → Update `WEBHOOK_SECRET` in Render environment variables

## Step 5: Test Deployment

### Test Health Endpoint
```bash
curl https://examshield-license-server.onrender.com/health
```

### Test Registration
```bash
curl -X POST https://examshield-license-server.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","device_type":"individual"}'
```

### Test Admin Dashboard
- Visit: `https://examshield-license-server.onrender.com/admin`
- Enter admin secret when prompted

## Troubleshooting

### Server Not Starting
- Check Render logs: **Logs** tab in Render dashboard
- Verify environment variables are set correctly
- Check `PORT` is available (Render sets it automatically)

### Data Not Persisting
- Create persistent disk in Render
- Mount to `/opt/render/project/src/server/data`
- Restart service after mounting disk

### Email Not Sending
- Verify SMTP credentials in environment variables
- Check Gmail App Password is correct
- Check Render logs for SMTP errors

### Webhook Not Working
- Verify `WEBHOOK_SECRET` matches Razorpay dashboard
- Check webhook URL is accessible from Razorpay
- Review Render logs for webhook requests

## Free Tier Limitations

Render free tier:
- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- For production, upgrade to paid plan ($7/month)

## Alternative: Keep Server Awake

Add health check endpoint ping:
- Use https://cron-job.org or similar
- Ping `https://examshield-license-server.onrender.com/health` every 10 minutes

## Next Steps

1. ✅ Push to GitHub
2. ✅ Deploy to Render
3. ✅ Set environment variables
4. ✅ Test endpoints
5. ✅ Update client build with Render URL
6. ✅ Configure Razorpay webhook
7. ✅ Link from portfolio

**Your license server is now live!** 🚀

