"""Test script for lawyer sessions management endpoints"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Lawyer Sessions Management")
print("=" * 60)
print()

# Setup: Login to get access token
print("Setup: Login as existing lawyer")
print("-" * 60)

test_email = "nimal.silva@lawfirm.lk"
test_password = "LawyerPass@2024"

print(f"Logging in as {test_email}...")
login_response = requests.post(
    f"{BASE_URL}/lawyers/login",
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
refresh_token = login_data["refresh_token"]
headers = {"Authorization": f"Bearer {access_token}"}
print(f"✅ Login successful!")
print()

print("=" * 60)

# Test 1: Get active sessions
print("Test 1: Get active sessions (GET /lawyers/sessions)")
print("-" * 60)
print("1.1. Calling GET /lawyers/sessions...")

sessions_response = requests.get(f"{BASE_URL}/lawyers/sessions", headers=headers)

print(f"   Status Code: {sessions_response.status_code}")
if sessions_response.status_code == 200:
    sessions_data = sessions_response.json()
    print(f"   ✅ Sessions retrieved successfully!")
    print(f"   Active Sessions Count: {len(sessions_data)}")
    
    if sessions_data:
        session = sessions_data[0]
        session_id = session.get('id')
        print(f"   First Session ID: {session_id}")
        print(f"   IP Address: {session.get('ip_address')}")
        print(f"   User Agent: {session.get('user_agent')[:50]}..." if session.get('user_agent') else None)
        print(f"   Created At: {session.get('created_at')}")
        print(f"   Expires At: {session.get('expires_at')}")
else:
    print(f"   ❌ Failed: {sessions_response.text}")
    exit(1)

print()
print("=" * 60)

# Test 2: Create another session (login again from different "device")
print("Test 2: Create another session (login again)")
print("-" * 60)
print("2.1. Logging in again to create new session...")

login2_response = requests.post(
    f"{BASE_URL}/lawyers/login",
    json={
        "email": test_email,
        "password": test_password
    }
)

if login2_response.status_code == 200:
    login2_data = login2_response.json()
    access_token2 = login2_data["access_token"]
    headers2 = {"Authorization": f"Bearer {access_token2}"}
    print(f"   ✅ Second login successful!")
    
    # Check session count
    sessions2_response = requests.get(f"{BASE_URL}/lawyers/sessions", headers=headers)
    if sessions2_response.status_code == 200:
        sessions2_data = sessions2_response.json()
        print(f"   Active Sessions Count: {len(sessions2_data)}")
        if len(sessions2_data) >= 2:
            print(f"   ✅ New session created")
        else:
            print(f"   ⚠️  Expected at least 2 sessions")
else:
    print(f"   ❌ Second login failed: {login2_response.text}")

print()
print("=" * 60)

# Test 3: Revoke a specific session
print("Test 3: Revoke a specific session (DELETE /lawyers/sessions/{id})")
print("-" * 60)

# Get sessions to find one to revoke
sessions_list_response = requests.get(f"{BASE_URL}/lawyers/sessions", headers=headers)
if sessions_list_response.status_code == 200:
    sessions_list = sessions_list_response.json()
    
    if len(sessions_list) >= 2:
        # Revoke the second session (not the current one)
        session_to_revoke = sessions_list[1]['id']
        print(f"3.1. Revoking session ID: {session_to_revoke}...")
        
        revoke_response = requests.delete(
            f"{BASE_URL}/lawyers/sessions/{session_to_revoke}",
            headers=headers
        )
        
        print(f"   Status Code: {revoke_response.status_code}")
        if revoke_response.status_code == 200:
            revoke_data = revoke_response.json()
            print(f"   ✅ Session revoked successfully!")
            print(f"   Message: {revoke_data.get('message')}")
            
            # Verify session is removed
            print()
            print("3.2. Verifying session was removed...")
            verify_response = requests.get(f"{BASE_URL}/lawyers/sessions", headers=headers)
            if verify_response.status_code == 200:
                remaining_sessions = verify_response.json()
                print(f"   Remaining Sessions: {len(remaining_sessions)}")
                if len(remaining_sessions) == len(sessions_list) - 1:
                    print(f"   ✅ Session successfully removed")
                else:
                    print(f"   ⚠️  Session count mismatch")
        else:
            print(f"   ❌ Revoke failed: {revoke_response.text}")
    else:
        print("   ⚠️  Not enough sessions to test revocation")

print()
print("=" * 60)

# Test 4: Try to revoke non-existent session
print("Test 4: Try to revoke non-existent session")
print("-" * 60)
print("4.1. Attempting to revoke session ID: 999999...")

nonexistent_revoke = requests.delete(
    f"{BASE_URL}/lawyers/sessions/999999",
    headers=headers
)

print(f"   Status Code: {nonexistent_revoke.status_code}")
if nonexistent_revoke.status_code == 404:
    print(f"   ✅ Correctly rejected non-existent session")
    print(f"   Error: {nonexistent_revoke.json()}")
else:
    print(f"   Response: {nonexistent_revoke.text}")

print()
print("=" * 60)

# Test 5: Try to access sessions without authentication
print("Test 5: Try to access sessions without authentication")
print("-" * 60)
print("5.1. Calling GET /lawyers/sessions without auth...")

no_auth_sessions = requests.get(f"{BASE_URL}/lawyers/sessions")

print(f"   Status Code: {no_auth_sessions.status_code}")
if no_auth_sessions.status_code == 401:
    print(f"   ✅ Correctly rejected unauthenticated request")
    print(f"   Error: {no_auth_sessions.json()}")
else:
    print(f"   Response: {no_auth_sessions.text}")

print()
print("=" * 60)

# Test 6: Try to revoke session without authentication
print("Test 6: Try to revoke session without authentication")
print("-" * 60)
print("6.1. Calling DELETE /lawyers/sessions/{id} without auth...")

no_auth_revoke = requests.delete(f"{BASE_URL}/lawyers/sessions/1")

print(f"   Status Code: {no_auth_revoke.status_code}")
if no_auth_revoke.status_code == 401:
    print(f"   ✅ Correctly rejected unauthenticated request")
    print(f"   Error: {no_auth_revoke.json()}")
else:
    print(f"   Response: {no_auth_revoke.text}")

print()
print("=" * 60)

# Test 7: Verify session details are correct
print("Test 7: Verify session details structure")
print("-" * 60)
print("7.1. Checking session data structure...")

final_sessions = requests.get(f"{BASE_URL}/lawyers/sessions", headers=headers)
if final_sessions.status_code == 200:
    sessions = final_sessions.json()
    if sessions:
        session = sessions[0]
        required_fields = ['id', 'ip_address', 'user_agent', 'created_at', 'expires_at']
        
        has_all_fields = all(field in session for field in required_fields)
        
        if has_all_fields:
            print(f"   ✅ Session structure is correct")
            print(f"   Fields present: {', '.join(required_fields)}")
        else:
            missing = [f for f in required_fields if f not in session]
            print(f"   ⚠️  Missing fields: {', '.join(missing)}")
    else:
        print(f"   ⚠️  No sessions available to verify")
else:
    print(f"   ❌ Failed to get sessions")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
