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
from datetime import datetime

# Note: Install argon2-cffi first: pip install argon2-cffi
try:
    from argon2 import PasswordHasher
    ph = PasswordHasher()
except ImportError:
    print("⚠️  argon2-cffi not installed. Using basic hashing (NOT FOR PRODUCTION!)")
    import hashlib
    class PasswordHasher:
        @staticmethod
        def hash(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()
    ph = PasswordHasher()


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
        
        # Hash password
        password_hash = ph.hash(password)
        
        # Create admin
        admin = Admin(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
            is_email_verified=True,  # First admin is pre-verified
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
        print()
        print("⚠️  IMPORTANT NEXT STEPS:")
        print("   1. The admin MUST set up MFA (2FA) on first login")
        print("   2. MFA is mandatory for all admin accounts")
        print("   3. Keep login credentials secure")
        print()
        
    except Exception as e:
        print(f"❌ Error creating admin account: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_admin_account()
