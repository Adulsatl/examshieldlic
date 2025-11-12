# ExamShield License Server Deployment Guide

This guide covers deploying the ExamShield License Server to production.

## Prerequisites

- Python 3.8 or higher
- pip3
- SMTP account (Gmail, SendGrid, etc.)
- Domain name (optional, for HTTPS)
- VPS or cloud server (Ubuntu/Debian recommended)

## Step 1: Server Setup

### Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
```

### Clone/Copy Files

```bash
# Create project directory
mkdir -p /opt/examshield-license
cd /opt/examshield-license

# Copy server files
cp -r server/* .
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask python-dotenv
```

## Step 2: Configuration

### Configure Environment Variables

```bash
cp config.env .env
nano .env
```

Update the following:

```env
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Webhook Security (generate a strong random string)
WEBHOOK_SECRET=$(openssl rand -hex 32)

# Data Directory
ES_DATA_DIR=/opt/examshield-license/data

# Flask Server
FLASK_HOST=127.0.0.1
FLASK_PORT=8080

# Admin Secret (generate a strong random string)
ADMIN_SECRET=$(openssl rand -hex 32)
```

**Important Notes:**
- For Gmail: Use an App Password, not your regular password
- Generate strong secrets: `openssl rand -hex 32`
- Keep `.env` file secure and never commit it to Git

## Step 3: Create Systemd Service

Create `/etc/systemd/system/examshield-license.service`:

```ini
[Unit]
Description=ExamShield License Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/examshield-license
Environment="PATH=/opt/examshield-license/venv/bin"
ExecStart=/opt/examshield-license/venv/bin/python3 license_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable examshield-license
sudo systemctl start examshield-license
sudo systemctl status examshield-license
```

## Step 4: Nginx Reverse Proxy (HTTPS)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/examshield-license`:

```nginx
server {
    listen 80;
    server_name license.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/examshield-license /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Get SSL Certificate

```bash
sudo certbot --nginx -d license.yourdomain.com
```

Certbot will automatically configure HTTPS.

## Step 5: Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 6: Backup Setup

Create backup script `/opt/examshield-license/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/examshield-license/backups"
DATA_DIR="/opt/examshield-license/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cp "$DATA_DIR/license_db.json" "$BACKUP_DIR/license_db_$DATE.json"

# Keep only last 30 days
find "$BACKUP_DIR" -name "license_db_*.json" -mtime +30 -delete

echo "Backup completed: license_db_$DATE.json"
```

Make executable:

```bash
chmod +x /opt/examshield-license/backup.sh
```

### Setup Cron Job

```bash
sudo crontab -e
```

Add daily backup at 2 AM:

```
0 2 * * * /opt/examshield-license/backup.sh >> /var/log/examshield-backup.log 2>&1
```

## Step 7: Payment Webhook Configuration

### Razorpay

1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://license.yourdomain.com/webhook/payment`
3. Select events: `payment.captured`
4. Copy webhook secret and update `WEBHOOK_SECRET` in `.env`

### Stripe

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://license.yourdomain.com/webhook/payment`
3. Select events: `payment_intent.succeeded`
4. Copy signing secret and update `WEBHOOK_SECRET` in `.env`

### Gumroad

1. Go to Gumroad → Settings → Webhooks
2. Add webhook URL: `https://license.yourdomain.com/webhook/payment`
3. Copy webhook secret and update `WEBHOOK_SECRET` in `.env`

**Note:** Update the webhook handler in `license_server.py` if needed to match your provider's payload format.

## Step 8: Client Configuration

Update client `VERIFY_URL` environment variable:

```bash
export ES_VERIFY_URL=https://license.yourdomain.com/verify
```

Or set in systemd service for ExamShield daemon:

```ini
[Service]
Environment="ES_VERIFY_URL=https://license.yourdomain.com/verify"
```

## Step 9: Testing

### Test Server Health

```bash
curl http://localhost:8080/health
```

### Test Registration

```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","device_type":"individual"}'
```

### Test Verification

```bash
curl -X POST http://localhost:8080/verify \
  -H "Content-Type: application/json" \
  -d '{"key":"ES-XXXXX","device_fingerprint":"test_fp"}'
```

### Run Test Suite

```bash
cd /path/to/examshieldbroadcast
python3 tests/test_license_system.py
```

## Step 10: Monitoring

### View Logs

```bash
sudo journalctl -u examshield-license -f
```

### Check Service Status

```bash
sudo systemctl status examshield-license
```

### Monitor Disk Space

```bash
df -h /opt/examshield-license/data
```

## Admin Operations

### Revoke License

```bash
curl "https://license.yourdomain.com/admin/revoke?key=ES-XXXXX&secret=YOUR_ADMIN_SECRET"
```

### Extend License

```bash
curl "https://license.yourdomain.com/admin/extend?key=ES-XXXXX&days=365&secret=YOUR_ADMIN_SECRET"
```

## Troubleshooting

### Server Not Starting

1. Check logs: `sudo journalctl -u examshield-license -n 50`
2. Verify `.env` file exists and is readable
3. Check Python path in systemd service
4. Ensure data directory is writable: `sudo chown -R www-data:www-data /opt/examshield-license/data`

### Email Not Sending

1. Verify SMTP credentials
2. For Gmail: Ensure App Password is used (not regular password)
3. Check firewall allows outbound SMTP (port 587)
4. Test SMTP connection manually

### Webhook Not Working

1. Verify webhook secret matches
2. Check webhook URL is accessible from payment provider
3. Review server logs for webhook requests
4. Test webhook signature verification

### License Verification Failing

1. Check license server is accessible from client
2. Verify `ES_VERIFY_URL` environment variable is set
3. Check firewall rules
4. Review server logs for verification requests

## Security Best Practices

1. **Keep secrets secure**: Never commit `.env` to Git
2. **Use HTTPS**: Always use SSL/TLS in production
3. **Regular backups**: Automated daily backups
4. **Monitor logs**: Set up log monitoring and alerts
5. **Update regularly**: Keep Python and dependencies updated
6. **Firewall**: Only expose necessary ports
7. **Strong secrets**: Use cryptographically secure random strings

## Alternative Deployment Options

### Render.com

1. Create new Web Service
2. Connect GitHub repository
3. Set environment variables in dashboard
4. Deploy automatically on push

### AWS EC2

1. Launch Ubuntu EC2 instance
2. Follow steps 1-4 above
3. Configure Security Groups for ports 80, 443
4. Use Elastic IP for static address

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY server/ .
RUN pip install flask python-dotenv
EXPOSE 8080
CMD ["python", "license_server.py"]
```

Build and run:

```bash
docker build -t examshield-license .
docker run -d -p 8080:8080 --env-file .env examshield-license
```

## Support

For issues or questions:
- Check logs: `sudo journalctl -u examshield-license`
- Review this documentation
- Contact support team

