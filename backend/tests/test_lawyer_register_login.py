"""Test script for lawyer registration and login endpoints"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Lawyer Registration & Login")
print("=" * 60)
print()

# Test 1: Register a new lawyer
print("Test 1: Register a new lawyer")
print("-" * 60)
print("1.1. Calling POST /lawyers/register...")

register_data = {
    "name": "Nimal Perera",
    "email": "nimal.perera.test@example.com",
    "password": "LawyerPass@2024",
    "phone": "+94771234567",
    "district": "Colombo",
    "specialties": "Criminal Law, Civil Law",
    "experience_years": 5
}

register_response = requests.post(
    f"{BASE_URL}/lawyers/register",
    json=register_data
)

print(f"   Status Code: {register_response.status_code}")
if register_response.status_code == 200:
    register_result = register_response.json()
    print(f"   ✅ Lawyer registered successfully!")
    print(f"   ID: {register_result.get('id')}")
    print(f"   Name: {register_result.get('name')}")
    print(f"   Email: {register_result.get('email')}")
    print(f"   Verification Status: {register_result.get('verification_status')}")
else:
    print(f"   ❌ Registration failed: {register_response.text}")

print()
print("=" * 60)

# Test 2: Try to register with same email (duplicate)
print("Test 2: Try to register with duplicate email")
print("-" * 60)
print("2.1. Calling POST /lawyers/register with existing email...")

duplicate_response = requests.post(
    f"{BASE_URL}/lawyers/register",
    json=register_data
)

print(f"   Status Code: {duplicate_response.status_code}")
if duplicate_response.status_code == 400:
    print(f"   ✅ Correctly rejected duplicate email")
    print(f"   Error: {duplicate_response.json()}")
else:
    print(f"   ⚠️  Expected 400, got: {duplicate_response.text}")

print()
print("=" * 60)

# Test 3: Login with unverified email (should fail)
print("Test 3: Try to login with unverified email")
print("-" * 60)
print("3.1. Calling POST /lawyers/login...")

login_data = {
    "email": register_data["email"],
    "password": register_data["password"]
}

login_response = requests.post(
    f"{BASE_URL}/lawyers/login",
    json=login_data
)

print(f"   Status Code: {login_response.status_code}")
if login_response.status_code == 403:
    print(f"   ✅ Correctly rejected unverified email")
    print(f"   Error: {login_response.json()}")
else:
    print(f"   Response: {login_response.text}")

print()
print("=" * 60)

# Test 4: Login with existing verified lawyer
print("Test 4: Login with existing verified lawyer account")
print("-" * 60)

# Using existing verified lawyer from your database
test_lawyer_email = "nimal.silva@lawfirm.lk"
test_lawyer_password = "LawyerPass@2024"

print(f"4.1. Logging in as {test_lawyer_email}...")

verified_login_response = requests.post(
    f"{BASE_URL}/lawyers/login",
    json={
        "email": test_lawyer_email,
        "password": test_lawyer_password
    }
)

print(f"   Status Code: {verified_login_response.status_code}")
if verified_login_response.status_code == 200:
    login_result = verified_login_response.json()
    access_token = login_result.get("access_token")
    refresh_token = login_result.get("refresh_token")
    
    print(f"   ✅ Login successful!")
    print(f"   User Type: {login_result.get('user_type')}")
    print(f"   User ID: {login_result.get('user_id')}")
    print(f"   Email: {login_result.get('email')}")
    print(f"   Name: {login_result.get('name')}")
    print(f"   MFA Enabled: {login_result.get('mfa_enabled')}")
    print(f"   Access Token (first 20 chars): {access_token[:20]}...")
    print(f"   Refresh Token (first 20 chars): {refresh_token[:20]}...")
    
    # Save tokens for further tests
    headers = {"Authorization": f"Bearer {access_token}"}
else:
    print(f"   ❌ Login failed: {verified_login_response.text}")
    exit(1)

print()
print("=" * 60)

# Test 5: Login with wrong password
print("Test 5: Login with incorrect password")
print("-" * 60)
print("5.1. Attempting login with wrong password...")

wrong_password_response = requests.post(
    f"{BASE_URL}/lawyers/login",
    json={
        "email": test_lawyer_email,
        "password": "WrongPassword123"
    }
)

print(f"   Status Code: {wrong_password_response.status_code}")
if wrong_password_response.status_code == 401:
    print(f"   ✅ Correctly rejected invalid password")
    print(f"   Error: {wrong_password_response.json()}")
else:
    print(f"   Response: {wrong_password_response.text}")

print()
print("=" * 60)

# Test 6: Login with non-existent email
print("Test 6: Login with non-existent email")
print("-" * 60)
print("6.1. Attempting login with non-existent email...")

nonexistent_response = requests.post(
    f"{BASE_URL}/lawyers/login",
    json={
        "email": "nonexistent.lawyer@example.com",
        "password": "SomePassword123"
    }
)

print(f"   Status Code: {nonexistent_response.status_code}")
if nonexistent_response.status_code == 401:
    print(f"   ✅ Correctly rejected non-existent email")
    print(f"   Error: {nonexistent_response.json()}")
else:
    print(f"   Response: {nonexistent_response.text}")

print()
print("=" * 60)

# Test 7: Validate registration with invalid data
print("Test 7: Register with invalid data (weak password)")
print("-" * 60)
print("7.1. Attempting registration with weak password...")

weak_password_response = requests.post(
    f"{BASE_URL}/lawyers/register",
    json={
        "name": "Test Lawyer",
        "email": "test.weak@example.com",
        "password": "weak",
        "phone": "+94771234567",
        "district": "Colombo",
        "specialties": "Criminal Law",
        "experience_years": 3
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

# Test 8: Register with invalid email format
print("Test 8: Register with invalid email format")
print("-" * 60)
print("8.1. Attempting registration with invalid email...")

invalid_email_response = requests.post(
    f"{BASE_URL}/lawyers/register",
    json={
        "name": "Test Lawyer",
        "email": "invalid-email",
        "password": "ValidPass@2024",
        "phone": "+94771234567",
        "district": "Colombo",
        "specialties": "Criminal Law",
        "experience_years": 3
    }
)

print(f"   Status Code: {invalid_email_response.status_code}")
if invalid_email_response.status_code == 422:
    print(f"   ✅ Correctly rejected invalid email format")
    print(f"   Validation Error: {invalid_email_response.json()}")
else:
    print(f"   Response: {invalid_email_response.text}")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
print()
print(f"Test lawyer account for further testing:")
print(f"Email: {test_lawyer_email}")
print(f"Access Token: {access_token[:50]}...")
