"""Test script for /auth/me endpoint"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing /auth/me Endpoint")
print("=" * 60)
print()

# Test 1: Get user profile with valid token
print("Test 1: Get user profile with valid access token")
print("-" * 60)

# Login first to get access token
print("1.1. Logging in as Dilani Wijesinghe...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dilani.w@yahoo.com",
        "password": "Welcome@2024"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()
access_token = login_data["access_token"]
print(f"   ✅ Login successful!")
print()

# Call /auth/me endpoint
print("1.2. Calling GET /auth/me...")
headers = {"Authorization": f"Bearer {access_token}"}
me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

print(f"   Status Code: {me_response.status_code}")
if me_response.status_code == 200:
    user_data = me_response.json()
    print(f"   ✅ Profile retrieved successfully!")
    print()
    print("   User Profile:")
    print(f"      ID: {user_data.get('id')}")
    print(f"      Name: {user_data.get('first_name')} {user_data.get('last_name')}")
    print(f"      Email: {user_data.get('email')}")
    print(f"      Role: {user_data.get('role')}")
    print(f"      Active: {user_data.get('is_active')}")
    print(f"      Email Verified: {user_data.get('email_verified')}")
    print(f"      MFA Enabled: {user_data.get('mfa_enabled')}")
    print(f"      Language: {user_data.get('preferred_language')}")
    print(f"      District: {user_data.get('district')}")
    print(f"      Last Login: {user_data.get('last_login_at')}")
    print()
    
    # Validate expected data
    print("   Validating response data...")
    assert user_data.get('email') == 'dilani.w@yahoo.com', "Email mismatch"
    assert user_data.get('first_name') == 'Dilani', "First name mismatch"
    assert user_data.get('last_name') == 'Wijesinghe', "Last name mismatch"
    assert user_data.get('role') == 'user', "Role mismatch"
    assert user_data.get('is_active') == True, "User should be active"
    assert user_data.get('preferred_language') == 'en', "Language mismatch"
    assert user_data.get('district') == 'Galle', "District mismatch"
    print("   ✅ All validations passed!")
else:
    print(f"   ❌ Failed to get profile: {me_response.text}")

print()
print("=" * 60)

# Test 2: Try without authentication
print("Test 2: Call /auth/me without access token")
print("-" * 60)
print("2.1. Calling GET /auth/me without Authorization header...")
no_auth_response = requests.get(f"{BASE_URL}/auth/me")

print(f"   Status Code: {no_auth_response.status_code}")
if no_auth_response.status_code == 401:
    print(f"   ✅ Correctly rejected: {no_auth_response.json()}")
else:
    print(f"   ❌ Should return 401 Unauthorized")

print()
print("=" * 60)

# Test 3: Try with invalid token
print("Test 3: Call /auth/me with invalid access token")
print("-" * 60)
print("3.1. Calling GET /auth/me with fake token...")
invalid_headers = {"Authorization": "Bearer invalid_token_here"}
invalid_response = requests.get(f"{BASE_URL}/auth/me", headers=invalid_headers)

print(f"   Status Code: {invalid_response.status_code}")
if invalid_response.status_code == 401:
    print(f"   ✅ Correctly rejected: {invalid_response.json()}")
else:
    print(f"   ❌ Should return 401 Unauthorized")

print()
print("=" * 60)

# Test 4: Try with expired token (simulated by logging out)
print("Test 4: Call /auth/me after logout (token still valid)")
print("-" * 60)
print("4.1. Logging out...")
logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
print(f"   Status Code: {logout_response.status_code}")
print(f"   ✅ Logged out")
print()

print("4.2. Calling GET /auth/me with access token after logout...")
after_logout_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

print(f"   Status Code: {after_logout_response.status_code}")
if after_logout_response.status_code == 200:
    print(f"   ℹ️  Access token still valid (JWT tokens are stateless)")
    print(f"   Note: Token will expire in 30 minutes from login")
else:
    print(f"   Response: {after_logout_response.json()}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
