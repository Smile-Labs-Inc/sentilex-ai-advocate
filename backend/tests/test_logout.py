"""Test script for logout endpoint"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8001"

print("=" * 60)
print("Testing Logout Endpoint")
print("=" * 60)
print()

# Step 1: Login first to get fresh tokens
print("1. Logging in as Dilani Wijesinghe...")
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
refresh_token = login_data["refresh_token"]

print(f"   ✅ Login successful!")
print(f"   User: {login_data['name']} ({login_data['email']})")
print(f"   Access Token: {access_token[:50]}...")
print()

# Headers with authorization
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Test logout
print("2. Calling POST /auth/logout...")
logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)

print(f"   Status Code: {logout_response.status_code}")
if logout_response.status_code == 200:
    print(f"   Response: {logout_response.json()}")
else:
    print(f"   Error Response: {logout_response.text}")
print()

if logout_response.status_code == 200:
    print("✅ Logout successful!")
    print()
    
    # Try to use the access token again to check /auth/me endpoint
    print("3. Testing if access token still works (GET /auth/me)...")
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status Code: {me_response.status_code}")
    if me_response.status_code == 200:
        print(f"   Response: {me_response.json()}")
        print("   ℹ️  Access token still valid until expiry (30 min from login)")
    else:
        print(f"   Response: {me_response.json()}")
    print()
    
    # Try to use refresh token (should fail now)
    print("4. Testing if refresh token is blacklisted...")
    refresh_response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    print(f"   Status Code: {refresh_response.status_code}")
    print(f"   Response: {refresh_response.json()}")
    if refresh_response.status_code == 401:
        print("   ✅ Refresh token correctly blacklisted!")
    else:
        print("   ❌ Refresh token should have been blacklisted!")
else:
    print(f"❌ Logout failed")

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)
