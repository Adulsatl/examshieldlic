#!/usr/bin/env python3
"""
Test script for ExamShield License System
Run this after starting the license server to test all endpoints.
"""

import requests
import json
import hmac
import hashlib
import time

# Configuration
BASE_URL = "http://localhost:8080"
WEBHOOK_SECRET = "change-me-secret-key"  # Should match server config

def test_register():
    """Test license registration"""
    print("\n[TEST] Registering new license...")
    response = requests.post(f"{BASE_URL}/register", json={
        "email": "test@example.com",
        "device_type": "individual"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    if response.status_code == 200:
        return data.get('license_key')
    return None

def test_verify(license_key, device_fp):
    """Test license verification"""
    print(f"\n[TEST] Verifying license {license_key}...")
    response = requests.post(f"{BASE_URL}/verify", json={
        "key": license_key,
        "device_fingerprint": device_fp
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200 and data.get('valid', False)

def test_webhook(license_key, email):
    """Test payment webhook"""
    print(f"\n[TEST] Simulating payment webhook for {email}...")
    
    # Create webhook payload
    payload = {
        "status": "paid",
        "email": email,
        "id": "test_transaction_123",
        "amount": 99.99
    }
    
    # Calculate HMAC signature
    raw_body = json.dumps(payload).encode()
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    
    response = requests.post(
        f"{BASE_URL}/webhook/payment",
        json=payload,
        headers={"X-Webhook-Signature": signature}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200

def test_device_limit(license_key, device_fps):
    """Test device limit enforcement"""
    print(f"\n[TEST] Testing device limit for {license_key}...")
    results = []
    for i, fp in enumerate(device_fps, 1):
        print(f"  Registering device {i}...")
        response = requests.post(f"{BASE_URL}/verify", json={
            "key": license_key,
            "device_fingerprint": fp
        })
        data = response.json()
        valid = response.status_code == 200 and data.get('valid', False)
        results.append(valid)
        print(f"  Device {i}: {'✓' if valid else '✗'} - {data.get('message', '')}")
    return results

def test_admin_revoke(license_key):
    """Test admin revoke endpoint"""
    print(f"\n[TEST] Testing admin revoke for {license_key}...")
    response = requests.get(f"{BASE_URL}/admin/revoke", params={
        "key": license_key,
        "secret": "admin-secret-change-me"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200

def test_admin_extend(license_key):
    """Test admin extend endpoint"""
    print(f"\n[TEST] Testing admin extend for {license_key}...")
    response = requests.get(f"{BASE_URL}/admin/extend", params={
        "key": license_key,
        "days": 365,
        "secret": "admin-secret-change-me"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200

def main():
    print("=" * 60)
    print("ExamShield License System Test Suite")
    print("=" * 60)
    print("\nMake sure the license server is running on", BASE_URL)
    input("Press Enter to continue...")
    
    # Test 1: Register
    license_key = test_register()
    if not license_key:
        print("❌ Registration failed. Cannot continue tests.")
        return
    
    # Test 2: Verify (should fail - license not activated)
    device_fp1 = "test_device_fingerprint_1"
    print("\n[EXPECTED] Verification should fail (license not activated)")
    test_verify(license_key, device_fp1)
    
    # Test 3: Webhook activation
    test_webhook(license_key, "test@example.com")
    time.sleep(1)  # Wait for DB update
    
    # Test 4: Verify (should succeed now)
    print("\n[EXPECTED] Verification should succeed (license activated)")
    test_verify(license_key, device_fp1)
    
    # Test 5: Device limit (individual = 2 devices)
    device_fps = [
        "test_device_fingerprint_1",
        "test_device_fingerprint_2",
        "test_device_fingerprint_3"  # Should be rejected
    ]
    print("\n[EXPECTED] Device 3 should be rejected (limit reached)")
    test_device_limit(license_key, device_fps)
    
    # Test 6: Admin revoke
    test_admin_revoke(license_key)
    
    # Test 7: Admin extend
    test_admin_extend(license_key)
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

