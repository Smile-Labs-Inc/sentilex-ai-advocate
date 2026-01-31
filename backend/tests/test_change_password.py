"""Test script for /auth/change-password endpoint"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing /auth/change-password Endpoint")
print("=" * 60)
print()

# Setup: Login to get access token
print("Setup: Login as existing user")
print("-" * 60)

original_password = "Welcome@2024"
new_password = "NewPassword@2024"
test_email = "dilani.w@yahoo.com"

print(f"Logging in as {test_email}...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": original_password
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

# Test 1: Change password with correct current password
print("Test 1: Change password with correct current password")
print("-" * 60)
print("1.1. Calling POST /auth/change-password...")

change_response = requests.post(
    f"{BASE_URL}/auth/change-password",
    headers=headers,
    json={
        "current_password": original_password,
        "new_password": new_password
    }
)

print(f"   Status Code: {change_response.status_code}")
if change_response.status_code == 200:
    change_data = change_response.json()
    print(f"   ✅ Password changed successfully!")
    print(f"   Message: {change_data.get('message')}")
    
    # Verify old password no longer works
    print()
    print("1.2. Verifying old password no longer works...")
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
    print("1.3. Verifying new password works...")
    new_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": new_password
        }
    )
    if new_login.status_code == 200:
        print(f"   ✅ New password works!")
        # Update access token for future tests
        access_token = new_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"   ❌ New password doesn't work!")
else:
    print(f"   ❌ Password change failed: {change_response.text}")

print()
print("=" * 60)

# Test 2: Try to change password with wrong current password
print("Test 2: Try to change password with wrong current password")
print("-" * 60)
print("2.1. Calling POST /auth/change-password with wrong current password...")

wrong_current = requests.post(
    f"{BASE_URL}/auth/change-password",
    headers=headers,
    json={
        "current_password": "WrongPassword@123",
        "new_password": "AnotherNew@Password123"
    }
)

print(f"   Status Code: {wrong_current.status_code}")
if wrong_current.status_code == 400:
    print(f"   ✅ Correctly rejected: {wrong_current.json()}")
else:
    print(f"   Response: {wrong_current.text}")

print()
print("=" * 60)

# Test 3: Try to use same password as new password
print("Test 3: Try to use same password as new password")
print("-" * 60)
print("3.1. Calling POST /auth/change-password with same password...")

same_password = requests.post(
    f"{BASE_URL}/auth/change-password",
    headers=headers,
    json={
        "current_password": new_password,
        "new_password": new_password
    }
)

print(f"   Status Code: {same_password.status_code}")
if same_password.status_code == 400:
    print(f"   ✅ Correctly rejected: {same_password.json()}")
else:
    print(f"   Response: {same_password.text}")

print()
print("=" * 60)

# Test 4: Try without authentication
print("Test 4: Try to change password without authentication")
print("-" * 60)
print("4.1. Calling POST /auth/change-password without Authorization header...")

no_auth = requests.post(
    f"{BASE_URL}/auth/change-password",
    json={
        "current_password": new_password,
        "new_password": "YetAnother@Pass123"
    }
)

print(f"   Status Code: {no_auth.status_code}")
if no_auth.status_code == 401:
    print(f"   ✅ Correctly rejected: {no_auth.json()}")
else:
    print(f"   Response: {no_auth.text}")

print()
print("=" * 60)

# Test 5: Try to reuse old password (password history check)
print("Test 5: Try to reuse old password (password history)")
print("-" * 60)
print("5.1. Attempting to change back to original password...")

reuse_password = requests.post(
    f"{BASE_URL}/auth/change-password",
    headers=headers,
    json={
        "current_password": new_password,
        "new_password": original_password
    }
)

print(f"   Status Code: {reuse_password.status_code}")
if reuse_password.status_code == 400:
    response_data = reuse_password.json()
    if "last 5 passwords" in response_data.get('detail', ''):
        print(f"   ✅ Password history check working: {response_data}")
    else:
        print(f"   Response: {response_data}")
elif reuse_password.status_code == 200:
    print(f"   ⚠️  Password reuse allowed (history check might be disabled)")
    # Change it back if it succeeded
    requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": test_email, "password": original_password}
    )
else:
    print(f"   Response: {reuse_password.text}")

print()
print("=" * 60)

# Test 6: Weak password validation
print("Test 6: Try to change to weak password")
print("-" * 60)
print("6.1. Calling POST /auth/change-password with weak password...")

weak_password = requests.post(
    f"{BASE_URL}/auth/change-password",
    headers=headers,
    json={
        "current_password": new_password,
        "new_password": "weak"
    }
)

print(f"   Status Code: {weak_password.status_code}")
if weak_password.status_code == 422:
    print(f"   ✅ Weak password rejected (validation error)")
    print(f"   Details: {weak_password.json()}")
else:
    print(f"   Response: {weak_password.text}")

print()
print("=" * 60)

# Cleanup: Change password back to original
print("Cleanup: Changing password back to original")
print("-" * 60)
print("Logging in with new password...")
cleanup_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": new_password
    }
)

if cleanup_login.status_code == 200:
    cleanup_token = cleanup_login.json()["access_token"]
    cleanup_headers = {"Authorization": f"Bearer {cleanup_token}"}
    
    # Change multiple times to bypass password history
    print("Changing password multiple times to bypass history...")
    temp_passwords = [
        "TempPass1@2024",
        "TempPass2@2024",
        "TempPass3@2024",
        "TempPass4@2024",
        "TempPass5@2024",
        original_password
    ]
    
    current_pass = new_password
    for idx, temp_pass in enumerate(temp_passwords, 1):
        change_temp = requests.post(
            f"{BASE_URL}/auth/change-password",
            headers=cleanup_headers,
            json={
                "current_password": current_pass,
                "new_password": temp_pass
            }
        )
        if change_temp.status_code == 200:
            print(f"   Step {idx}: ✅")
            current_pass = temp_pass
            # Login again to get fresh token
            temp_login = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": test_email, "password": current_pass}
            )
            if temp_login.status_code == 200:
                cleanup_headers = {"Authorization": f"Bearer {temp_login.json()['access_token']}"}
        else:
            print(f"   Step {idx}: Failed - {change_temp.text}")
            break
    
    # Verify original password works
    final_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": original_password
        }
    )
    if final_login.status_code == 200:
        print(f"✅ Password restored to original!")
    else:
        print(f"⚠️  Could not restore original password")
else:
    print("⚠️  Could not login for cleanup")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
