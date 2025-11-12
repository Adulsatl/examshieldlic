# How to Implement ExamShield Licensing System

## Overview

This guide walks you through implementing and testing the complete licensing system step-by-step.

## Prerequisites

- Python 3.8+ installed
- pip3 available
- Windows/Linux/Mac OS

## Implementation Steps

### 1. Quick Start (5 minutes)

#### Windows:
```cmd
# Double-click or run:
start_server.bat
```

#### Linux/Mac:
```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config.env .env
# Edit .env with your settings (or leave defaults for testing)
python3 license_server.py
```

The server will start on `http://localhost:8080`

### 2. Configure Server (Optional for Testing)

Edit `server/.env`:

```env
# Minimum required for testing:
WEBHOOK_SECRET=test-secret-123
ADMIN_SECRET=test-admin-123

# SMTP (optional - leave blank if you don't want emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Note:** For testing, you can leave SMTP blank. The server will still work, just won't send emails.

### 3. Test Registration

#### Method 1: Using Web Interface

1. Open browser: `http://localhost:8080/register-page`
2. Enter email and select license type
3. Click "Register License"
4. Copy the license key shown

#### Method 2: Using curl/Postman

```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"device_type\":\"individual\"}"
```

Response will include `license_key` like: `ES-A1B2C3D4E5F6...`

### 4. Activate License (Simulate Payment)

The license starts as inactive. To activate it, simulate a payment webhook:

#### Using Python Script:

Create `activate_license.py`:

```python
import requests
import hmac
import hashlib
import json

SECRET = "test-secret-123"  # Match your WEBHOOK_SECRET
EMAIL = "test@example.com"  # Email you registered with

payload = {
    "status": "paid",
    "email": EMAIL,
    "id": "test_transaction_123",
    "amount": 99.99
}

# Calculate HMAC signature
raw_body = json.dumps(payload).encode()
signature = hmac.new(
    SECRET.encode(),
    raw_body,
    hashlib.sha256
).hexdigest()

response = requests.post(
    "http://localhost:8080/webhook/payment",
    json=payload,
    headers={"X-Webhook-Signature": signature}
)

print(response.status_code)
print(response.json())
```

Run: `python activate_license.py`

### 5. Test License Verification

#### Get Your Device Fingerprint:

```bash
cd client
python license.py
```

This shows your device fingerprint (long hex string).

#### Verify License:

```bash
curl -X POST http://localhost:8080/verify \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"ES-YOUR-KEY-HERE\",\"device_fingerprint\":\"YOUR-FINGERPRINT\"}"
```

Should return: `{"valid": true, "active": true, ...}`

### 6. Test Client Integration

#### Test License Module:

```bash
cd client
python license.py
```

This will:
- Show device fingerprint
- Check license status
- Start 7-day trial if no license

#### Test with ExamShield:

```bash
# Copy license module to system location (Linux/Mac)
sudo mkdir -p /opt/examshield
sudo cp client/license.py /opt/examshield/

# Set verify URL
export ES_VERIFY_URL=http://localhost:8080/verify

# Run examshield
python examshield.py
```

The daemon will check license on startup and exit if invalid.

### 7. Test Installer

#### Build Package:

```bash
./build_examshield_full.sh  # Linux/Mac
# or
bash build_examshield_full.sh  # Windows Git Bash
```

This creates `ExamShield_Installer_v2.4-stable.deb`

#### Test Installer GUI:

```bash
python build/opt/examshield/installer.py
```

The installer will:
1. Show License Key field (optional)
2. Verify key online if provided
3. Allow trial mode if blank
4. Block if invalid key

### 8. Run Test Suite

```bash
cd tests
python test_license_system.py
```

This automatically tests:
- Registration
- Verification
- Webhook activation
- Device limits
- Admin endpoints

## Integration with Payment Providers

### Razorpay Integration

1. In Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/payment`
3. Select event: `payment.captured`
4. Copy webhook secret to `WEBHOOK_SECRET` in `.env`

### Stripe Integration

1. In Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-domain.com/webhook/payment`
3. Select event: `payment_intent.succeeded`
4. Copy signing secret to `WEBHOOK_SECRET` in `.env`

### Gumroad Integration

1. In Gumroad → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/payment`
3. Copy webhook secret to `WEBHOOK_SECRET` in `.env`

**Note:** The webhook handler supports generic format. You may need to adjust payload parsing in `license_server.py` for specific providers.

## Production Deployment

### Quick Checklist:

1. ✅ Server running and accessible
2. ✅ HTTPS configured (Nginx + Let's Encrypt)
3. ✅ SMTP configured for email delivery
4. ✅ Strong secrets set (WEBHOOK_SECRET, ADMIN_SECRET)
5. ✅ Payment provider webhook configured
6. ✅ Backup automation set up
7. ✅ Client ES_VERIFY_URL points to production

### Detailed Steps:

See `docs/setup_steps.md` for complete deployment guide including:
- VPS setup
- Nginx configuration
- SSL certificates
- Systemd service
- Backup automation

## Testing Checklist

- [ ] Server starts without errors
- [ ] `/health` endpoint responds
- [ ] Registration creates license key
- [ ] Email sent (if SMTP configured)
- [ ] Webhook activates license
- [ ] Verification succeeds after activation
- [ ] Device limit enforced (3rd device rejected for individual)
- [ ] Trial mode works (7 days)
- [ ] Admin revoke works
- [ ] Admin extend works
- [ ] Installer verifies license
- [ ] Installer allows trial mode
- [ ] ExamShield daemon checks license on startup

## Common Workflows

### New Customer Flow:

1. Customer visits registration page
2. Enters email, selects license type
3. Receives license key via email
4. Makes payment
5. Payment provider sends webhook
6. License auto-activates
7. Customer installs ExamShield with license key
8. System verifies online and activates

### Trial User Flow:

1. Customer installs ExamShield
2. Leaves license key blank in installer
3. 7-day trial starts automatically
4. After 7 days, system blocks until license purchased

### Admin Operations:

```bash
# Revoke license
curl "http://localhost:8080/admin/revoke?key=ES-XXXXX&secret=YOUR_SECRET"

# Extend license
curl "http://localhost:8080/admin/extend?key=ES-XXXXX&days=365&secret=YOUR_SECRET"
```

## Troubleshooting

### Server Issues

**Port already in use:**
- Change `FLASK_PORT` in `.env`

**Module not found:**
```bash
pip install flask python-dotenv
```

**Permission denied:**
- Check `data/` directory permissions
- On Linux: `chmod 755 data/`

### License Issues

**Verification fails:**
- Check license is activated (`data/license_db.json` shows `"active": true`)
- Check server is accessible
- Verify device fingerprint matches

**Trial not starting:**
- Check `/etc/examshield/trial.json` is writable
- Check license module is in `/opt/examshield/`

### Email Issues

**Not sending:**
- Verify SMTP credentials
- For Gmail: Use App Password
- Check firewall allows port 587
- Test SMTP connection separately

## Next Steps

1. **Test locally** - Follow steps 1-8 above
2. **Configure production** - See `docs/setup_steps.md`
3. **Integrate payment** - Set up webhook with provider
4. **Deploy client** - Build and distribute `.deb` package
5. **Monitor** - Set up logging and alerts

## Support Files

- `QUICKSTART.md` - Quick reference guide
- `docs/setup_steps.md` - Production deployment
- `tests/test_license_system.py` - Automated tests
- `server/config.env` - Configuration template

## Need Help?

1. Check logs: Server output or `data/` directory
2. Review documentation in `docs/`
3. Run test suite: `python tests/test_license_system.py`
4. Check `data/license_db.json` for license status

