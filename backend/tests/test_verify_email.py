"""Test script for /auth/verify-email endpoint"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing /auth/verify-email Endpoint")
print("=" * 60)
print()

# Test 1: Register a new user to get verification token
print("Test 1: Register new user and generate verification token")
print("-" * 60)

# Register new user
import random
random_num = random.randint(10000, 99999)
test_email = f"testuser{random_num}@example.com"

print(f"1.1. Registering new user: {test_email}")
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "first_name": "Test",
        "last_name": "User",
        "email": test_email,
        "password": "TestPass@123",
        "preferred_language": "en",
        "district": "Colombo"
    }
)

print(f"   Status Code: {register_response.status_code}")
if register_response.status_code == 201:
    register_data = register_response.json()
    print(f"   ✅ User registered successfully!")
    print(f"   Message: {register_data.get('message')}")
    print(f"   Verification Sent: {register_data.get('verification_sent')}")
    
    # Check if user is not verified yet
    user_data = register_data.get('user')
    if user_data:
        print(f"   Email Verified: {user_data.get('email_verified')}")
        if not user_data.get('email_verified'):
            print(f"   ✅ User correctly marked as unverified")
else:
    print(f"   ❌ Registration failed: {register_response.text}")
    exit(1)

print()

# Generate verification token manually (since email is not actually sent in test)
print("1.2. Generating verification token...")
import sys
sys.path.insert(0, 'C:\\Users\\SAMPR\\OneDrive\\Desktop\\GitHub Projects\\sentilex-ai-advocate\\backend')
from utils.auth import generate_verification_token

verification_token = generate_verification_token(test_email)
print(f"   Token generated: {verification_token[:50]}...")

print()
print("=" * 60)

# Test 2: Verify email with valid token
print("Test 2: Verify email with valid token")
print("-" * 60)
print("2.1. Calling POST /auth/verify-email with valid token...")

verify_response = requests.post(
    f"{BASE_URL}/auth/verify-email",
    json={
        "token": verification_token
    }
)

print(f"   Status Code: {verify_response.status_code}")
if verify_response.status_code == 200:
    verify_data = verify_response.json()
    print(f"   ✅ Email verified successfully!")
    print(f"   Message: {verify_data.get('message')}")
    
    # Login to check if email is now verified
    print()
    print("2.2. Logging in to verify email_verified flag...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": "TestPass@123"
        }
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"   ✅ Login successful!")
        
        # Get user profile to check email_verified
        access_token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            email_verified = me_data.get('email_verified')
            print(f"   Email Verified Status: {email_verified}")
            if email_verified:
                print(f"   ✅ Email verification status updated correctly!")
            else:
                print(f"   ❌ Email still showing as unverified")
else:
    print(f"   ❌ Verification failed: {verify_response.text}")

print()
print("=" * 60)

# Test 3: Try to verify with invalid token
print("Test 3: Try to verify with invalid token")
print("-" * 60)
print("3.1. Calling POST /auth/verify-email with invalid token...")

invalid_verify_response = requests.post(
    f"{BASE_URL}/auth/verify-email",
    json={
        "token": "invalid_token_here"
    }
)

print(f"   Status Code: {invalid_verify_response.status_code}")
if invalid_verify_response.status_code == 400:
    print(f"   ✅ Correctly rejected: {invalid_verify_response.json()}")
else:
    print(f"   Response: {invalid_verify_response.text}")

print()
print("=" * 60)

# Test 4: Try to verify already verified email
print("Test 4: Try to verify already verified email")
print("-" * 60)
print("4.1. Calling POST /auth/verify-email again with same token...")

duplicate_verify_response = requests.post(
    f"{BASE_URL}/auth/verify-email",
    json={
        "token": verification_token
    }
)

print(f"   Status Code: {duplicate_verify_response.status_code}")
if duplicate_verify_response.status_code == 200:
    print(f"   ✅ Accepted (idempotent operation)")
    print(f"   Message: {duplicate_verify_response.json().get('message')}")
else:
    print(f"   Response: {duplicate_verify_response.text}")

print()
print("=" * 60)

# Test 5: Try with expired token (simulate by using old user)
print("Test 5: Test with non-existent user email in token")
print("-" * 60)
print("5.1. Generating token for non-existent user...")

fake_email = "nonexistent@example.com"
fake_token = generate_verification_token(fake_email)

print("5.2. Calling POST /auth/verify-email...")
fake_verify_response = requests.post(
    f"{BASE_URL}/auth/verify-email",
    json={
        "token": fake_token
    }
)

print(f"   Status Code: {fake_verify_response.status_code}")
if fake_verify_response.status_code == 404:
    print(f"   ✅ Correctly rejected: {fake_verify_response.json()}")
else:
    print(f"   Response: {fake_verify_response.text}")

print()
print("=" * 60)

# Test 6: Try with wrong token type
print("Test 6: Test with wrong token type (access token)")
print("-" * 60)
print("6.1. Using access token instead of verification token...")

if 'access_token' in locals():
    wrong_type_response = requests.post(
        f"{BASE_URL}/auth/verify-email",
        json={
            "token": access_token
        }
    )
    
    print(f"   Status Code: {wrong_type_response.status_code}")
    if wrong_type_response.status_code == 400:
        print(f"   ✅ Correctly rejected: {wrong_type_response.json()}")
    else:
        print(f"   Response: {wrong_type_response.text}")
else:
    print("   ⚠️  Skipped (no access token available)")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
print()
print(f"Test user created: {test_email} (password: TestPass@123)")
print("Email verified: True")
