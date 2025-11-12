# Fix: Webhook Signature Error

## Problem
Getting "Invalid signature" error when activating license via webhook.

## Solution

The `WEBHOOK_SECRET` in your activation script must match the `WEBHOOK_SECRET` in your server's `.env` file.

### Quick Fix Options:

#### Option 1: Use the Updated Script (Recommended)
The `activate_license.py` script now automatically reads from `server/.env`:

```bash
python activate_license.py adulsrichu@gmail.com
```

#### Option 2: Check Your Server's Secret

1. Check what secret your server is using:
   ```bash
   # Windows PowerShell
   Get-Content server\.env | Select-String "WEBHOOK_SECRET"
   
   # Linux/Mac
   grep WEBHOOK_SECRET server/.env
   ```

2. Use that secret when running:
   ```bash
   python activate_license.py adulsrichu@gmail.com your-actual-secret-here
   ```

#### Option 3: Update Server's .env File

1. Edit `server/.env` (or create it from `server/config.env`):
   ```env
   WEBHOOK_SECRET=test-secret-123
   ```

2. Restart your server

3. Run activation:
   ```bash
   python activate_license.py adulsrichu@gmail.com test-secret-123
   ```

#### Option 4: For Testing Only - Disable Signature Check

If you're just testing locally, you can temporarily set:
```env
WEBHOOK_SECRET=change-me-secret-key-here
```

The server will skip signature verification for this default value (testing only!).

## Steps to Fix Your Current Issue:

1. **Check if server/.env exists:**
   ```bash
   # If not, create it:
   cd server
   copy config.env .env
   ```

2. **Check the WEBHOOK_SECRET value:**
   ```bash
   # Windows
   type server\.env | findstr WEBHOOK_SECRET
   
   # Linux
   grep WEBHOOK_SECRET server/.env
   ```

3. **Run activation with matching secret:**
   ```bash
   python activate_license.py adulsrichu@gmail.com
   # Script will auto-read from server/.env
   ```

   OR manually specify:
   ```bash
   python activate_license.py adulsrichu@gmail.com your-secret-from-env
   ```

## Verify It Works

After activation, check the license database:
```bash
# Check if license was activated
type data\license_db.json
# Look for "active": true for your email
```

## Common Issues:

- **Secret mismatch**: Most common - secrets don't match
- **No .env file**: Server using default, script using different default
- **Server not restarted**: Changed .env but server still using old value

## Test Without Signature (Local Testing Only)

For local testing, you can use the default secret that bypasses verification:
```env
WEBHOOK_SECRET=change-me-secret-key-here
```

Then run:
```bash
python activate_license.py adulsrichu@gmail.com change-me-secret-key-here
```

**Warning:** Never use this in production! Always use a strong, unique secret.

