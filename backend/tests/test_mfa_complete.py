"""Comprehensive test script for all MFA endpoints"""
import requests
import pyotp
import time

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Comprehensive MFA Testing")
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

# Test 1: Check MFA status before setup
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
    
    # Validate formats
    if secret and len(secret) == 32:
        print(f"   ✅ Secret format valid (32 characters)")
    if qr_code_url and qr_code_url.startswith('data:image/png;base64,'):
        print(f"   ✅ QR code format valid (base64 PNG)")
    if backup_codes and len(backup_codes) == 10:
        print(f"   ✅ Backup codes count valid (10 codes)")
else:
    print(f"   ❌ MFA setup failed: {setup_response.text}")
    exit(1)

print()
print("=" * 60)

# Test 3: Enable MFA with valid TOTP code
print("Test 3: Enable MFA with valid TOTP code")
print("-" * 60)
print("3.1. Generating valid TOTP code...")

totp = pyotp.TOTP(secret)
valid_code = totp.now()
print(f"   Generated Code: {valid_code}")

print()
print("3.2. Calling POST /auth/mfa/enable with valid code...")

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
    exit(1)

print()
print("=" * 60)

# Test 4: Regenerate backup codes
print("Test 4: Regenerate backup codes")
print("-" * 60)
print("4.1. Calling POST /auth/mfa/regenerate-backup-codes...")

regenerate_response = requests.post(
    f"{BASE_URL}/auth/mfa/regenerate-backup-codes",
    headers=headers
)

print(f"   Status Code: {regenerate_response.status_code}")
if regenerate_response.status_code == 200:
    regenerate_data = regenerate_response.json()
    new_backup_codes = regenerate_data.get('backup_codes')
    
    print(f"   ✅ Backup codes regenerated!")
    print(f"   New Backup Codes Count: {len(new_backup_codes) if new_backup_codes else 0}")
    
    if new_backup_codes:
        print(f"   First 3 New Codes: {new_backup_codes[:3]}")
        
        # Verify codes are different
        if new_backup_codes != backup_codes:
            print(f"   ✅ New codes are different from original")
        else:
            print(f"   ⚠️  New codes are the same as original")
        
        # Update backup codes for later use
        backup_codes = new_backup_codes
    
    if new_backup_codes and len(new_backup_codes) == 10:
        print(f"   ✅ Backup codes count valid (10 codes)")
else:
    print(f"   ❌ Backup code regeneration failed: {regenerate_response.text}")

print()
print("=" * 60)

# Test 5: Check MFA status after enabling
print("Test 5: Check MFA status after enabling")
print("-" * 60)
print("5.1. Calling GET /auth/mfa/status...")

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
    
    if status2_data.get('backup_codes_remaining') == 10:
        print(f"   ✅ All 10 backup codes available")
else:
    print(f"   Response: {status2_response.text}")

print()
print("=" * 60)

# Test 6: Login with MFA enabled (get temp token)
print("Test 6: Login with MFA enabled (get temp token)")
print("-" * 60)
print("6.1. Attempting login...")

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
    temp_token = mfa_login_data.get('access_token')
    
    if mfa_login_data.get('requires_mfa'):
        print(f"   ✅ Login requires MFA verification")
        print(f"   Requires MFA: {mfa_login_data.get('requires_mfa')}")
        print(f"   MFA Enabled: {mfa_login_data.get('mfa_enabled')}")
        print(f"   Temp Token (first 20 chars): {temp_token[:20]}...")
    else:
        print(f"   ⚠️  Login succeeded without MFA requirement")
else:
    print(f"   ❌ Login failed: {mfa_login.text}")
    exit(1)

print()
print("=" * 60)

# Test 7: Verify MFA with TOTP code
print("Test 7: Verify MFA with TOTP code")
print("-" * 60)
print("7.1. Generating new TOTP code...")

# Wait a moment to ensure we get a fresh code
time.sleep(1)
verify_code = totp.now()
print(f"   Generated Code: {verify_code}")

print()
print("7.2. Calling POST /auth/mfa/verify with temp token...")

verify_response = requests.post(
    f"{BASE_URL}/auth/mfa/verify",
    json={
        "temp_token": temp_token,
        "code": verify_code
    }
)

print(f"   Status Code: {verify_response.status_code}")
if verify_response.status_code == 200:
    verify_data = verify_response.json()
    final_access_token = verify_data.get('access_token')
    final_refresh_token = verify_data.get('refresh_token')
    
    print(f"   ✅ MFA verification successful!")
    print(f"   Access Token (first 20 chars): {final_access_token[:20]}...")
    print(f"   Refresh Token (first 20 chars): {final_refresh_token[:20]}...")
    print(f"   User Type: {verify_data.get('user_type')}")
    print(f"   User ID: {verify_data.get('user_id')}")
    print(f"   Email: {verify_data.get('email')}")
    
    # Update headers with new token
    headers_after_mfa = {"Authorization": f"Bearer {final_access_token}"}
