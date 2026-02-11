"""Test script for /auth/sessions/{session_id} endpoint"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8001"

print("=" * 60)
print("Testing /auth/sessions/{session_id} Endpoint")
print("=" * 60)
print()

# Setup: Create multiple sessions
print("Setup: Creating multiple sessions")
print("-" * 60)

# First login
print("1. First login...")
login1_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dilani.w@yahoo.com",
        "password": "Welcome@2024"
    }
)

if login1_response.status_code != 200:
    print(f"❌ First login failed: {login1_response.status_code}")
    exit(1)

login1_data = login1_response.json()
access_token1 = login1_data["access_token"]
print(f"   ✅ First login successful!")

# Second login
print("2. Second login...")
login2_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dilani.w@yahoo.com",
        "password": "Welcome@2024"
    }
)

if login2_response.status_code != 200:
    print(f"❌ Second login failed")
    exit(1)

login2_data = login2_response.json()
access_token2 = login2_data["access_token"]
print(f"   ✅ Second login successful!")

# Third login
print("3. Third login...")
login3_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dilani.w@yahoo.com",
        "password": "Welcome@2024"
    }
)

if login3_response.status_code != 200:
    print(f"❌ Third login failed")
    exit(1)

login3_data = login3_response.json()
access_token3 = login3_data["access_token"]
print(f"   ✅ Third login successful!")
print()

# Get all sessions
print("4. Getting all sessions...")
headers1 = {"Authorization": f"Bearer {access_token1}"}
sessions_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers1)

if sessions_response.status_code != 200:
    print(f"❌ Failed to get sessions")
    exit(1)

sessions_data = sessions_response.json()
sessions = sessions_data.get('sessions', [])
print(f"   ✅ Total active sessions: {len(sessions)}")

if len(sessions) < 2:
    print("   ⚠️  Need at least 2 sessions for testing")
    exit(1)

# Display sessions
for idx, session in enumerate(sessions, 1):
    print(f"   Session {idx}: ID={session.get('id')}, Created={session.get('created_at')}")

print()
print("=" * 60)

# Test 1: Revoke a specific session
print("Test 1: Revoke a specific session (not current)")
print("-" * 60)

# Get the first session ID to revoke
session_to_revoke = sessions[0]['id']
print(f"1.1. Revoking session ID: {session_to_revoke}")
print(f"     Using access token from session 1")

revoke_response = requests.delete(
    f"{BASE_URL}/auth/sessions/{session_to_revoke}",
    headers=headers1
)

print(f"   Status Code: {revoke_response.status_code}")
if revoke_response.status_code == 200:
    print(f"   ✅ Session revoked successfully!")
    print(f"   Response: {revoke_response.json()}")
else:
    print(f"   Response: {revoke_response.text}")

print()
print("1.2. Verifying session was revoked...")
sessions_after_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers1)

if sessions_after_response.status_code == 200:
    sessions_after = sessions_after_response.json().get('sessions', [])
    print(f"   Total sessions after revoke: {len(sessions_after)}")
    
    # Check if the revoked session is gone
    revoked_session_ids = [s['id'] for s in sessions_after]
    if session_to_revoke not in revoked_session_ids:
        print(f"   ✅ Session {session_to_revoke} successfully removed!")
    else:
        print(f"   ❌ Session {session_to_revoke} still exists!")
else:
    print(f"   ❌ Failed to verify")

print()
print("=" * 60)

# Test 2: Try to revoke non-existent session
print("Test 2: Try to revoke non-existent session")
print("-" * 60)
fake_session_id = 999999
print(f"2.1. Trying to revoke session ID: {fake_session_id}")

fake_revoke_response = requests.delete(
    f"{BASE_URL}/auth/sessions/{fake_session_id}",
    headers=headers1
)

print(f"   Status Code: {fake_revoke_response.status_code}")
if fake_revoke_response.status_code == 404:
    print(f"   ✅ Correctly rejected: {fake_revoke_response.json()}")
elif fake_revoke_response.status_code == 200:
    print(f"   ⚠️  Returned 200 for non-existent session")
else:
    print(f"   Response: {fake_revoke_response.text}")

print()
print("=" * 60)

# Test 3: Try without authentication
print("Test 3: Try to revoke session without authentication")
print("-" * 60)
print("3.1. Calling DELETE without Authorization header...")

if len(sessions) > 1:
    second_session_id = sessions[1]['id']
    no_auth_response = requests.delete(f"{BASE_URL}/auth/sessions/{second_session_id}")

    print(f"   Status Code: {no_auth_response.status_code}")
    if no_auth_response.status_code == 401:
        print(f"   ✅ Correctly rejected: {no_auth_response.json()}")
    else:
        print(f"   ❌ Should return 401 Unauthorized")
else:
    print("   ⚠️  Not enough sessions to test")

print()
print("=" * 60)

# Test 4: Try to revoke another user's session (if we had multiple users)
print("Test 4: Revoke all remaining sessions")
print("-" * 60)
print("4.1. Getting current sessions...")

current_sessions_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers1)
if current_sessions_response.status_code == 200:
    current_sessions = current_sessions_response.json().get('sessions', [])
    print(f"   Current sessions: {len(current_sessions)}")
    
    if current_sessions:
        print()
        print("4.2. Revoking each session one by one...")
        for session in current_sessions:
            session_id = session['id']
            print(f"     Revoking session {session_id}...")
            revoke_resp = requests.delete(
                f"{BASE_URL}/auth/sessions/{session_id}",
                headers=headers1
            )
            if revoke_resp.status_code == 200:
                print(f"     ✅ Revoked")
            else:
                print(f"     Status: {revoke_resp.status_code}")
        
        print()
        print("4.3. Verifying all sessions revoked...")
        final_sessions_response = requests.get(f"{BASE_URL}/auth/sessions", headers=headers1)
        
        # Note: The current access token might still work (JWT is stateless)
        # But sessions should be cleared from database
        if final_sessions_response.status_code == 200:
            final_sessions = final_sessions_response.json().get('sessions', [])
            print(f"   Remaining sessions: {len(final_sessions)}")
            if len(final_sessions) == 0:
                print(f"   ✅ All sessions successfully revoked!")
            else:
                print(f"   ℹ️  {len(final_sessions)} session(s) still active")
        else:
            print(f"   Status: {final_sessions_response.status_code}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
