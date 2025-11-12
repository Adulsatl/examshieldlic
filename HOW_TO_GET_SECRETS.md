# How to Get SMTP Gmail, Webhook Secret, and Admin Secret

## 📧 1. Gmail SMTP Credentials

### Step-by-Step Guide

#### Step 1: Enable 2-Step Verification
1. Go to https://myaccount.google.com
2. Click **Security** (left sidebar)
3. Under "Signing in to Google", find **2-Step Verification**
4. Click **Get Started** and follow the setup process
5. You'll need your phone for verification

#### Step 2: Generate App Password
1. Still in **Security** settings
2. Scroll down to **2-Step Verification** section
3. Click **App passwords** (or go directly: https://myaccount.google.com/apppasswords)
4. You may need to sign in again
5. Select app: **Mail**
6. Select device: **Other (Custom name)**
7. Enter name: **ExamShield License Server**
8. Click **Generate**
9. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

#### Step 3: Use in .env File
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # The 16-char app password (remove spaces)
```

**Important Notes:**
- Use your **regular Gmail address** for `SMTP_USER`
- Use the **16-character app password** (not your regular Gmail password)
- Remove spaces from the app password when pasting
- If you lose the password, generate a new one

---

## 🔐 2. Webhook Secret

### What is it?
A secret key used to verify that webhook requests are coming from your payment provider (Razorpay/Stripe).

### How to Generate

#### Option 1: Using PowerShell (Windows)
```powershell
# Generate random 32-character secret
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

#### Option 2: Using Python
```python
import secrets
print(secrets.token_hex(32))
```

#### Option 3: Using OpenSSL (Linux/Mac)
```bash
openssl rand -hex 32
```

#### Option 4: Online Generator
- Go to https://randomkeygen.com
- Use "CodeIgniter Encryption Keys" or "Fort Knox Password"
- Copy a 32+ character random string

#### Option 5: Manual (Simple)
Just create a long random string:
```
WEBHOOK_SECRET=examshield_webhook_2025_secure_key_xyz123abc456
```

### Use in .env File
```env
WEBHOOK_SECRET=your-generated-secret-here
```

**Important:**
- Make it long (32+ characters)
- Use mix of letters, numbers, symbols
- Keep it secret - never share or commit to Git
- Use the **same secret** in both:
  - Your server's `.env` file
  - Your payment provider's webhook settings

### For Razorpay:
1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/payment`
3. Copy the webhook secret they provide
4. Use that as your `WEBHOOK_SECRET`

---

## 🛡️ 3. Admin Secret

### What is it?
A password to protect your admin dashboard from unauthorized access.

### How to Generate

#### Option 1: Using PowerShell (Windows)
```powershell
# Generate random 32-character secret
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

#### Option 2: Using Python
```python
import secrets
print(secrets.token_hex(32))
```

#### Option 3: Using OpenSSL (Linux/Mac)
```bash
openssl rand -hex 32
```

#### Option 4: Simple Password
Create a strong password you'll remember:
```
ADMIN_SECRET=MySecureAdmin2025!ExamShield
```

### Use in .env File
```env
ADMIN_SECRET=your-generated-admin-secret-here
```

**Important:**
- Make it strong and unique
- Don't use common passwords
- Store it securely (password manager)
- You'll need to enter this when accessing `/admin`

---

## 📝 Complete .env Example

Here's a complete example with all secrets:

```env
# SMTP Gmail Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # Gmail App Password (16 chars, no spaces)

# Webhook Security
WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6  # 32+ character random string

# Admin Secret
ADMIN_SECRET=MySecureAdmin2025!ExamShield  # Strong password for admin access

# Razorpay (when ready)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Data Directory
ES_DATA_DIR=./data

# Flask Server
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# Public Reports (optional)
PUBLIC_REPORTS_ENABLED=false
```

---

## 🚀 Quick Setup Script

### Windows PowerShell:
```powershell
# Generate secrets
$webhook = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$admin = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

Write-Host "WEBHOOK_SECRET=$webhook"
Write-Host "ADMIN_SECRET=$admin"
```

### Python:
```python
import secrets
print(f"WEBHOOK_SECRET={secrets.token_hex(32)}")
print(f"ADMIN_SECRET={secrets.token_hex(32)}")
```

---

## ✅ Verification Checklist

After setting up, verify:

- [ ] Gmail App Password generated and working
- [ ] WEBHOOK_SECRET is 32+ characters
- [ ] ADMIN_SECRET is strong and unique
- [ ] All secrets added to `.env` file
- [ ] `.env` file is in `.gitignore` (not committed to Git)
- [ ] Test email sending works
- [ ] Admin dashboard requires secret to access

---

## 🔒 Security Best Practices

1. **Never commit `.env` to Git**
   - Already in `.gitignore` ✅

2. **Use different secrets for production**
   - Don't reuse test secrets

3. **Rotate secrets periodically**
   - Change every 6-12 months

4. **Store backups securely**
   - Use password manager
   - Keep offline backup

5. **Don't share secrets**
   - Never email or message them
   - Use secure sharing if needed

---

## 🆘 Troubleshooting

### Gmail SMTP Not Working?
- ✅ Check 2-Step Verification is enabled
- ✅ Verify App Password is correct (16 chars, no spaces)
- ✅ Try generating new App Password
- ✅ Check firewall allows port 587

### Webhook Verification Failing?
- ✅ Ensure WEBHOOK_SECRET matches in both places
- ✅ Check webhook URL is correct
- ✅ Verify signature format

### Admin Dashboard Access Denied?
- ✅ Check ADMIN_SECRET matches exactly
- ✅ No extra spaces or quotes
- ✅ Case-sensitive

---

## 📞 Quick Reference

| Secret | Length | Where to Get |
|--------|--------|--------------|
| **Gmail App Password** | 16 chars | Google Account → Security → App Passwords |
| **Webhook Secret** | 32+ chars | Generate randomly OR from payment provider |
| **Admin Secret** | Any | Generate randomly OR create strong password |

---

**All set! Copy these into your `server/.env` file and you're ready to go!** 🚀

