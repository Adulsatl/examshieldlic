# Quick Start Checklist

## ✅ Pre-Flight Check

- [ ] Python 3.8+ installed
- [ ] Server files in `server/` directory
- [ ] `.env` file created (copy from `config.env`)

## 🚀 Start Testing (5 minutes)

### 1. Install Dependencies
```bash
cd server
pip install -r requirements.txt
```

### 2. Configure Basic Settings
Edit `server/.env`:
```env
# Minimum required for testing:
WEBHOOK_SECRET=test-secret-123
ADMIN_SECRET=test-admin-123

# SMTP (optional - leave blank if not testing emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Start Server
```bash
python license_server.py
```

### 4. Test in Browser
- Open: http://localhost:8080/register-page
- Fill form and submit
- Should redirect to payment page
- Click "Test Payment (Simulate)"
- Check email (if SMTP configured)

## 📝 What You Should See

✅ Server starts: `Starting ExamShield License Server on 0.0.0.0:8080`
✅ Registration page loads
✅ Payment page shows license info
✅ Test payment activates license
✅ Admin dashboard shows reports

## 🎯 Next Actions

1. **If everything works:** → Proceed to production deployment
2. **If errors:** → Check error messages, verify `.env` settings
3. **If emails not sending:** → Configure SMTP or skip for now

## 🔧 Common First-Time Issues

**Port already in use:**
- Change `FLASK_PORT=8081` in `.env`

**Module not found:**
- Run: `pip install -r requirements.txt`

**Permission denied:**
- Check `data/` directory is writable

---

**Ready? Start the server and test!** 🚀

