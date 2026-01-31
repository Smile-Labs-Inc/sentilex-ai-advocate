"""Test script for lawyer profile endpoints (GET/PUT /lawyers/me)"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Lawyer Profile Endpoints")
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
headers = {"Authorization": f"Bearer {access_token}"}
print(f"✅ Login successful!")
print()

print("=" * 60)

# Test 1: Get current lawyer profile
print("Test 1: Get current lawyer profile (GET /lawyers/me)")
print("-" * 60)
print("1.1. Calling GET /lawyers/me...")

profile_response = requests.get(f"{BASE_URL}/lawyers/me", headers=headers)

print(f"   Status Code: {profile_response.status_code}")
if profile_response.status_code == 200:
    profile_data = profile_response.json()
    print(f"   ✅ Profile retrieved successfully!")
    print(f"   ID: {profile_data.get('id')}")
    print(f"   Name: {profile_data.get('name')}")
    print(f"   Email: {profile_data.get('email')}")
    print(f"   Phone: {profile_data.get('phone')}")
    print(f"   District: {profile_data.get('district')}")
    print(f"   Specialties: {profile_data.get('specialties')}")
    print(f"   Experience: {profile_data.get('experience_years')} years")
    print(f"   Verification Status: {profile_data.get('verification_status')}")
    print(f"   Email Verified: {profile_data.get('is_email_verified')}")
    print(f"   MFA Enabled: {profile_data.get('mfa_enabled')}")
    print(f"   Last Login: {profile_data.get('last_login')}")
else:
    print(f"   ❌ Failed: {profile_response.text}")

print()
print("=" * 60)

# Test 2: Get profile without authentication
print("Test 2: Try to get profile without authentication")
print("-" * 60)
print("2.1. Calling GET /lawyers/me without Authorization header...")

no_auth_response = requests.get(f"{BASE_URL}/lawyers/me")

print(f"   Status Code: {no_auth_response.status_code}")
if no_auth_response.status_code == 401:
    print(f"   ✅ Correctly rejected unauthenticated request")
    print(f"   Error: {no_auth_response.json()}")
else:
    print(f"   Response: {no_auth_response.text}")

print()
print("=" * 60)

# Test 3: Update lawyer profile
print("Test 3: Update lawyer profile (PUT /lawyers/me)")
print("-" * 60)
print("3.1. Updating phone number and availability...")

update_data = {
    "phone": "+94 77 999 8888",
    "availability": "Busy"
}

update_response = requests.put(
    f"{BASE_URL}/lawyers/me",
    headers=headers,
    json=update_data
)

print(f"   Status Code: {update_response.status_code}")
if update_response.status_code == 200:
    updated_data = update_response.json()
    print(f"   ✅ Profile updated successfully!")
    print(f"   Updated Phone: {updated_data.get('phone')}")
    print(f"   Updated Availability: {updated_data.get('availability')}")
else:
    print(f"   ❌ Update failed: {update_response.text}")

print()
print("=" * 60)

# Test 4: Update with additional fields
print("Test 4: Update multiple profile fields")
print("-" * 60)
print("4.1. Updating specialties and experience...")

multi_update = {
    "specialties": "Criminal Law, Family Law, Corporate Law",
    "experience_years": 13,
    "district": "Colombo"
}

multi_update_response = requests.put(
    f"{BASE_URL}/lawyers/me",
    headers=headers,
    json=multi_update
)

print(f"   Status Code: {multi_update_response.status_code}")
if multi_update_response.status_code == 200:
    multi_updated = multi_update_response.json()
    print(f"   ✅ Multiple fields updated successfully!")
    print(f"   Specialties: {multi_updated.get('specialties')}")
    print(f"   Experience: {multi_updated.get('experience_years')} years")
    print(f"   District: {multi_updated.get('district')}")
else:
    print(f"   ❌ Update failed: {multi_update_response.text}")

print()
print("=" * 60)

# Test 5: Verify changes persisted
print("Test 5: Verify updates persisted (GET /lawyers/me again)")
print("-" * 60)
print("5.1. Fetching profile to verify changes...")

verify_response = requests.get(f"{BASE_URL}/lawyers/me", headers=headers)

print(f"   Status Code: {verify_response.status_code}")
if verify_response.status_code == 200:
    verify_data = verify_response.json()
    
    # Check if updates persisted
    phone_match = verify_data.get('phone') == "+94 77 999 8888"
    specialties_match = "Corporate Law" in verify_data.get('specialties', '')
    experience_match = verify_data.get('experience_years') == 13
    
    if phone_match and specialties_match and experience_match:
        print(f"   ✅ All updates persisted correctly!")
    else:
        print(f"   ⚠️  Some updates may not have persisted")
    
    print(f"   Phone: {verify_data.get('phone')}")
    print(f"   Specialties: {verify_data.get('specialties')}")
    print(f"   Experience: {verify_data.get('experience_years')} years")
else:
    print(f"   ❌ Failed: {verify_response.text}")

print()
print("=" * 60)

# Test 6: Update with invalid authentication token
print("Test 6: Try to update with invalid token")
print("-" * 60)
print("6.1. Calling PUT /lawyers/me with invalid token...")

invalid_headers = {"Authorization": "Bearer invalid_token_here"}
invalid_update = requests.put(
    f"{BASE_URL}/lawyers/me",
    headers=invalid_headers,
    json={"phone": "+94 77 111 2222"}
)

print(f"   Status Code: {invalid_update.status_code}")
if invalid_update.status_code == 401:
    print(f"   ✅ Correctly rejected invalid token")
    print(f"   Error: {invalid_update.json()}")
else:
    print(f"   Response: {invalid_update.text}")

print()
print("=" * 60)

# Test 7: Update with read-only fields (should be ignored or rejected)
print("Test 7: Try to update read-only fields")
print("-" * 60)
print("7.1. Attempting to update email (read-only)...")

readonly_update = requests.put(
    f"{BASE_URL}/lawyers/me",
    headers=headers,
    json={
        "email": "newemail@example.com",
        "id": 999,
        "rating": 5.0
    }
)

print(f"   Status Code: {readonly_update.status_code}")
if readonly_update.status_code == 200:
    readonly_data = readonly_update.json()
    # Email should not have changed
    if readonly_data.get('email') == test_email:
        print(f"   ✅ Read-only fields correctly ignored")
        print(f"   Email unchanged: {readonly_data.get('email')}")
    else:
        print(f"   ⚠️  Read-only field was modified!")
else:
    print(f"   Response: {readonly_update.status_code} - {readonly_update.text}")

print()
print("=" * 60)

# Restore original values
print("Cleanup: Restoring original profile values")
print("-" * 60)

restore_data = {
    "phone": "+94 77 123 4567",
    "availability": "Available",
    "specialties": "Criminal Law, Family Law, Civil Litigation",
    "experience_years": 12,
    "district": "Colombo"
}

restore_response = requests.put(
    f"{BASE_URL}/lawyers/me",
    headers=headers,
    json=restore_data
)

if restore_response.status_code == 200:
    print("✅ Original values restored")
else:
    print(f"⚠️  Could not restore: {restore_response.text}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
