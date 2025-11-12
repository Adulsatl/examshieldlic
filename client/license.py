#!/usr/bin/env python3
"""
ExamShield Client License Module
Handles license verification, trial management, and device fingerprinting.
"""

import os
import json
import hashlib
import socket
import uuid
import requests
import platform
from datetime import datetime, timedelta

# Cross-platform path configuration
def get_config_dir():
    """Get configuration directory based on OS"""
    system = platform.system()
    if system == 'Windows':
        # Windows: Use AppData
        appdata = os.getenv('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(appdata, 'ExamShield')
    else:
        # Linux/Unix: Use /etc/examshield (requires admin) or user directory
        try:
            # Check if running as root (Linux/Unix only)
            if hasattr(os, 'geteuid') and os.geteuid() == 0:
                config_dir = '/etc/examshield'
            else:
                # User directory for non-root
                config_dir = os.path.join(os.path.expanduser('~'), '.examshield')
        except (AttributeError, OSError):
            # Fallback for systems without geteuid (Windows, some Unix)
            config_dir = os.path.join(os.path.expanduser('~'), '.examshield')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

# Configuration
CONFIG_DIR = get_config_dir()
LICENSE_FILE = os.path.join(CONFIG_DIR, 'license.json')
TRIAL_FILE = os.path.join(CONFIG_DIR, 'trial.json')
VERIFY_URL = os.getenv('ES_VERIFY_URL', 'http://localhost:8080/verify')
TRIAL_DAYS = 7

def get_device_fingerprint():
    """
    Generate unique device fingerprint using MAC address and hostname.
    Returns SHA256 hash as hex string.
    """
    try:
        # Get MAC address
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        
        # Get hostname
        hostname = socket.gethostname()
        
        # Combine and hash
        combined = f"{mac}:{hostname}"
        fingerprint = hashlib.sha256(combined.encode()).hexdigest()
        
        return fingerprint
    except Exception as e:
        # Fallback to hostname only
        hostname = socket.gethostname()
        fingerprint = hashlib.sha256(hostname.encode()).hexdigest()
        return fingerprint

def load_license():
    """Load license information from file"""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def save_license(license_data):
    """Save license information to file"""
    os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump(license_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving license: {e}")
        return False

def load_trial():
    """Load trial information from file"""
    if os.path.exists(TRIAL_FILE):
        try:
            with open(TRIAL_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def save_trial(trial_data):
    """Save trial information to file"""
    os.makedirs(os.path.dirname(TRIAL_FILE), exist_ok=True)
    try:
        with open(TRIAL_FILE, 'w') as f:
            json.dump(trial_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving trial: {e}")
        return False

def check_trial_eligibility(email=None):
    """Check with server if email is eligible for trial"""
    if not email:
        # Try to get email from license file if exists
        license_data = load_license()
        if license_data and 'email' in license_data:
            email = license_data.get('email')
        else:
            return True  # If no email, allow trial (offline mode)
    
    try:
        response = requests.post(
            VERIFY_URL.replace('/verify', '/check-trial-eligibility'),
            json={'email': email},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('eligible', True)
    except:
        # If server unreachable, allow trial (offline mode)
        pass
    
    return True  # Default to allowing trial if check fails

def start_trial(email=None):
    """Initialize 7-day trial period (only if eligible)"""
    # Check eligibility if email provided
    if email and not check_trial_eligibility(email):
        return None  # Not eligible for trial
    
    trial_data = {
        'started': datetime.now().isoformat(),
        'expires': (datetime.now() + timedelta(days=TRIAL_DAYS)).isoformat(),
        'active': True,
        'email': email  # Store email to track trial usage
    }
    save_trial(trial_data)
    return trial_data

def is_trial_expired():
    """Check if trial period has expired"""
    trial = load_trial()
    if not trial:
        return True  # No trial started
    
    expires_str = trial.get('expires')
    if not expires_str:
        return True
    
    try:
        expires = datetime.fromisoformat(expires_str)
        return datetime.now() > expires
    except:
        return True

def verify_key_online(key):
    """
    Verify license key online with server.
    Returns (success, message, data) tuple.
    """
    if not key or not key.strip():
        return False, "License key is empty", None
    
    device_fp = get_device_fingerprint()
    
    try:
        response = requests.post(
            VERIFY_URL,
            json={
                'key': key.strip(),
                'device_fingerprint': device_fp
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                # Save license info
                license_data = {
                    'key': key.strip(),
                    'device_fingerprint': device_fp,
                    'verified': datetime.now().isoformat(),
                    'active': True,
                    'devices_registered': data.get('devices_registered', 0),
                    'device_limit': data.get('device_limit', 2)
                }
                save_license(license_data)
                return True, "License verified successfully", data
            else:
                return False, data.get('error', 'License verification failed'), data
        else:
            error_data = response.json() if response.content else {}
            return False, error_data.get('error', f'Server error: {response.status_code}'), error_data
    
    except requests.exceptions.Timeout:
        return False, "Connection timeout. Please check your internet connection.", None
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to license server. Please check your internet connection.", None
    except Exception as e:
        return False, f"Verification error: {str(e)}", None

def status():
    """
    Check current license status.
    Returns dict with: status (trial/active/expired/invalid), message, days_remaining
    """
    # Check for active license
    license_data = load_license()
    if license_data:
        key = license_data.get('key')
        if key:
            # Verify online
            success, message, data = verify_key_online(key)
            if success:
                return {
                    'status': 'active',
                    'message': 'License is active',
                    'key': key,
                    'devices_registered': data.get('devices_registered', 0) if data else 0,
                    'device_limit': data.get('device_limit', 2) if data else 2
                }
            else:
                # License invalid or expired
                return {
                    'status': 'invalid',
                    'message': message or 'License verification failed',
                    'key': key
                }
    
    # Check trial
    trial = load_trial()
    if trial:
        if is_trial_expired():
            return {
                'status': 'expired',
                'message': f'Trial period expired. Please purchase a license.',
                'trial_started': trial.get('started'),
                'trial_expired': trial.get('expires')
            }
        else:
            expires_str = trial.get('expires')
            try:
                expires = datetime.fromisoformat(expires_str)
                days_left = (expires - datetime.now()).days
                return {
                    'status': 'trial',
                    'message': f'Trial mode active. {days_left} days remaining.',
                    'days_remaining': days_left,
                    'trial_expires': expires_str
                }
            except:
                return {
                    'status': 'trial',
                    'message': 'Trial mode active',
                    'days_remaining': 0
                }
    
    # No license or trial - check if eligible before starting
    # Try to get email from system or user input
    email = None
    # In a real scenario, you might get email from user input or config
    # For now, we'll allow trial but server will prevent duplicate registrations
    
    trial_data = start_trial(email)
    if trial_data:
        return {
            'status': 'trial',
            'message': f'Trial mode started. {TRIAL_DAYS} days remaining.',
            'days_remaining': TRIAL_DAYS,
            'trial_expires': trial_data['expires']
        }
    else:
        # Trial not eligible
        return {
            'status': 'invalid',
            'message': 'Free trial not available. This email has already been registered. Please purchase a license.',
            'requires_purchase': True
        }

def check_and_exit_if_invalid():
    """
    Check license status and exit if invalid/expired.
    Returns True if valid, False if should exit.
    """
    license_status = status()
    
    if license_status['status'] == 'active':
        return True
    elif license_status['status'] == 'trial':
        print(f"⚠️  {license_status['message']}")
        return True  # Allow trial to continue
    elif license_status['status'] == 'expired':
        print(f"❌ {license_status['message']}")
        print("Please purchase a license to continue using ExamShield.")
        return False
    else:  # invalid
        print(f"❌ {license_status['message']}")
        print("Please verify your license key or contact support.")
        return False

if __name__ == '__main__':
    # Test mode
    print("ExamShield License Module Test")
    print("=" * 40)
    
    fp = get_device_fingerprint()
    print(f"Device Fingerprint: {fp}")
    
    stat = status()
    print(f"\nLicense Status: {stat['status']}")
    print(f"Message: {stat['message']}")
    
    if 'days_remaining' in stat:
        print(f"Days Remaining: {stat['days_remaining']}")