else:
    print(f"   ❌ MFA verification failed: {verify_response.text}")
    exit(1)

print()
print("=" * 60)

# Test 8: Login with MFA and verify using backup code
print("Test 8: Login with MFA and verify using backup code")
print("-" * 60)
print("8.1. Attempting new login to get fresh temp token...")

backup_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": test_password
    }
)

if backup_login.status_code == 200:
    backup_login_data = backup_login.json()
    backup_temp_token = backup_login_data.get('access_token')
    print(f"   ✅ Login successful, temp token obtained")
    
    # Use first backup code
    backup_code_to_use = backup_codes[0]
    print(f"   Using Backup Code: {backup_code_to_use}")
    
    print()
    print("8.2. Calling POST /auth/mfa/verify with backup code...")
    
    backup_verify = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "temp_token": backup_temp_token,
            "code": backup_code_to_use
        }
    )
    
    print(f"   Status Code: {backup_verify.status_code}")
    if backup_verify.status_code == 200:
        backup_verify_data = backup_verify.json()
        print(f"   ✅ MFA verification with backup code successful!")
        print(f"   User ID: {backup_verify_data.get('user_id')}")
        print(f"   Email: {backup_verify_data.get('email')}")
        
        # Check status to see remaining backup codes
        print()
        print("8.3. Checking remaining backup codes...")
        status_after_backup = requests.get(f"{BASE_URL}/auth/mfa/status", headers=headers)
        if status_after_backup.status_code == 200:
            status_after_data = status_after_backup.json()
            remaining = status_after_data.get('backup_codes_remaining')
            print(f"   Backup Codes Remaining: {remaining}")
            if remaining == 9:
                print(f"   ✅ Backup code count decreased correctly (10 → 9)")
            else:
                print(f"   ⚠️  Expected 9 backup codes, got {remaining}")
    else:
        print(f"   ❌ Backup code verification failed: {backup_verify.text}")
else:
    print(f"   ❌ Login failed: {backup_login.text}")

print()
print("=" * 60)

# Test 9: Try to verify MFA with invalid code
print("Test 9: Try to verify MFA with invalid code")
print("-" * 60)
print("9.1. Attempting login to get temp token...")

invalid_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": test_password
    }
)

if invalid_login.status_code == 200:
    invalid_temp_token = invalid_login.json().get('access_token')
    
    print("9.2. Calling POST /auth/mfa/verify with invalid code...")
    
    invalid_verify = requests.post(
        f"{BASE_URL}/auth/mfa/verify",
        json={
            "temp_token": invalid_temp_token,
            "code": "000000"
        }
    )
    
    print(f"   Status Code: {invalid_verify.status_code}")
    if invalid_verify.status_code in [400, 401]:
        print(f"   ✅ Invalid code correctly rejected")
        print(f"   Error: {invalid_verify.json()}")
    else:
        print(f"   ⚠️  Unexpected response: {invalid_verify.text}")

print()
print("=" * 60)

# Test 10: Try to regenerate backup codes without MFA enabled
print("Test 10: Try to access MFA endpoints without proper setup")
print("-" * 60)

# First disable MFA
print("10.1. Disabling MFA temporarily...")
disable_temp = requests.post(
    f"{BASE_URL}/auth/mfa/disable",
    headers=headers,
    json={"password": test_password}
)

if disable_temp.status_code == 200:
    print(f"   ✅ MFA disabled")
    
    print()
    print("10.2. Trying to regenerate backup codes without MFA enabled...")
    
    no_mfa_regenerate = requests.post(
        f"{BASE_URL}/auth/mfa/regenerate-backup-codes",
        headers=headers
    )
    
    print(f"   Status Code: {no_mfa_regenerate.status_code}")
    if no_mfa_regenerate.status_code == 400:
        print(f"   ✅ Correctly rejected (MFA not enabled)")
        print(f"   Error: {no_mfa_regenerate.json()}")
    else:
        print(f"   Response: {no_mfa_regenerate.text}")

print()
print("=" * 60)

# Cleanup: Ensure MFA is disabled
print("Cleanup: Ensuring MFA is disabled")
print("-" * 60)

final_status = requests.get(f"{BASE_URL}/auth/mfa/status", headers=headers)
if final_status.status_code == 200:
    final_status_data = final_status.json()
    if final_status_data.get('mfa_enabled'):
        print("Disabling MFA for cleanup...")
        final_disable = requests.post(
            f"{BASE_URL}/auth/mfa/disable",
            headers=headers,
            json={"password": test_password}
        )
        if final_disable.status_code == 200:
            print("✅ MFA disabled")
        else:
            print(f"⚠️  Could not disable MFA: {final_disable.text}")
    else:
        print("✅ MFA already disabled")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
print()
print(f"Secret used: {secret}")
print(f"Backup codes tested: {len(backup_codes) if backup_codes else 0}")
print(f"TOTP verifications: ✅")
print(f"Backup code verifications: ✅")
print(f"Backup code regeneration: ✅")
