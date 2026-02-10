#!/usr/bin/env python
"""
Test complete admin login flow with MFA (no chicken-egg problem!)
"""

import requests
import pyotp
import json

BASE_URL = "http://127.0.0.1:8001"

# Test admin created with MFA enabled from the start
ADMIN_EMAIL = "test.admin@sentilex.com"
ADMIN_PASSWORD = "TestAdmin@2024"
MFA_SECRET = "AQZIMM5WIKVLB55KHG3M2LCMLCFAHQKK"  # From creation output

def test_complete_admin_flow():
    """Test the complete admin authentication flow"""
    
    print("\n" + "="*60)
    print("TESTING COMPLETE ADMIN LOGIN FLOW")
    print("="*60)
    
    # Step 1: Login with email + password
    print("\n📧 Step 1: Login with email + password...")
    login_response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    print(f"   Status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.json()}")
        return False
    
    login_data = login_response.json()
    print(f"   ✅ Received temporary token")
    print(f"   Requires MFA: {login_data['requires_mfa']}")
    
    temp_token = login_data['access_token']
    
    # Step 2: Generate MFA code
    print("\n🔐 Step 2: Generate MFA code from secret...")
    totp = pyotp.TOTP(MFA_SECRET)
    mfa_code = totp.now()
    print(f"   Generated code: {mfa_code}")
    
    # Step 3: Verify MFA code
    print("\n✅ Step 3: Verify MFA code...")
    verify_response = requests.post(
        f"{BASE_URL}/admin/auth/mfa/verify",
        json={
            "temp_token": temp_token,
            "code": mfa_code,
            "ip_address": "127.0.0.1",
            "user_agent": "test-client"
        }
    )
    
    print(f"   Status: {verify_response.status_code}")
    if verify_response.status_code != 200:
        print(f"   ❌ MFA verification failed: {verify_response.json()}")
        return False
    
    verify_data = verify_response.json()
    print(f"   ✅ MFA verified successfully!")
    print(f"   Admin: {verify_data['name']} ({verify_data['role']})")
    print(f"   Access token: {verify_data['access_token'][:30]}...")
    print(f"   Refresh token: {verify_data['refresh_token'][:30]}...")
    
    print("\n" + "="*60)
    print("🎉 COMPLETE FLOW SUCCESSFUL!")
    print("="*60)
    print("\n✅ Solution Confirmed:")
    print("   • Admin was created with MFA enabled from the start")
    print("   • No chicken-egg problem encountered")
    print("   • Login → MFA verification → Full access granted")
    print("   • Admin can now use the system with MFA security")
    print()
    
    return True

if __name__ == "__main__":
    success = test_complete_admin_flow()
    if not success:
        print("\n❌ Test failed!")
        exit(1)
