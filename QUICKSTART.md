# ExamShield Licensing System - Quick Start Guide

This guide shows you how to run and test the licensing system locally.

## Step 1: Start the License Server

### Option A: Quick Test (Development Mode)

```bash
# Navigate to server directory
cd server

# Install dependencies
pip3 install flask python-dotenv

# Copy and configure environment
cp config.env .env
# Edit .env and set at minimum:
# - SMTP settings (or leave blank for testing - emails won't send)
# - WEBHOOK_SECRET (any random string)
# - ADMIN_SECRET (any random string)

# Run the server
python3 license_server.py
```

The server will start on `http://localhost:8080`

### Option B: Using Virtual Environment (Recommended)

```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure .env file
cp config.env .env
# Edit .env with your settings

# Run server
python3 license_server.py
```

## Step 2: Test the Server

### Test Health Endpoint

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{"status": "ok", "service": "ExamShield License Server"}
```

### Test Registration

```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","device_type":"individual"}'
```

This will:
- Generate a license key
- Save it to `data/license_db.json`
- Send email (if SMTP configured)

### View Registration Page

Open in browser: `http://localhost:8080/register-page`

## Step 3: Test License Verification

### Get Device Fingerprint

```bash
# Run the client license module
cd client
python3 license.py
```

This will show your device fingerprint.

### Verify License

```bash
# Replace ES-XXXXX with actual license key from registration
curl -X POST http://localhost:8080/verify \
  -H "Content-Type: application/json" \
  -d '{
    "key": "ES-XXXXX",
    "device_fingerprint": "your_device_fingerprint_here"
  }'
```

**Note:** Verification will fail until license is activated via webhook.

## Step 4: Simulate Payment Webhook

### Activate License via Webhook

```bash
# Generate HMAC signature (replace secret with your WEBHOOK_SECRET)
SECRET="change-me-secret-key"
PAYLOAD='{"status":"paid","email":"test@example.com","id":"test_123","amount":99.99}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

# Send webhook
curl -X POST http://localhost:8080/webhook/payment \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

**Windows PowerShell version:**
```powershell
$secret = "change-me-secret-key"
$payload = '{"status":"paid","email":"test@example.com","id":"test_123","amount":99.99}'
$hmac = New-Object System.Security.Cryptography.HMACSHA256
$hmac.Key = [System.Text.Encoding]::UTF8.GetBytes($secret)
$signature = [System.BitConverter]::ToString($hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($payload))).Replace("-","").ToLower()

Invoke-WebRequest -Uri "http://localhost:8080/webhook/payment" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"; "X-Webhook-Signature"=$signature} `
  -Body $payload
```

Now verify again - it should succeed!

## Step 5: Test Client Integration

### Test License Module

```bash
cd client
python3 license.py
```

This will:
- Show device fingerprint
- Check license status
- Start trial if no license found

### Test with ExamShield Daemon

```bash
# Make sure license.py is accessible
sudo mkdir -p /opt/examshield
sudo cp client/license.py /opt/examshield/

# Set verify URL (optional, defaults to localhost:8080)
export ES_VERIFY_URL=http://localhost:8080/verify

# Run examshield (it will check license on startup)
python3 examshield.py
```

## Step 6: Test Installer

### Build the Package

```bash
# Make sure all files are in place
./build_examshield_full.sh
```

This creates `ExamShield_Installer_v2.4-stable.deb`

### Test Installer GUI

```bash
# Run installer directly
python3 build/opt/examshield/installer.py
```

The installer will:
- Show License Key field (optional)
- Verify key online if provided
- Activate trial if blank
- Block installation if invalid key

## Step 7: Run Full Test Suite

```bash
# Make sure server is running
# In another terminal:
cd tests
python3 test_license_system.py
```

This will test:
- Registration
- Verification (before/after activation)
- Device limits
- Admin endpoints

## Step 8: Admin Operations

### Revoke License

```bash
curl "http://localhost:8080/admin/revoke?key=ES-XXXXX&secret=admin-secret-change-me"
```

### Extend License

```bash
curl "http://localhost:8080/admin/extend?key=ES-XXXXX&days=365&secret=admin-secret-change-me"
```

## Common Issues & Solutions

### Server Won't Start

1. **Port already in use:**
   ```bash
   # Change port in .env: FLASK_PORT=8081
   ```

2. **Missing dependencies:**
   ```bash
   pip3 install flask python-dotenv
   ```

3. **Permission errors:**
   ```bash
   # Make sure data/ directory is writable
   chmod 755 data/
   ```

### Email Not Sending

- For Gmail: Use App Password (not regular password)
- Check SMTP settings in `.env`
- Test SMTP connection separately
- Server will still work without email (just won't send keys)

### License Verification Fails

1. **Check server is running:** `curl http://localhost:8080/health`
2. **Check license is activated:** Look in `data/license_db.json` for `"active": true`
3. **Check device fingerprint matches**
4. **Check ES_VERIFY_URL environment variable**

### Installer Can't Verify License

1. Make sure license server is accessible from installer machine
2. Check firewall allows connection to port 8080
3. Update `ES_VERIFY_URL` if server is on different host
4. Installer will allow trial mode even if server is unreachable

## Next Steps

1. **Configure Production Server:**
   - See `docs/setup_steps.md` for deployment guide
   - Set up HTTPS with Nginx
   - Configure real SMTP
   - Set strong secrets

2. **Integrate Payment Provider:**
   - Set up Razorpay/Stripe/Gumroad webhook
   - Update `WEBHOOK_SECRET` in production
   - Test webhook delivery

3. **Deploy Client:**
   - Build `.deb` package
   - Distribute to users
   - Set `ES_VERIFY_URL` to production server

## File Structure Reference

```
examshieldbroadcast/
├── server/
│   ├── license_server.py    # Main Flask server
│   ├── config.env            # Configuration template
│   ├── register.html         # Web registration page
│   └── requirements.txt      # Python dependencies
├── client/
│   └── license.py            # Client license module
├── data/
│   └── license_db.json       # License database (auto-created)
├── tests/
│   └── test_license_system.py # Test suite
└── docs/
    └── setup_steps.md        # Deployment guide
```

## Quick Commands Cheat Sheet

```bash
# Start server
cd server && python3 license_server.py

# Register license
curl -X POST http://localhost:8080/register -H "Content-Type: application/json" -d '{"email":"test@example.com","device_type":"individual"}'

# Verify license
curl -X POST http://localhost:8080/verify -H "Content-Type: application/json" -d '{"key":"ES-XXXXX","device_fingerprint":"fp"}'

# Activate via webhook
curl -X POST http://localhost:8080/webhook/payment -H "Content-Type: application/json" -H "X-Webhook-Signature: sig" -d '{"status":"paid","email":"test@example.com"}'

# Test client
cd client && python3 license.py

# Build package
./build_examshield_full.sh
```

