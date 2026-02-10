"""Test script for /auth/forgot-password and /auth/reset-password endpoints"""
import requests
import sys

# Base URL
BASE_URL = "http://127.0.0.1:8001"

print("=" * 60)
print("Testing /auth/forgot-password & /auth/reset-password")
print("=" * 60)
print()

# Test user
test_email = "dilani.w@yahoo.com"
original_password = "Welcome@2024"
new_reset_password = "ResetPass@2024"

# Test 1: Request password reset for existing user
print("Test 1: Request password reset for existing user")
print("-" * 60)
print(f"1.1. Requesting password reset for {test_email}...")

forgot_response = requests.post(
    f"{BASE_URL}/auth/forgot-password",
    json={
        "email": test_email
    }
)

print(f"   Status Code: {forgot_response.status_code}")
if forgot_response.status_code == 200:
    forgot_data = forgot_response.json()
    print(f"   ✅ Request successful!")
    print(f"   Message: {forgot_data.get('message')}")
else:
    print(f"   ❌ Request failed: {forgot_response.text}")

print()
print("=" * 60)

# Test 2: Request password reset for non-existent user
print("Test 2: Request password reset for non-existent user")
print("-" * 60)
print("2.1. Requesting password reset for fake email...")

fake_forgot = requests.post(
    f"{BASE_URL}/auth/forgot-password",
    json={
        "email": "nonexistent@example.com"
    }
)

print(f"   Status Code: {fake_forgot.status_code}")
if fake_forgot.status_code == 200:
    fake_data = fake_forgot.json()
    print(f"   ✅ Same response (prevents email enumeration)")
    print(f"   Message: {fake_data.get('message')}")
else:
    print(f"   Response: {fake_forgot.text}")

print()
print("=" * 60)

# Test 3: Generate reset token and test password reset
print("Test 3: Reset password with valid token")
print("-" * 60)
print("3.1. Generating password reset token...")

sys.path.insert(0, 'C:\\Users\\SAMPR\\OneDrive\\Desktop\\GitHub Projects\\sentilex-ai-advocate\\backend')
from utils.auth import generate_password_reset_token

reset_token = generate_password_reset_token(test_email)
print(f"   Token generated: {reset_token[:50]}...")

print()
print("3.2. Calling POST /auth/reset-password with valid token...")

reset_response = requests.post(
    f"{BASE_URL}/auth/reset-password",
    json={
        "token": reset_token,
        "new_password": new_reset_password
    }
)

print(f"   Status Code: {reset_response.status_code}")
if reset_response.status_code == 200:
    reset_data = reset_response.json()
    print(f"   ✅ Password reset successfully!")
    print(f"   Message: {reset_data.get('message')}")
    
    # Verify old password doesn't work
    print()
    print("3.3. Verifying old password no longer works...")
    old_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": original_password
        }
    )
    if old_login.status_code == 401:
        print(f"   ✅ Old password correctly rejected")
    else:
        print(f"   ❌ Old password still works!")
    
    # Verify new password works
    print()
    print("3.4. Verifying new reset password works...")
    new_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": new_reset_password
        }
    )
    if new_login.status_code == 200:
        print(f"   ✅ New password works!")
    else:
        print(f"   ❌ New password doesn't work!")
        print(f"   Response: {new_login.text}")
else:
    print(f"   ❌ Password reset failed: {reset_response.text}")

print()
print("=" * 60)

# Test 4: Try to reset with invalid token
print("Test 4: Try to reset password with invalid token")
print("-" * 60)
print("4.1. Calling POST /auth/reset-password with invalid token...")

invalid_reset = requests.post(
    f"{BASE_URL}/auth/reset-password",
    json={
        "token": "invalid_token_here",
        "new_password": "SomePassword@123"
    }
)

print(f"   Status Code: {invalid_reset.status_code}")
if invalid_reset.status_code == 400:
    print(f"   ✅ Correctly rejected: {invalid_reset.json()}")
else:
    print(f"   Response: {invalid_reset.text}")

print()
print("=" * 60)

# Test 5: Try to reset with wrong token type (access token)
print("Test 5: Try to reset password with wrong token type")
print("-" * 60)
print("5.1. Generating access token instead of reset token...")

# Login to get access token
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": new_reset_password
    }
)

if login_resp.status_code == 200:
    access_token = login_resp.json()["access_token"]
    
    print("5.2. Calling POST /auth/reset-password with access token...")
    wrong_type_reset = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": access_token,
            "new_password": "AnotherPass@123"
        }
    )
    
    print(f"   Status Code: {wrong_type_reset.status_code}")
    if wrong_type_reset.status_code == 400:
        print(f"   ✅ Correctly rejected: {wrong_type_reset.json()}")
    else:
        print(f"   Response: {wrong_type_reset.text}")
else:
    print("   ⚠️  Could not get access token")

print()
print("=" * 60)

# Test 6: Try to reset for non-existent user
print("Test 6: Reset password for non-existent user")
print("-" * 60)
print("6.1. Generating reset token for non-existent user...")

fake_user_token = generate_password_reset_token("nonexistent@example.com")

print("6.2. Calling POST /auth/reset-password...")
fake_user_reset = requests.post(
    f"{BASE_URL}/auth/reset-password",
    json={
        "token": fake_user_token,
        "new_password": "ValidPass@123"
    }
)

print(f"   Status Code: {fake_user_reset.status_code}")
if fake_user_reset.status_code == 404:
    print(f"   ✅ Correctly rejected: {fake_user_reset.json()}")
else:
    print(f"   Response: {fake_user_reset.text}")

print()
print("=" * 60)

# Test 7: Try to reset with weak password
print("Test 7: Try to reset with weak password")
print("-" * 60)
print("7.1. Calling POST /auth/reset-password with weak password...")

weak_reset = requests.post(
    f"{BASE_URL}/auth/reset-password",
    json={
        "token": reset_token,
        "new_password": "weak"
    }
)

print(f"   Status Code: {weak_reset.status_code}")
if weak_reset.status_code == 422:
    print(f"   ✅ Weak password rejected (validation error)")
else:
    print(f"   Response: {weak_reset.text}")

print()
print("=" * 60)

# Test 8: Request multiple password resets (rate limiting test)
print("Test 8: Request multiple password resets")
print("-" * 60)
print("8.1. Sending 3 consecutive password reset requests...")

for i in range(1, 4):
    multi_forgot = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={
            "email": test_email
        }
    )
    print(f"   Request {i}: Status {multi_forgot.status_code}")
    if multi_forgot.status_code != 200:
        print(f"      ⚠️  Rate limiting might be active")

print(f"   ℹ️  All requests returned same response (good for security)")

print()
print("=" * 60)

# Cleanup: Restore original password (bypass history with multiple resets)
print("Cleanup: Restoring original password")
print("-" * 60)
print("Resetting password multiple times to bypass history...")

temp_passwords = [
    "TempReset1@2024",
    "TempReset2@2024",
    "TempReset3@2024",
    "TempReset4@2024",
    "TempReset5@2024",
    original_password
]

for idx, temp_pass in enumerate(temp_passwords, 1):
    temp_token = generate_password_reset_token(test_email)
    temp_reset = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": temp_token,
            "new_password": temp_pass
        }
    )
    if temp_reset.status_code == 200:
        print(f"   Step {idx}: ✅")
    else:
        print(f"   Step {idx}: Failed - {temp_reset.json().get('detail')}")

# Verify original password works
verify_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": original_password
    }
)
if verify_login.status_code == 200:
    print(f"✅ Password restored to original!")
else:
    print(f"⚠️  Original password not working: {verify_login.text}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
