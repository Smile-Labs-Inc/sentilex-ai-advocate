"""Test script for lawyer password management endpoints"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Lawyer Password Management")
print("=" * 60)
print()

# Setup: Login
test_email = "nimal.silva@lawfirm.lk"
test_password = "LawyerPass@2024"

print("Setup: Login as existing lawyer")
print("-" * 60)
print(f"Logging in as {test_email}...")

login_response = requests.post(
    f"{BASE_URL}/lawyers/login",
    json={"email": test_email, "password": test_password}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

access_token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
print("✅ Login successful!")
print()

print("=" * 60)

# Test 1: Change password with correct old password
print("Test 1: Change password (POST /lawyers/change-password)")
print("-" * 60)
print("1.1. Changing password...")

new_password = "NewLawyerPass@2024"

change_response = requests.post(
    f"{BASE_URL}/lawyers/change-password",
    headers=headers,
    json={
        "current_password": test_password,
        "new_password": new_password
    }
)

print(f"   Status Code: {change_response.status_code}")
if change_response.status_code == 200:
    print(f"   ✅ Password changed successfully!")
    print(f"   Message: {change_response.json().get('message')}")
    
    # Verify new password works
    print()
    print("1.2. Verifying new password works...")
    verify_login = requests.post(
        f"{BASE_URL}/lawyers/login",
        json={"email": test_email, "password": new_password}
    )
    
    if verify_login.status_code == 200:
        print(f"   ✅ New password works!")
        # Update headers with new token
        access_token = verify_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"   ❌ New password doesn't work")
else:
    print(f"   ❌ Failed: {change_response.text}")
    # Don't exit, continue with other tests

print()
print("=" * 60)

# Test 2: Try to change password with wrong old password
print("Test 2: Try to change password with wrong old password")
print("-" * 60)
print("2.1. Attempting change with wrong old password...")

wrong_old_response = requests.post(
    f"{BASE_URL}/lawyers/change-password",
    headers=headers,
    json={
        "current_password": "WrongPassword123",
        "new_password": "AnotherNewPass@2024"
    }
)

print(f"   Status Code: {wrong_old_response.status_code}")
if wrong_old_response.status_code == 400:
    print(f"   ✅ Correctly rejected wrong old password")
    print(f"   Error: {wrong_old_response.json()}")
else:
    print(f"   Response: {wrong_old_response.text}")

print()
print("=" * 60)

# Test 3: Try to change password with weak new password
print("Test 3: Try to change password with weak new password")
print("-" * 60)
print("3.1. Attempting change with weak password...")

weak_password_response = requests.post(
    f"{BASE_URL}/lawyers/change-password",
    headers=headers,
    json={
        "current_password": new_password,
        "new_password": "weak"
    }
)

print(f"   Status Code: {weak_password_response.status_code}")
if weak_password_response.status_code == 422:
    print(f"   ✅ Correctly rejected weak password")
    print(f"   Validation Error: {weak_password_response.json()}")
else:
    print(f"   Response: {weak_password_response.text}")

print()
print("=" * 60)

# Test 4: Forgot password request
print("Test 4: Forgot password (POST /lawyers/forgot-password)")
print("-" * 60)
print("4.1. Requesting password reset...")

forgot_response = requests.post(
    f"{BASE_URL}/lawyers/forgot-password",
    json={"email": test_email}
)

print(f"   Status Code: {forgot_response.status_code}")
if forgot_response.status_code == 200:
    print(f"   ✅ Password reset email sent!")
    print(f"   Message: {forgot_response.json().get('message')}")
else:
    print(f"   ❌ Failed: {forgot_response.text}")

print()
print("=" * 60)

# Test 5: Forgot password with non-existent email
print("Test 5: Forgot password with non-existent email")
print("-" * 60)
print("5.1. Requesting reset for non-existent email...")

nonexistent_forgot = requests.post(
    f"{BASE_URL}/lawyers/forgot-password",
    json={"email": "nonexistent.lawyer@example.com"}
)

print(f"   Status Code: {nonexistent_forgot.status_code}")
# Should return 200 to prevent email enumeration
if nonexistent_forgot.status_code == 200:
    print(f"   ✅ Returns success (prevents email enumeration)")
    print(f"   Message: {nonexistent_forgot.json().get('message')}")
else:
    print(f"   Response: {nonexistent_forgot.text}")

print()
print("=" * 60)

# Test 6: Try to change password without authentication
print("Test 6: Try to change password without authentication")
print("-" * 60)
print("6.1. Calling POST /lawyers/change-password without auth...")

no_auth_change = requests.post(
    f"{BASE_URL}/lawyers/change-password",
    json={
        "current_password": "something",
        "new_password": "NewPassword@2024"
    }
)

print(f"   Status Code: {no_auth_change.status_code}")
if no_auth_change.status_code == 401:
    print(f"   ✅ Correctly rejected unauthenticated request")
    print(f"   Error: {no_auth_change.json()}")
else:
    print(f"   Response: {no_auth_change.text}")

print()
print("=" * 60)

# Test 7: Try to reuse old password (password history check)
print("Test 7: Try to reuse old password (password history)")
print("-" * 60)
print("7.1. Attempting to change back to old password...")

reuse_response = requests.post(
    f"{BASE_URL}/lawyers/change-password",
    headers=headers,
    json={
        "current_password": new_password,
        "new_password": test_password  # Original password
    }
)

print(f"   Status Code: {reuse_response.status_code}")
if reuse_response.status_code == 400:
    print(f"   ✅ Correctly prevented password reuse")
    print(f"   Error: {reuse_response.json()}")
elif reuse_response.status_code == 200:
    print(f"   ⚠️  Password reuse was allowed (history check may not be enabled)")
else:
    print(f"   Response: {reuse_response.text}")

print()
print("=" * 60)

# Restore original password
print("Cleanup: Restoring original password")
print("-" * 60)

restore_response = requests.post(
    f"{BASE_URL}/lawyers/change-password",
    headers=headers,
    json={
        "current_password": new_password,
        "new_password": "TempPassword@2026"
    }
)

if restore_response.status_code == 200:
    # Login with temp password
    temp_login = requests.post(
        f"{BASE_URL}/lawyers/login",
        json={"email": test_email, "password": "TempPassword@2026"}
    )
    if temp_login.status_code == 200:
        temp_token = temp_login.json()["access_token"]
        temp_headers = {"Authorization": f"Bearer {temp_token}"}
        
        # Now change to original
        final_restore = requests.post(
            f"{BASE_URL}/lawyers/change-password",
            headers=temp_headers,
            json={
                "current_password": "TempPassword@2026",
                "new_password": test_password
            }
        )
        if final_restore.status_code == 200:
            print("✅ Original password restored")
        else:
            print(f"⚠️  Could not restore original password: {final_restore.text}")
else:
    print(f"⚠️  Could not start password restore: {restore_response.text}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
