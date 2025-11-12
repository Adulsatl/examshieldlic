#!/usr/bin/env python3
"""
Quick script to activate a license by simulating payment webhook.
Usage: python activate_license.py <email> [webhook_secret]
"""

import sys
import os
import requests
import hmac
import hashlib
import json

# Configuration
SERVER_URL = "http://localhost:8080"

# Try to read WEBHOOK_SECRET from server's .env file
def get_webhook_secret():
    """Try to read webhook secret from server .env file"""
    env_paths = [
        os.path.join('server', '.env'),
        os.path.join('server', 'config.env'),
        '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('WEBHOOK_SECRET=') and not line.startswith('#'):
                            return line.split('=', 1)[1].strip()
            except:
                pass
    
    # Default fallback
    return "change-me-secret-key-here"

def activate_license(email, webhook_secret=None):
    """Activate license for given email via webhook"""
    
    if webhook_secret is None:
        webhook_secret = get_webhook_secret()
    
    payload = {
        "status": "paid",
        "email": email,
        "id": f"test_transaction_{hash(email) % 10000}",
        "amount": 99.99
    }
    
    # Calculate HMAC signature
    raw_body = json.dumps(payload).encode()
    signature = hmac.new(
        webhook_secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    
    print(f"Activating license for: {email}")
    print(f"Webhook URL: {SERVER_URL}/webhook/payment")
    print(f"Using secret: {webhook_secret[:10]}..." if len(webhook_secret) > 10 else f"Using secret: {webhook_secret}")
    
    try:
        response = requests.post(
            f"{SERVER_URL}/webhook/payment",
            json=payload,
            headers={"X-Webhook-Signature": signature},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n[SUCCESS] License activated successfully!")
        else:
            print("\n[ERROR] Activation failed")
            
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to server at {SERVER_URL}")
        print("Make sure the license server is running!")
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python activate_license.py <email> [webhook_secret]")
        print("\nExample: python activate_license.py test@example.com")
        print("Or: python activate_license.py test@example.com your-secret-key")
        print("\nNote: Script will try to read WEBHOOK_SECRET from server/.env automatically")
        sys.exit(1)
    
    email = sys.argv[1]
    webhook_secret = sys.argv[2] if len(sys.argv) > 2 else None
    
    activate_license(email, webhook_secret)

