"""Test script for /auth/mfa/setup, /auth/mfa/enable, and /auth/mfa/status endpoints"""
import requests
import pyotp

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing MFA Setup & Enable Endpoints")
print("=" * 60)
print()

# Setup: Login to get access token
print("Setup: Login as existing user")
print("-" * 60)

test_email = "dilani.w@yahoo.com"
test_password = "Welcome@2024"

print(f"Logging in as {test_email}...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": test_password
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()
access_token = login_data["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
print(f"✅ Login successful!")
print()

print("=" * 60)

# Test 1: Get MFA status before setup
print("Test 1: Check MFA status before setup")
print("-" * 60)
print("1.1. Calling GET /auth/mfa/status...")

status_response = requests.get(f"{BASE_URL}/auth/mfa/status", headers=headers)

print(f"   Status Code: {status_response.status_code}")
if status_response.status_code == 200:
    status_data = status_response.json()
    print(f"   ✅ MFA Status retrieved!")
    print(f"   Enabled: {status_data.get('mfa_enabled')}")
    print(f"   Backup Codes Available: {status_data.get('backup_codes_remaining')}")
else:
    print(f"   Response: {status_response.text}")

print()
print("=" * 60)

# Test 2: Initialize MFA setup
print("Test 2: Initialize MFA setup")
print("-" * 60)
print("2.1. Calling POST /auth/mfa/setup...")

setup_response = requests.post(f"{BASE_URL}/auth/mfa/setup", headers=headers)

print(f"   Status Code: {setup_response.status_code}")
if setup_response.status_code == 200:
    setup_data = setup_response.json()
    print(f"   ✅ MFA setup initialized!")
    
    secret = setup_data.get('secret')
    qr_code_url = setup_data.get('qr_code_url')
    backup_codes = setup_data.get('backup_codes')
    
    print(f"   Secret: {secret}")
    print(f"   QR Code URL: {qr_code_url[:80]}..." if qr_code_url else "None")
    print(f"   Backup Codes Count: {len(backup_codes) if backup_codes else 0}")
    
    if backup_codes:
        print(f"   First 3 Backup Codes: {backup_codes[:3]}")
    
    # Validate secret format
    if secret and len(secret) == 32:
        print(f"   ✅ Secret format valid (32 characters)")
    else:
        print(f"   ❌ Secret format invalid")
    
    # Validate QR code
    if qr_code_url and qr_code_url.startswith('data:image/png;base64,'):
        print(f"   ✅ QR code format valid (base64 PNG)")
    else:
        print(f"   ❌ QR code format invalid")
    
    # Validate backup codes
    if backup_codes and len(backup_codes) == 10:
        print(f"   ✅ Backup codes count valid (10 codes)")
    else:
        print(f"   ❌ Backup codes count invalid")
else:
    print(f"   ❌ MFA setup failed: {setup_response.text}")
    exit(1)

print()
print("=" * 60)

# Test 3: Try to setup MFA again (should return new codes)
print("Test 3: Setup MFA again (regenerate)")
print("-" * 60)
print("3.1. Calling POST /auth/mfa/setup again...")

setup2_response = requests.post(f"{BASE_URL}/auth/mfa/setup", headers=headers)

print(f"   Status Code: {setup2_response.status_code}")
if setup2_response.status_code == 200:
    setup2_data = setup2_response.json()
    secret2 = setup2_data.get('secret')
    
    if secret2 != secret:
        print(f"   ✅ New secret generated (regeneration working)")
        print(f"   New Secret: {secret2}")
        # Use the latest secret for verification
        secret = secret2
        backup_codes = setup2_data.get('backup_codes')
    else:
        print(f"   ℹ️  Same secret returned")
else:
    print(f"   Response: {setup2_response.text}")

print()
print("=" * 60)

# Test 4: Try to enable MFA without verification code
print("Test 4: Try to enable MFA without valid code")
print("-" * 60)
print("4.1. Calling POST /auth/mfa/enable with invalid code...")

invalid_enable = requests.post(
    f"{BASE_URL}/auth/mfa/enable",
    headers=headers,
    json={
        "verification_code": "000000"
    }
)

print(f"   Status Code: {invalid_enable.status_code}")
if invalid_enable.status_code == 400:
    print(f"   ✅ Correctly rejected: {invalid_enable.json()}")
else:
    print(f"   Response: {invalid_enable.text}")

print()
print("=" * 60)

# Test 5: Enable MFA with valid TOTP code
print("Test 5: Enable MFA with valid TOTP code")
print("-" * 60)
print("5.1. Generating valid TOTP code...")

totp = pyotp.TOTP(secret)
valid_code = totp.now()
print(f"   Generated Code: {valid_code}")

print()
print("5.2. Calling POST /auth/mfa/enable with valid code...")

enable_response = requests.post(
    f"{BASE_URL}/auth/mfa/enable",
    headers=headers,
    json={
        "verification_code": valid_code
    }
)

print(f"   Status Code: {enable_response.status_code}")
if enable_response.status_code == 200:
    enable_data = enable_response.json()
    print(f"   ✅ MFA enabled successfully!")
    print(f"   Message: {enable_data.get('message')}")
else:
    print(f"   ❌ MFA enable failed: {enable_response.text}")

print()
print("=" * 60)

# Test 6: Check MFA status after enabling
print("Test 6: Check MFA status after enabling")
print("-" * 60)
print("6.1. Calling GET /auth/mfa/status...")

status2_response = requests.get(f"{BASE_URL}/auth/mfa/status", headers=headers)

print(f"   Status Code: {status2_response.status_code}")
if status2_response.status_code == 200:
    status2_data = status2_response.json()
    print(f"   ✅ MFA Status retrieved!")
    print(f"   Enabled: {status2_data.get('mfa_enabled')}")
    print(f"   Enabled At: {status2_data.get('mfa_enabled_at')}")
    print(f"   Backup Codes Available: {status2_data.get('backup_codes_remaining')}")
    
    if status2_data.get('mfa_enabled'):
        print(f"   ✅ MFA correctly showing as enabled")
else:
    print(f"   Response: {status2_response.text}")

print()
print("=" * 60)

# Test 7: Try to setup MFA without authentication
print("Test 7: Try to setup MFA without authentication")
print("-" * 60)
print("7.1. Calling POST /auth/mfa/setup without Authorization header...")

no_auth_setup = requests.post(f"{BASE_URL}/auth/mfa/setup")

print(f"   Status Code: {no_auth_setup.status_code}")
if no_auth_setup.status_code == 401:
    print(f"   ✅ Correctly rejected: {no_auth_setup.json()}")
else:
    print(f"   Response: {no_auth_setup.text}")

print()
print("=" * 60)

# Test 8: Test login with MFA required
print("Test 8: Login with MFA enabled (requires MFA verification)")
print("-" * 60)
print("8.1. Attempting login...")

mfa_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": test_password
    }
)

