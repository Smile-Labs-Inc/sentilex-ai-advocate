#!/usr/bin/env python
"""
Test creating an admin with automatic MFA setup
This demonstrates the solution to the chicken-and-egg problem
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.config import get_db
from models.admin import Admin, AdminRole
from utils.auth import hash_password
from datetime import datetime
import pyotp

def create_test_admin():
    """Create a test admin with MFA automatically configured"""
    
    print("\n" + "="*60)
    print("   Creating Test Admin with Automatic MFA Setup")
    print("="*60)
    
    db = next(get_db())
    
    # Test admin details
    email = "test.admin@sentilex.com"
    password = "TestAdmin@2024"
    full_name = "Test Admin"
    role = AdminRole.ADMIN
    
    # Check if exists
    existing = db.query(Admin).filter(Admin.email == email).first()
    if existing:
        print(f"⚠️  Admin already exists: {email}")
        print(f"   Deleting existing admin...")
        db.delete(existing)
        db.commit()
    
    # Generate MFA credentials
    mfa_secret = pyotp.random_base32()
    backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
    
    # Create admin with MFA enabled
    admin = Admin(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        is_active=True,
        is_email_verified=True,
        mfa_enabled=True,  # ✅ MFA enabled from creation
        mfa_secret=mfa_secret,
        mfa_backup_codes=",".join(backup_codes),
        mfa_enabled_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("\n✅ Admin created successfully with MFA enabled!")
    print("="*60)
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Role: {role.value}")
    print(f"   MFA Enabled: Yes")
    print()
    print("📱 MFA Configuration:")
    print(f"   Secret: {mfa_secret}")
    print()
    print("🔑 Backup Codes:")
    for i, code in enumerate(backup_codes, 1):
        print(f"   {i:2d}. {code}")
    print()
    print("="*60)
    print("🎉 CHICKEN-EGG PROBLEM SOLVED!")
    print("="*60)
    print()
    print("The admin can now:")
    print("   1. Login with email + password")
    print("   2. Enter MFA code from authenticator app")
    print("   3. Complete authentication successfully")
    print()
    print("No bootstrapping issue because MFA was set up during creation!")
    print()
    
    return admin, mfa_secret

if __name__ == "__main__":
    create_test_admin()
