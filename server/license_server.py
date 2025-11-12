#!/usr/bin/env python3
"""
ExamShield License Server
Flask-based API for license registration, verification, and payment webhook handling.
"""

import os
import json
import hmac
import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__)

# Configuration from environment
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'change-me-secret-key')
ES_DATA_DIR = os.getenv('ES_DATA_DIR', './data')
FLASK_PORT = int(os.getenv('FLASK_PORT', '8080'))
PORT = int(os.getenv('PORT', str(FLASK_PORT)))  # For platforms that set PORT (e.g., Render/Heroku)
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'  # Disable debug in production

LICENSE_DB_PATH = os.path.join(ES_DATA_DIR, 'license_db.json')

# Ensure data directory exists
os.makedirs(ES_DATA_DIR, exist_ok=True)

# Initialize license database if it doesn't exist
def init_license_db():
    if not os.path.exists(LICENSE_DB_PATH):
        with open(LICENSE_DB_PATH, 'w') as f:
            json.dump({}, f, indent=2)

def load_license_db():
    init_license_db()
    try:
        with open(LICENSE_DB_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading license DB: {e}")
        return {}

def save_license_db(db):
    try:
        # Create backup
        if os.path.exists(LICENSE_DB_PATH):
            backup_path = os.path.join(os.path.dirname(LICENSE_DB_PATH), 'backups', 
                                      f"license_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            import shutil
            shutil.copy2(LICENSE_DB_PATH, backup_path)
        
        with open(LICENSE_DB_PATH, 'w') as f:
            json.dump(db, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving license DB: {e}")
        return False

def generate_license_key():
    """Generate a unique license key"""
    return f"ES-{secrets.token_hex(16).upper()}"

def send_email(to_email, subject, body):
    """Send email with license key"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"SMTP not configured. Would send email to {to_email}: {subject}")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/register', methods=['POST'])
def register():
    """Register a new license request"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    device_type = data.get('device_type', 'individual')  # 'individual' or 'organization'
    name = data.get('name', '').strip()  # Individual name or organization name
    
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email required'}), 400
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    db = load_license_db()
    
    # Check if email already registered (prevent duplicate registrations/trials)
    for key, entry in db.items():
        existing_email = entry.get('email', '').strip().lower()
        if existing_email == email:
            # Email already exists - check if it's active or pending
            if entry.get('active', False):
                return jsonify({
                    'error': 'This email already has an active license',
                    'existing_key': key,
                    'message': 'Please use your existing license key or contact support.'
                }), 409  # Conflict status code
            else:
                # Pending payment - allow them to continue with existing registration
                return jsonify({
                    'error': 'This email already has a pending registration',
                    'existing_key': key,
                    'payment_url': f'/payment?key={key}',
                    'message': 'You have a pending registration. Please complete payment or contact support.'
                }), 409
    
    # Generate license key
    license_key = generate_license_key()
    
    # Set device limit based on type
    device_limit = 2 if device_type == 'individual' else 999999  # Unlimited for org
    
    # Create license entry (inactive until payment)
    license_entry = {
        'key': license_key,
        'email': email.lower(),  # Store lowercase for consistency
        'name': name,
        'active': False,
        'created': datetime.now().isoformat(),
        'expires': None,  # Set after payment
        'device_type': device_type,
        'device_limit': device_limit,
        'devices': [],
        'payment_status': 'pending',
        'trial_used': True  # Mark that this email has used registration (prevents free trial)
    }
    
    db[license_key] = license_entry
    save_license_db(db)
    
    # Return registration success with payment redirect URL
    return jsonify({
        'success': True,
        'license_key': license_key,
        'payment_url': f'/payment?key={license_key}',
        'message': 'Registration successful. Redirecting to payment...'
    }), 200

@app.route('/check-trial-eligibility', methods=['POST'])
def check_trial_eligibility():
    """Check if email is eligible for free trial"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email required'}), 400
    
    db = load_license_db()
    
    # Check if email has any registration (active or pending)
    for key, entry in db.items():
        existing_email = entry.get('email', '').strip().lower()
        if existing_email == email:
            return jsonify({
                'eligible': False,
                'reason': 'Email already registered',
                'has_active': entry.get('active', False),
                'has_pending': not entry.get('active', False) and entry.get('payment_status') == 'pending'
            }), 200
    
    return jsonify({
        'eligible': True,
        'message': 'Email is eligible for free trial'
    }), 200

@app.route('/verify', methods=['POST'])
def verify():
    """Verify license key and device fingerprint"""
    data = request.get_json()
    license_key = data.get('key', '').strip()
    device_fingerprint = data.get('device_fingerprint', '').strip()
    
    if not license_key or not device_fingerprint:
        return jsonify({'error': 'License key and device fingerprint required'}), 400
    
    db = load_license_db()
    
    if license_key not in db:
        return jsonify({
            'valid': False,
            'error': 'License key not found'
        }), 404
    
    license_entry = db[license_key]
    
    # Check if license is active
    if not license_entry.get('active', False):
        return jsonify({
            'valid': False,
            'error': 'License not activated. Payment pending.',
            'active': False
        }), 403
    
    # Check expiration
    expires = license_entry.get('expires')
    if expires:
        try:
            exp_date = datetime.fromisoformat(expires)
            if datetime.now() > exp_date:
                return jsonify({
                    'valid': False,
                    'error': 'License expired',
                    'expired': True
                }), 403
        except:
            pass
    
    # Check device limit
    devices = license_entry.get('devices', [])
    device_limit = license_entry.get('device_limit', 2)
    
    # Check if device is already registered
    if device_fingerprint in devices:
        return jsonify({
            'valid': True,
            'active': True,
            'message': 'Device verified'
        }), 200
    
    # Check if device limit reached
    if len(devices) >= device_limit:
        return jsonify({
            'valid': False,
            'error': f'Device limit reached ({device_limit} devices)',
            'device_limit': device_limit,
            'registered_devices': len(devices)
        }), 403
    
    # Register new device
    devices.append(device_fingerprint)
    license_entry['devices'] = devices
    db[license_key] = license_entry
    save_license_db(db)
    
    return jsonify({
        'valid': True,
        'active': True,
        'message': 'Device registered successfully',
        'devices_registered': len(devices),
        'device_limit': device_limit
    }), 200

@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    """Handle payment webhook from payment provider"""
    # Get raw body for signature verification
    raw_body = request.get_data()
    signature = request.headers.get('X-Webhook-Signature', '')
    
    # Verify HMAC signature
    # Allow bypass for testing if WEBHOOK_SECRET is empty or "test" mode
    if WEBHOOK_SECRET and WEBHOOK_SECRET != "change-me-secret-key-here":
        expected_sig = hmac.new(
            WEBHOOK_SECRET.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            return jsonify({
                'error': 'Invalid signature',
                'hint': 'Make sure WEBHOOK_SECRET matches in both client and server'
            }), 401
    
    data = request.get_json()
    
    # Extract payment information (generic format)
    payment_status = data.get('status') or data.get('payment_status') or data.get('event')
    customer_email = data.get('email') or data.get('customer_email') or data.get('customer', {}).get('email')
    transaction_id = data.get('id') or data.get('transaction_id') or data.get('payment_id')
    amount = data.get('amount') or data.get('amount_paid')
    
    # Check if payment is successful
    success_statuses = ['paid', 'payment.succeeded', 'payment.captured', 'success', 'completed']
    if payment_status not in success_statuses:
        return jsonify({
            'message': 'Payment not successful',
            'status': payment_status
        }), 200
    
    if not customer_email:
        return jsonify({'error': 'Customer email not found in webhook'}), 400
    
    # Find license by email and activate it
    db = load_license_db()
    activated = False
    activated_entry = None
    
    for key, entry in db.items():
        if entry.get('email', '').lower() == customer_email.lower() and not entry.get('active', False):
            # Activate license
            activation_date = datetime.now()
            expiry_date = activation_date + timedelta(days=365)  # 1 year validity
            
            entry['active'] = True
            entry['activated'] = activation_date.isoformat()
            entry['expires'] = expiry_date.isoformat()
            entry['transaction_id'] = transaction_id
            entry['payment_amount'] = amount
            entry['payment_status'] = 'completed'
            db[key] = entry
            activated = True
            activated_entry = entry
            break
    
    if activated and activated_entry:
        save_license_db(db)
        
        # Send license email with all details
        license_key = activated_entry.get('key')
        name = activated_entry.get('name', 'Customer')
        device_type = activated_entry.get('device_type', 'individual')
        activation_date_str = activation_date.strftime('%B %d, %Y')
        expiry_date_str = expiry_date.strftime('%B %d, %Y')
        
        email_subject = f"Your ExamShield License is Activated - {license_key}"
        email_body = f"""Dear {name},

Thank you for your purchase! Your ExamShield license has been successfully activated.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LICENSE DETAILS:

License Key: {license_key}
License Type: {device_type.title()}
Device Limit: {'2 devices' if device_type == 'individual' else 'Unlimited devices'}

Activation Date: {activation_date_str}
Expiry Date: {expiry_date_str}
Validity Period: 1 Year

Transaction ID: {transaction_id}
Payment Amount: ${amount if amount else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:

1. Download ExamShield from: https://adulsportfolio.vercel.app/shop
2. During installation, enter your License Key: {license_key}
3. Your license will be automatically verified and activated

IMPORTANT NOTES:

• Keep this email safe - you'll need your license key for installation
• Your license is valid for 1 year from the activation date
• You can use this license on {'2 devices' if device_type == 'individual' else 'unlimited devices'}
• If you need support, contact us with your license key

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing ExamShield!

Best regards,
ExamShield Team
https://adulsportfolio.vercel.app/shop
"""
        
        email_sent = send_email(customer_email, email_subject, email_body)
        
        return jsonify({
            'success': True,
            'message': 'License activated successfully',
            'email_sent': email_sent,
            'license_key': license_key
        }), 200
    else:
        return jsonify({
            'message': 'No pending license found for this email',
            'email': customer_email
        }), 200

@app.route('/admin/revoke', methods=['GET'])
def admin_revoke():
    """Admin endpoint to revoke a license"""
    license_key = request.args.get('key', '').strip()
    admin_secret = request.args.get('secret', '')
    
    # Simple admin secret check (in production, use proper auth)
    if admin_secret != os.getenv('ADMIN_SECRET', 'admin-secret-change-me'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    db = load_license_db()
    
    if license_key not in db:
        return jsonify({'error': 'License key not found'}), 404
    
    db[license_key]['active'] = False
    db[license_key]['revoked'] = datetime.now().isoformat()
    save_license_db(db)
    
    return jsonify({
        'success': True,
        'message': f'License {license_key} revoked'
    }), 200

@app.route('/admin/reports', methods=['GET'])
def admin_reports():
    """Get purchase reports and statistics"""
    admin_secret = request.args.get('secret', '')
    
    if admin_secret != os.getenv('ADMIN_SECRET', 'admin-secret-change-me'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = load_license_db()
    
    reports = []
    stats = {
        'total': 0,
        'active': 0,
        'pending': 0,
        'revenue': 0.0
    }
    
    for key, entry in db.items():
        reports.append({
            'key': entry.get('key'),
            'name': entry.get('name'),
            'email': entry.get('email'),
            'device_type': entry.get('device_type'),
            'active': entry.get('active', False),
            'activated': entry.get('activated'),
            'expires': entry.get('expires'),
            'created': entry.get('created'),
            'payment_amount': entry.get('payment_amount', 0),
            'payment_status': entry.get('payment_status', 'pending'),
            'transaction_id': entry.get('transaction_id')
        })
        
        stats['total'] += 1
        if entry.get('active', False):
            stats['active'] += 1
        elif entry.get('payment_status') == 'pending':
            stats['pending'] += 1
        
        amount = entry.get('payment_amount', 0)
        if amount:
            try:
                stats['revenue'] += float(amount)
            except:
                pass
    
    return jsonify({
        'reports': reports,
        'stats': stats
    }), 200

@app.route('/public/reports', methods=['GET'])
def public_reports():
    """Get public purchase count (if enabled)"""
    # Check if public reports are enabled
    public_enabled = os.getenv('PUBLIC_REPORTS_ENABLED', 'false').lower() == 'true'
    
    if not public_enabled:
        return jsonify({'error': 'Public reports are disabled'}), 403
    
    db = load_license_db()
    
    # Only return count, no sensitive data
    total = len(db)
    active = sum(1 for entry in db.values() if entry.get('active', False))
    
    return jsonify({
        'total_licenses': total,
        'active_licenses': active,
        'last_updated': datetime.now().isoformat()
    }), 200

@app.route('/admin/extend', methods=['GET'])
def admin_extend():
    """Admin endpoint to extend license expiry"""
    license_key = request.args.get('key', '').strip()
    days = int(request.args.get('days', 365))
    admin_secret = request.args.get('secret', '')
    
    if admin_secret != os.getenv('ADMIN_SECRET', 'admin-secret-change-me'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    db = load_license_db()
    
    if license_key not in db:
        return jsonify({'error': 'License key not found'}), 404
    
    current_expires = db[license_key].get('expires')
    if current_expires:
        try:
            exp_date = datetime.fromisoformat(current_expires)
            new_expires = exp_date + timedelta(days=days)
        except:
            new_expires = datetime.now() + timedelta(days=days)
    else:
        new_expires = datetime.now() + timedelta(days=days)
    
    db[license_key]['expires'] = new_expires.isoformat()
    save_license_db(db)
    
    return jsonify({
        'success': True,
        'message': f'License extended by {days} days',
        'new_expires': new_expires.isoformat()
    }), 200

@app.route('/register-page', methods=['GET'])
def register_page():
    """Serve registration HTML page"""
    html_path = os.path.join(os.path.dirname(__file__), 'register.html')
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    return '<h1>Registration page not found</h1>', 404

@app.route('/payment', methods=['GET'])
def payment_page():
    """Serve payment HTML page"""
    html_path = os.path.join(os.path.dirname(__file__), 'payment.html')
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    return '<h1>Payment page not found</h1>', 404

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    """Serve admin dashboard HTML page"""
    html_path = os.path.join(os.path.dirname(__file__), 'admin_dashboard.html')
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    return '<h1>Admin dashboard not found</h1>', 404

@app.route('/success', methods=['GET'])
def success_page():
    """Serve success page after payment"""
    html_path = os.path.join(os.path.dirname(__file__), 'success.html')
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    return '<h1>Success page not found</h1>', 404

@app.route('/license-info', methods=['GET'])
def license_info():
    """Get license information for payment page"""
    license_key = request.args.get('key', '').strip()
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    db = load_license_db()
    
    if license_key not in db:
        return jsonify({'error': 'License key not found'}), 404
    
    entry = db[license_key]
    return jsonify({
        'key': entry.get('key'),
        'name': entry.get('name'),
        'email': entry.get('email'),
        'device_type': entry.get('device_type'),
        'active': entry.get('active', False),
        'payment_status': entry.get('payment_status', 'pending')
    }), 200

@app.route('/payment-config', methods=['GET'])
def payment_config():
    """Return payment provider availability to toggle UI buttons"""
    razorpay_enabled = bool(os.getenv('RAZORPAY_KEY_ID')) and bool(os.getenv('RAZORPAY_KEY_SECRET'))
    stripe_enabled = False  # Placeholder until implemented
    return jsonify({
        'razorpay_enabled': razorpay_enabled,
        'stripe_enabled': stripe_enabled
    }), 200

@app.route('/create-razorpay-order', methods=['POST'])
def create_razorpay_order():
    """Create Razorpay order for payment"""
    data = request.get_json()
    license_key = data.get('license_key', '').strip()
    amount = data.get('amount')  # Amount in paise (optional, will be determined from license)
    currency = data.get('currency', 'INR')
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    # Load license to get device type and determine price
    db = load_license_db()
    if license_key not in db:
        return jsonify({'error': 'License key not found'}), 404
    
    license_entry = db[license_key]
    device_type = license_entry.get('device_type', 'individual')
    
    # Set amount based on license type if not provided
    if not amount:
        if device_type == 'organization':
            amount = 29999  # $299.99 in paise (₹299.99)
        else:
            amount = 9999   # $99.99 in paise (₹99.99)
    
    # Check if Razorpay is configured
    razorpay_key_id = os.getenv('RAZORPAY_KEY_ID', '')
    razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET', '')
    
    if not razorpay_key_id or not razorpay_key_secret:
        return jsonify({
            'error': 'Razorpay not configured',
            'message': 'Please configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env file'
        }), 500
    
    try:
        import razorpay
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        
        order = client.order.create({
            'amount': amount,
            'currency': currency,
            'receipt': license_key,
            'notes': {
                'license_key': license_key,
                'product': 'ExamShield License'
            }
        })
        
        return jsonify({
            'order_id': order['id'],
            'razorpay_key': razorpay_key_id,
            'amount': amount,
            'currency': currency
        }), 200
    except ImportError:
        return jsonify({
            'error': 'Razorpay SDK not installed',
            'message': 'Install with: pip install razorpay'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Failed to create order',
            'message': str(e)
        }), 500

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify payment and activate license"""
    data = request.get_json()
    provider = data.get('provider', '')
    payment_response = data.get('payment_response', {})
    license_key = data.get('license_key', '').strip()
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    db = load_license_db()
    
    if license_key not in db:
        return jsonify({'error': 'License key not found'}), 404
    
    # Verify payment based on provider
    if provider == 'razorpay':
        razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET', '')
        if not razorpay_key_secret:
            return jsonify({'error': 'Razorpay not configured'}), 500
        
        try:
            import razorpay
            client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'), razorpay_key_secret))
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': payment_response.get('razorpay_order_id'),
                'razorpay_payment_id': payment_response.get('razorpay_payment_id'),
                'razorpay_signature': payment_response.get('razorpay_signature')
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            # Payment verified - activate license via webhook simulation
            entry = db[license_key]
            customer_email = entry.get('email', '')
            device_type = entry.get('device_type', 'individual')
            
            # Get payment amount based on device type
            payment_amount = entry.get('payment_amount')
            if not payment_amount:
                payment_amount = 299.99 if device_type == 'organization' else 99.99
                entry['payment_amount'] = payment_amount
            
            # Simulate webhook call
            webhook_data = {
                'status': 'paid',
                'email': customer_email,
                'id': payment_response.get('razorpay_payment_id'),
                'amount': payment_amount
            }
            
            # Activate license (reuse webhook logic)
            activation_date = datetime.now()
            expiry_date = activation_date + timedelta(days=365)
            
            entry['active'] = True
            entry['activated'] = activation_date.isoformat()
            entry['expires'] = expiry_date.isoformat()
            entry['transaction_id'] = payment_response.get('razorpay_payment_id')
            entry['payment_status'] = 'completed'
            db[license_key] = entry
            save_license_db(db)
            
            # Send email
            send_license_email(entry, activation_date, expiry_date, payment_response.get('razorpay_payment_id'))
            
            return jsonify({
                'success': True,
                'message': 'Payment verified and license activated'
            }), 200
            
        except ImportError:
            return jsonify({'error': 'Razorpay SDK not installed'}), 500
        except Exception as e:
            return jsonify({
                'error': 'Payment verification failed',
                'message': str(e)
            }), 400
    
    return jsonify({'error': 'Unsupported payment provider'}), 400

def send_license_email(entry, activation_date, expiry_date, transaction_id):
    """Helper function to send license email"""
    license_key = entry.get('key')
    name = entry.get('name', 'Customer')
    device_type = entry.get('device_type', 'individual')
    customer_email = entry.get('email')
    # Get payment amount from entry or set default based on device type
    amount = entry.get('payment_amount')
    if not amount:
        amount = 299.99 if device_type == 'organization' else 99.99
    
    activation_date_str = activation_date.strftime('%B %d, %Y')
    expiry_date_str = expiry_date.strftime('%B %d, %Y')
    
    email_subject = f"Your ExamShield License is Activated - {license_key}"
    email_body = f"""Dear {name},

Thank you for your purchase! Your ExamShield license has been successfully activated.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LICENSE DETAILS:

License Key: {license_key}
License Type: {device_type.title()}
Device Limit: {'2 devices' if device_type == 'individual' else 'Unlimited devices'}

Activation Date: {activation_date_str}
Expiry Date: {expiry_date_str}
Validity Period: 1 Year

Transaction ID: {transaction_id}
Payment Amount: ${amount if amount else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:

1. Download ExamShield from: https://adulsportfolio.vercel.app/shop
2. During installation, enter your License Key: {license_key}
3. Your license will be automatically verified and activated

IMPORTANT NOTES:

• Keep this email safe - you'll need your license key for installation
• Your license is valid for 1 year from the activation date
• You can use this license on {'2 devices' if device_type == 'individual' else 'unlimited devices'}
• If you need support, contact us with your license key

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing ExamShield!

Best regards,
ExamShield Team
https://adulsportfolio.vercel.app/shop
"""
    
    send_email(customer_email, email_subject, email_body)

@app.route('/activate-trial', methods=['POST'])
def activate_trail():
    """Start a 7-day free trial for a registered (but unpaid) license"""
    data = request.get_json()
    license_key = (data or {}).get('license_key', '').strip()
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    db = load_license_db()
    if license_key not in db:
        return jsonify({'error': 'License key not found'}), 404
    entry = db[license_key]
    if entry.get('active', False):
        return jsonify({'error': 'License already active'}), 400
    if entry.get('trial_active', False):
        return jsonify({'error': 'Trial already activated for this license'}), 400
    # Activate trial (client will enforce; server records for reporting)
    trial_start = datetime.now()
    trial_end = trial_start + timedelta(days=7)
    entry['trial_active'] = True
    entry['trial_started'] = trial_start.isoformat()
    entry['trial_expires'] = trial_end.isoformat()
    db[license_key] = entry
    save_license_db(db)
    # Send email with trial details
    try:
        name = entry.get('name', 'Customer')
        customer_email = entry.get('email')
        device_type = entry.get('device_type', 'individual')
        email_subject = f"Your ExamShield Free Trial Started"
        email_body = f"""Dear {name},

Your 7-day free trial for ExamShield has started.

TRIAL DETAILS:

License Type: {device_type.title()}
Trial Started: {trial_start.strftime('%B %d, %Y')}
Trial Expires: {trial_end.strftime('%B %d, %Y')}

NEXT STEPS:
1. Download ExamShield from: https://adulsportfolio.vercel.app/shop
2. Install normally. The client will allow usage in trial mode for 7 days.
3. You can purchase anytime to activate a full license.

Thank you for trying ExamShield!

Best regards,
ExamShield Team
https://adulsportfolio.vercel.app/shop
"""
        send_email(customer_email, email_subject, email_body)
    except Exception:
        pass
    return jsonify({'success': True, 'message': 'Free trial activated', 'trial_expires': entry['trial_expires']}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'ExamShield License Server'}), 200

if __name__ == '__main__':
    print(f"Starting ExamShield License Server on {FLASK_HOST}:{PORT}")
    print(f"License DB: {LICENSE_DB_PATH}")
    print(f"Debug mode: {DEBUG}")
    app.run(host=FLASK_HOST, port=PORT, debug=DEBUG)

