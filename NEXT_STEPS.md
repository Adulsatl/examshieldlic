# What to Do Next - Action Plan

## 🎯 Immediate Next Steps (Today)

### Step 1: Test the System Locally

1. **Start the License Server:**
   ```bash
   cd server
   python license_server.py
   ```

2. **Test Registration:**
   - Open: http://localhost:8080/register-page
   - Fill form: Name, Email, License Type
   - Submit → Should redirect to payment page

3. **Test Payment (Simulation):**
   - On payment page, click "Test Payment (Simulate)"
   - Should activate license and send email (if SMTP configured)

4. **Check Admin Dashboard:**
   - Open: http://localhost:8080/admin
   - Enter admin secret (from `.env` or default: `admin-secret-change-me`)
   - View reports and statistics

### Step 2: Configure SMTP (For Email Delivery)

Edit `server/.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use Gmail App Password, not regular password
```

**To get Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate password for "Mail"
5. Use that password in `.env`

### Step 3: Set Strong Secrets

Edit `server/.env`:

```env
# Generate strong secrets (run these commands):
# Windows PowerShell:
# $secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
# Linux/Mac:
# openssl rand -hex 32

WEBHOOK_SECRET=your-strong-random-secret-here
ADMIN_SECRET=your-strong-admin-secret-here
```

## 🚀 Production Deployment (This Week)

### Step 4: Set Up Razorpay Account

1. **Create Razorpay Account:**
   - Go to https://razorpay.com
   - Sign up for account
   - Complete KYC verification

2. **Get API Keys:**
   - Dashboard → Settings → API Keys
   - Copy Key ID and Key Secret
   - Add to `server/.env`:
     ```env
     RAZORPAY_KEY_ID=rzp_live_xxxxx
     RAZORPAY_KEY_SECRET=xxxxx
     ```

3. **Install Razorpay SDK:**
   ```bash
   cd server
   pip install razorpay
   ```

4. **Configure Webhook:**
   - Dashboard → Settings → Webhooks
   - Add webhook URL: `https://your-domain.com/webhook/payment`
   - Select event: `payment.captured`
   - Copy webhook secret → Update `WEBHOOK_SECRET` in `.env`

### Step 5: Deploy to Production Server

**Option A: VPS (Recommended)**

1. **Get a VPS:**
   - DigitalOcean, AWS EC2, or any Linux VPS
   - Ubuntu 20.04+ recommended

2. **Deploy Server:**
   ```bash
   # On your VPS
   git clone your-repo
   cd examshieldbroadcast/server
   
   # Install dependencies
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configure .env
   nano .env  # Add all your production settings
   
   # Run server (use systemd for production)
   ```

3. **Set Up Systemd Service:**
   - See `docs/setup_steps.md` for detailed instructions
   - Create `/etc/systemd/system/examshield-license.service`

4. **Configure Nginx + SSL:**
   - Set up reverse proxy
   - Get SSL certificate (Let's Encrypt)
   - See `docs/setup_steps.md`

**Option B: Cloud Platform (Easier)**

1. **Render.com:**
   - Connect GitHub repo
   - Set environment variables
   - Deploy automatically

2. **Heroku:**
   - Create app
   - Set config vars
   - Deploy

### Step 6: Update URLs

After deployment, update:

1. **Email Templates:**
   - Change `localhost:8080` to your production domain
   - Update download link to your portfolio

2. **Payment Page:**
   - Update API URLs in `payment.html`

3. **Registration Page:**
   - Update redirect URLs

## 🔗 Portfolio Integration (This Week)

### Step 7: Add to Your Portfolio

Add to `https://adulsportfolio.vercel.app`:

**1. Purchase Count Widget:**
```html
<div id="examshield-stats">
  <h3>ExamShield Licenses</h3>
  <p id="license-count">Loading...</p>
  <script>
    fetch('https://your-license-server.com/public/reports')
      .then(res => res.json())
      .then(data => {
        document.getElementById('license-count').textContent = 
          data.active_licenses + ' active licenses';
      })
      .catch(() => {
        document.getElementById('license-count').textContent = 'Check back soon';
      });
  </script>
</div>
```

**2. Buy Button:**
```html
<a href="https://your-license-server.com/register-page" 
   class="buy-button"
   target="_blank">
  Buy ExamShield License - $99.99
</a>
```

**3. Enable Public Reports:**
```env
# In server/.env
PUBLIC_REPORTS_ENABLED=true
```

## ✅ Testing Checklist

Before going live, test:

- [ ] Registration works
- [ ] Payment page loads
- [ ] Test payment activates license
- [ ] Email is sent after payment
- [ ] License verification works
- [ ] Admin dashboard accessible
- [ ] Reports show correct data
- [ ] CSV export works
- [ ] Duplicate prevention works
- [ ] Public reports work (if enabled)

## 📋 Quick Reference

### Important URLs (After Deployment)

- Registration: `https://your-domain.com/register-page`
- Payment: `https://your-domain.com/payment?key=ES-XXXXX`
- Success: `https://your-domain.com/success?key=ES-XXXXX`
- Admin: `https://your-domain.com/admin`
- Public Reports: `https://your-domain.com/public/reports`

### Environment Variables Checklist

```env
# Required
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
WEBHOOK_SECRET=strong-random-secret
ADMIN_SECRET=strong-admin-secret

# Payment (Required for real payments)
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Optional
PUBLIC_REPORTS_ENABLED=false
ES_DATA_DIR=./data
FLASK_PORT=8080
```

## 🆘 Need Help?

1. **Check Documentation:**
   - `COMPLETE_SETUP_GUIDE.md` - Full setup guide
   - `docs/setup_steps.md` - Deployment instructions
   - `PAYMENT_AND_ADMIN_SETUP.md` - Payment & admin setup

2. **Test Locally First:**
   - Make sure everything works on localhost
   - Test all flows before deploying

3. **Common Issues:**
   - Email not sending → Check SMTP credentials
   - Payment not working → Check Razorpay keys
   - Admin access denied → Check ADMIN_SECRET

## 🎯 Priority Order

**Do This First:**
1. ✅ Test locally
2. ✅ Configure SMTP
3. ✅ Set strong secrets

**Then:**
4. ✅ Set up Razorpay
5. ✅ Deploy to production
6. ✅ Update URLs
7. ✅ Integrate with portfolio

**Finally:**
8. ✅ Test complete flow
9. ✅ Go live!

## 📞 Support

If you encounter issues:
1. Check server logs
2. Review error messages
3. Test endpoints with curl/Postman
4. Check `.env` configuration

---

**You're ready to go! Start with Step 1 (testing locally) and work through the list.** 🚀

