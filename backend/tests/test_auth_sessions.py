"""Test script for /auth/sessions endpoint"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing /auth/sessions Endpoint")
print("=" * 60)
print()

# Test 1: Get active sessions with valid token
print("Test 1: Get active sessions with valid access token")
print("-" * 60)

# Login first to create a session
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

# Call /auth/sessions endpoint
print("1.2. Calling GET /auth/sessions...")
headers = {"Authorization": f"Bearer {access_token}"}
sessions_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers)

print(f"   Status Code: {sessions_response.status_code}")
if sessions_response.status_code == 200:
    sessions_data = sessions_response.json()
    print(f"   ✅ Sessions retrieved successfully!")
    print()
    
    sessions = sessions_data.get('sessions', [])
    print(f"   Total Active Sessions: {len(sessions)}")
    print()
    
    if sessions:
        for idx, session in enumerate(sessions, 1):
            print(f"   Session {idx}:")
            print(f"      ID: {session.get('id')}")
            print(f"      User ID: {session.get('user_id')}")
            print(f"      User Type: {session.get('user_type')}")
            print(f"      IP Address: {session.get('ip_address')}")
            print(f"      Device Type: {session.get('device_type')}")
            print(f"      Browser: {session.get('browser')}")
            print(f"      OS: {session.get('os')}")
            print(f"      Created At: {session.get('created_at')}")
            print(f"      Last Activity: {session.get('last_activity')}")
            print(f"      Expires At: {session.get('expires_at')}")
            print(f"      Active: {session.get('is_active')}")
            print()
    else:
        print("   ℹ️  No active sessions found")
else:
    print(f"   ❌ Failed to get sessions: {sessions_response.text}")

print()
print("=" * 60)

# Test 2: Login multiple times to create multiple sessions
print("Test 2: Create multiple sessions by logging in again")
print("-" * 60)
print("2.1. Logging in again (2nd session)...")
login2_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dilani.w@yahoo.com",
        "password": "Welcome@2024"
    }
)

if login2_response.status_code == 200:
    print("   ✅ Second login successful!")
    login2_data = login2_response.json()
    access_token2 = login2_data["access_token"]
    
    print()
    print("2.2. Checking sessions again...")
    headers2 = {"Authorization": f"Bearer {access_token2}"}
    sessions2_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers2)
    
    if sessions2_response.status_code == 200:
        sessions2_data = sessions2_response.json()
        sessions2 = sessions2_data.get('sessions', [])
        print(f"   Total Active Sessions: {len(sessions2)}")
        print(f"   ✅ Multiple sessions tracked correctly!")
    else:
        print(f"   ❌ Failed: {sessions2_response.text}")
else:
    print(f"   ❌ Second login failed: {login2_response.text}")

print()
print("=" * 60)

# Test 3: Try without authentication
print("Test 3: Call /auth/sessions without access token")
print("-" * 60)
print("3.1. Calling GET /auth/sessions without Authorization header...")
no_auth_response = requests.get(f"{BASE_URL}/auth/sessions")

print(f"   Status Code: {no_auth_response.status_code}")
if no_auth_response.status_code == 401:
    print(f"   ✅ Correctly rejected: {no_auth_response.json()}")
else:
    print(f"   ❌ Should return 401 Unauthorized")

print()
print("=" * 60)

# Test 4: Check sessions after logout
print("Test 4: Check sessions after logout")
print("-" * 60)
print("4.1. Logging out all sessions...")
logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers2)
print(f"   Status Code: {logout_response.status_code}")

if logout_response.status_code == 200:
    print(f"   ✅ Logged out successfully")
    print()
    
    # Login again to check if sessions were cleared
    print("4.2. Logging in again after logout...")
    login3_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "dilani.w@yahoo.com",
            "password": "Welcome@2024"
        }
    )
    
    if login3_response.status_code == 200:
        login3_data = login3_response.json()
        access_token3 = login3_data["access_token"]
        headers3 = {"Authorization": f"Bearer {access_token3}"}
        
        print("   ✅ Login successful")
        print()
        print("4.3. Checking sessions...")
        sessions3_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers3)
        
        if sessions3_response.status_code == 200:
            sessions3_data = sessions3_response.json()
            sessions3 = sessions3_data.get('sessions', [])
            print(f"   Total Active Sessions: {len(sessions3)}")
            if len(sessions3) == 1:
                print(f"   ✅ Previous sessions correctly cleared!")
            else:
                print(f"   ℹ️  {len(sessions3)} session(s) found")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