print(f"   Status Code: {mfa_login.status_code}")
if mfa_login.status_code == 200:
    mfa_login_data = mfa_login.json()
    if mfa_login_data.get('requires_mfa'):
        print(f"   ✅ Login requires MFA verification")
        print(f"   Requires MFA: {mfa_login_data.get('requires_mfa')}")
        print(f"   MFA Enabled: {mfa_login_data.get('mfa_enabled')}")
        
        # Note: In a real flow, user would be redirected to MFA verification
        # The temp_token would be used to verify MFA code
    else:
        print(f"   ⚠️  Login succeeded without MFA (might have temp token)")
else:
    print(f"   Response: {mfa_login.text}")

print()
print("=" * 60)

# Test 9: Disable MFA (cleanup)
print("Test 9: Disable MFA (cleanup)")
print("-" * 60)
print("9.1. Calling POST /auth/mfa/disable...")

disable_response = requests.post(
    f"{BASE_URL}/auth/mfa/disable",
    headers=headers,
    json={
        "password": test_password
    }
)

print(f"   Status Code: {disable_response.status_code}")
if disable_response.status_code == 200:
    disable_data = disable_response.json()
    print(f"   ✅ MFA disabled successfully!")
    print(f"   Message: {disable_data.get('message')}")
    
    # Verify MFA is disabled
    print()
    print("9.2. Verifying MFA is disabled...")
    status3_response = requests.get(f"{BASE_URL}/auth/mfa/status", headers=headers)
    if status3_response.status_code == 200:
        status3_data = status3_response.json()
        if not status3_data.get('enabled'):
            print(f"   ✅ MFA correctly disabled")
        else:
            print(f"   ❌ MFA still showing as enabled")
else:
    print(f"   ❌ MFA disable failed: {disable_response.text}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
print()
print(f"Secret used: {secret}")
print(f"Backup codes generated: {len(backup_codes) if backup_codes else 0}")
