#!/usr/bin/env python3
"""
Register a license and activate it in one step.
Usage: python register_and_activate.py <email> [device_type]
"""

import sys
import requests
import time
import os
import hmac
import hashlib
import json

SERVER_URL = "http://localhost:8080"

def get_webhook_secret():
    """Read webhook secret from server .env"""
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
    
    return "change-me-secret-key-here"

def register_and_activate(email, device_type="individual"):
    """Register license and activate it"""
    
    print(f"Registering license for: {email}")
    print(f"Device type: {device_type}")
    
    # Step 1: Register
    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            json={"email": email, "device_type": device_type},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Registration failed: {response.status_code}")
            print(response.json())
            return False
        
        data = response.json()
        license_key = data.get('license_key')
        
        if not license_key:
            print("[ERROR] No license key received")
            return False
        
        print(f"[SUCCESS] License registered: {license_key}")
        print("Activating license...")
        
        # Step 2: Activate via webhook
        webhook_secret = get_webhook_secret()
        
        payload = {
            "status": "paid",
            "email": email,
            "id": f"test_transaction_{hash(email) % 10000}",
            "amount": 99.99
        }
        
        raw_body = json.dumps(payload).encode()
        signature = hmac.new(
            webhook_secret.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        
        time.sleep(0.5)  # Small delay
        
        response = requests.post(
            f"{SERVER_URL}/webhook/payment",
            json=payload,
            headers={"X-Webhook-Signature": signature},
            timeout=10
        )
        
        if response.status_code == 200:
            print("[SUCCESS] License activated!")
            print(f"\nLicense Key: {license_key}")
            print(f"Email: {email}")
            print(f"Status: Active")
            return True
        else:
            print(f"[ERROR] Activation failed: {response.status_code}")
            print(response.json())
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {SERVER_URL}")
        print("Make sure the license server is running!")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python register_and_activate.py <email> [device_type]")
        print("\nExample: python register_and_activate.py test@example.com")
        print("         python register_and_activate.py test@example.com organization")
        sys.exit(1)
    
    email = sys.argv[1]
    device_type = sys.argv[2] if len(sys.argv) > 2 else "individual"
    
    register_and_activate(email, device_type)

