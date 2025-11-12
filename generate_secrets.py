#!/usr/bin/env python3
"""
Quick script to generate secure secrets for ExamShield License Server
Run: python generate_secrets.py
"""

import secrets

print("=" * 60)
print("ExamShield License Server - Secret Generator")
print("=" * 60)
print()

# Generate Webhook Secret
webhook_secret = secrets.token_hex(32)
print("WEBHOOK_SECRET=" + webhook_secret)
print()

# Generate Admin Secret
admin_secret = secrets.token_hex(32)
print("ADMIN_SECRET=" + admin_secret)
print()

print("=" * 60)
print("Copy these into your server/.env file")
print("=" * 60)
print()
print("For Gmail SMTP:")
print("1. Go to: https://myaccount.google.com/apppasswords")
print("2. Generate App Password for 'Mail'")
print("3. Use that 16-character password for SMTP_PASSWORD")
print()

