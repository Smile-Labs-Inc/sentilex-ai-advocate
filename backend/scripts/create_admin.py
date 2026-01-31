#!/usr/bin/env python
"""
Create Initial Admin Account

This script creates the first admin account for the SentiLex AI Advocate system.
Run this after applying the 002_auth_system migration.

Usage:
    python create_admin.py
"""

import sys
import os
from pathlib import Path
from getpass import getpass

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from database.config import get_db, check_db_connection
from models.admin import Admin, AdminRole
from utils.auth import hash_password
from datetime import datetime
import pyotp
import qrcode
from io import BytesIO


def create_admin_account():
    """Create the initial admin account"""
    
    print("=" * 60)
    print("   SentiLex AI Advocate - Create Initial Admin Account")
    print("=" * 60)
    print()
    
    # Check database connection
    if not check_db_connection():
        print("❌ Database connection failed!")
        print("   Please ensure the database is running and configured correctly.")
        sys.exit(1)
    
    # Get admin details
    print("Enter admin account details:")
    print()
    
    full_name = input("Full Name: ").strip()
    if not full_name:
        print("❌ Full name is required!")
        sys.exit(1)
    
    email = input("Email: ").strip().lower()
    if not email or '@' not in email:
        print("❌ Valid email is required!")
        sys.exit(1)
    
    password = getpass("Password (min 12 chars): ")
    if len(password) < 12:
        print("❌ Password must be at least 12 characters!")
        sys.exit(1)
    
    password_confirm = getpass("Confirm Password: ")
    if password != password_confirm:
        print("❌ Passwords do not match!")
        sys.exit(1)
    
    # Ask for role
    print()
    print("Select role:")
    print("  1. Admin (standard access)")
    print("  2. Superadmin (full system access)")
    role_choice = input("Choice [1]: ").strip() or "1"
    
    if role_choice == "2":
        role = AdminRole.SUPERADMIN  # Uses the enum, which has lowercase value
        print("⚠️  Creating SUPERADMIN account!")
    else:
        role = AdminRole.ADMIN  # Uses the enum, which has lowercase value
        print("ℹ️  Creating ADMIN account")
    
    print()
    confirm = input("Create this admin account? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Cancelled")
        sys.exit(0)
    
    # Create admin account
    try:
        db = next(get_db())
        
        # Check if admin already exists
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"❌ Admin with email {email} already exists!")
            sys.exit(1)
        
        # Hash password using the same method as the rest of the system
        password_hash = hash_password(password)
        
        # Generate MFA secret and backup codes
        print()
        print("=" * 60)
        print("   Setting up Multi-Factor Authentication (MFA)")
        print("=" * 60)
        
        mfa_secret = pyotp.random_base32()
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        
        # Generate QR code for easy setup
        totp_uri = pyotp.totp.TOTP(mfa_secret).provisioning_uri(
            name=email,
            issuer_name="SentiLex AI Advocate"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Print QR code to terminal
        qr.print_ascii()
        
        print()
        print(f"📱 MFA Secret: {mfa_secret}")
        print()
        print("🔑 Backup Codes (save these securely!):")
        for i, code in enumerate(backup_codes, 1):
            print(f"   {i:2d}. {code}")
        print()
        
        # Create admin
        admin = Admin(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
            is_email_verified=True,  # First admin is pre-verified
            mfa_enabled=True,  # MFA is mandatory for admins
            mfa_secret=mfa_secret,
            mfa_backup_codes=",".join(backup_codes),
            mfa_enabled_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print()
        print("=" * 60)
        print("✅ Admin account created successfully!")
        print("=" * 60)
        print(f"   ID: {admin.id}")
        print(f"   Name: {admin.full_name}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role.value}")
        print(f"   MFA Enabled: Yes")
        print()
        print("=" * 60)
        print("⚠️  IMPORTANT - SAVE THIS INFORMATION SECURELY")
        print("=" * 60)
        print()
        print("📱 To complete MFA setup:")
        print("   1. Open your authenticator app (Google Authenticator, Authy, etc.)")
        print("   2. Scan the QR code above OR manually enter the secret:")
        print(f"      Secret: {mfa_secret}")
        print("   3. Save the backup codes in a secure location")
        print("   4. You'll need a 6-digit code from the app to login")
        print()
        print("🔐 Security Notes:")
        print("   - MFA is MANDATORY for all admin accounts")
        print("   - Backup codes are single-use")
        print("   - Each backup code can only be used once")
        print("   - Keep login credentials and backup codes secure")
        print()
        
    except Exception as e:
        print(f"❌ Error creating admin account: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_admin_account()
