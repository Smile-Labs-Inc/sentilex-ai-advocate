#!/usr/bin/env python
"""
Test Admin Login Endpoint

Tests the admin login flow which requires MFA to be enabled.
Note: Admins CANNOT login without MFA being enabled first.

Endpoints tested:
- POST /admin/auth/login

Test Account:
- Email: kaveesha@gmail.com
- Password: KamalKaveesha@2003
- Role: superadmin
- MFA: Not yet enabled (will fail login until MFA is set up)
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test admin credentials
ADMIN_EMAIL = "kaveesha@gmail.com"
ADMIN_PASSWORD = "KamalKaveesha@2003"


def test_admin_login_without_mfa_enabled():
    """Test 1: Admin login WITH MFA enabled (returns temporary token)"""
    print("\n" + "="*60)
    print("Test 1: Admin Login WITH MFA Enabled (Get Temp Token)")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print(f"Response Text: {response.text}")
        print("⚠️  Server error - check backend logs")
        raise Exception("Server returned 500 error")
    print(f"Response Keys: {list(response.json().keys())}")
    
    # Since MFA is enabled, should return 200 with temporary token
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["requires_mfa"] == True, "Should require MFA verification"
    assert data["mfa_enabled"] == True, "MFA should be enabled"
    assert data["user_type"] == "admin", "Should be admin user type"
    assert data["refresh_token"] == "", "Refresh token should be empty until MFA verified"
    print(f"✅ Test passed: Admin login returns temporary token for MFA verification")


def test_admin_login_wrong_password():
    """Test 2: Login with wrong password"""
    print("\n" + "="*60)
    print("Test 2: Admin Login with Wrong Password")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": "WrongPassword123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Invalid credentials" in response.json()["detail"], "Should indicate invalid credentials"
    print("✅ Test passed: Wrong password rejected")


def test_admin_login_nonexistent_email():
    """Test 3: Login with non-existent email"""
    print("\n" + "="*60)
    print("Test 3: Admin Login with Non-existent Email")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": "nonexistent@admin.com",
            "password": "SomePassword123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Invalid credentials" in response.json()["detail"], "Should indicate invalid credentials"
    print("✅ Test passed: Non-existent email rejected")


def test_admin_login_invalid_email_format():
    """Test 4: Login with invalid email format"""
    print("\n" + "="*60)
    print("Test 4: Admin Login with Invalid Email Format")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": "not-an-email",
            "password": ADMIN_PASSWORD
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Should fail validation
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✅ Test passed: Invalid email format rejected")


def test_admin_login_missing_fields():
    """Test 5: Login with missing fields"""
    print("\n" + "="*60)
    print("Test 5: Admin Login with Missing Fields")
    print("="*60)
    
    # Missing password
    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": ADMIN_EMAIL
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✅ Test passed: Missing password rejected")


def test_admin_login_empty_credentials():
    """Test 6: Login with empty credentials"""
    print("\n" + "="*60)
    print("Test 6: Admin Login with Empty Credentials")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "email": "",
            "password": ""
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✅ Test passed: Empty credentials rejected")


def main():
    """Run all admin login tests"""
    print("\n" + "="*60)
    print("ADMIN LOGIN ENDPOINT TESTS")
    print("="*60)
    print(f"Testing admin: {ADMIN_EMAIL}")
    print(f"Base URL: {BASE_URL}")
    print("\nNote: Admin login requires MFA to be enabled.")
    print("These tests verify login validation BEFORE MFA setup.")
    
    try:
        test_admin_login_without_mfa_enabled()
        test_admin_login_wrong_password()
        test_admin_login_nonexistent_email()
        test_admin_login_invalid_email_format()
        test_admin_login_missing_fields()
        test_admin_login_empty_credentials()
        
        print("\n" + "="*60)
        print("✅ ALL ADMIN LOGIN TESTS PASSED!")
        print("="*60)
        print("\n⚠️  NEXT STEPS:")
        print("   1. Run test_admin_mfa.py to set up MFA for this admin")
        print("   2. After MFA is enabled, admin can complete login flow")
        print("   3. Full login requires MFA verification (6-digit code)")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
