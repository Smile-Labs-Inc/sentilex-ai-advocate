"""Test script for GET /lawyers/ listing endpoint"""
import requests

BASE_URL = "http://127.0.0.1:8001"

print("=" * 60)
print("Testing Lawyer Listing Endpoint")
print("=" * 60)
print()

# Test 1: Get all lawyers
print("Test 1: Get all lawyers (GET /lawyers/)")
print("-" * 60)
print("1.1. Calling GET /lawyers/...")

all_lawyers = requests.get(f"{BASE_URL}/lawyers/")

print(f"   Status Code: {all_lawyers.status_code}")
if all_lawyers.status_code == 200:
    lawyers_data = all_lawyers.json()
    print(f"   ✅ Lawyers retrieved successfully!")
    print(f"   Total Lawyers: {len(lawyers_data)}")
    
    if lawyers_data:
        lawyer = lawyers_data[0]
        print(f"   First Lawyer:")
        print(f"     - ID: {lawyer.get('id')}")
        print(f"     - Name: {lawyer.get('name')}")
        print(f"     - District: {lawyer.get('district')}")
        print(f"     - Specialties: {lawyer.get('specialties')}")
        print(f"     - Experience: {lawyer.get('experience_years')} years")
        print(f"     - Rating: {lawyer.get('rating')}")
        print(f"     - Verification Status: {lawyer.get('verification_status')}")
else:
    print(f"   ❌ Failed: {all_lawyers.text}")

print()
print("=" * 60)

# Test 2: Filter by district
print("Test 2: Filter lawyers by district")
print("-" * 60)
print("2.1. Calling GET /lawyers/?district=Colombo...")

colombo_lawyers = requests.get(f"{BASE_URL}/lawyers/?district=Colombo")

print(f"   Status Code: {colombo_lawyers.status_code}")
if colombo_lawyers.status_code == 200:
    colombo_data = colombo_lawyers.json()
    print(f"   ✅ Filtered lawyers retrieved!")
    print(f"   Lawyers in Colombo: {len(colombo_data)}")
    
    # Verify all are from Colombo
    if colombo_data:
        all_colombo = all(l.get('district') == 'Colombo' for l in colombo_data)
        if all_colombo:
            print(f"   ✅ All lawyers are from Colombo")
        else:
            print(f"   ⚠️  Some lawyers are not from Colombo")
else:
    print(f"   Response: {colombo_lawyers.text}")

print()
print("=" * 60)

# Test 3: Filter by specialty
print("Test 3: Filter lawyers by specialty")
print("-" * 60)
print("3.1. Calling GET /lawyers/?specialty=Criminal Law...")

criminal_lawyers = requests.get(f"{BASE_URL}/lawyers/?specialty=Criminal Law")

print(f"   Status Code: {criminal_lawyers.status_code}")
if criminal_lawyers.status_code == 200:
    criminal_data = criminal_lawyers.json()
    print(f"   ✅ Filtered lawyers retrieved!")
    print(f"   Lawyers with Criminal Law specialty: {len(criminal_data)}")
    
    if criminal_data:
        # Verify all have Criminal Law in specialties
        all_criminal = all('Criminal Law' in l.get('specialties', '') for l in criminal_data)
        if all_criminal:
            print(f"   ✅ All lawyers have Criminal Law specialty")
        else:
            print(f"   ⚠️  Some lawyers don't have Criminal Law specialty")
else:
    print(f"   Response: {criminal_lawyers.text}")

print()
print("=" * 60)

# Test 4: Filter by both district and specialty
print("Test 4: Filter by both district and specialty")
print("-" * 60)
print("4.1. Calling GET /lawyers/?district=Colombo&specialty=Criminal Law...")

combo_lawyers = requests.get(
    f"{BASE_URL}/lawyers/?district=Colombo&specialty=Criminal Law"
)

print(f"   Status Code: {combo_lawyers.status_code}")
if combo_lawyers.status_code == 200:
    combo_data = combo_lawyers.json()
    print(f"   ✅ Filtered lawyers retrieved!")
    print(f"   Lawyers matching both filters: {len(combo_data)}")
    
    if combo_data:
        # Verify filters applied
        all_match = all(
            l.get('district') == 'Colombo' and 'Criminal Law' in l.get('specialties', '')
            for l in combo_data
        )
        if all_match:
            print(f"   ✅ All lawyers match both filters")
        else:
            print(f"   ⚠️  Some lawyers don't match both filters")
else:
    print(f"   Response: {combo_lawyers.text}")

print()
print("=" * 60)

# Test 5: Filter by non-existent district
print("Test 5: Filter by non-existent district")
print("-" * 60)
print("5.1. Calling GET /lawyers/?district=NonExistentCity...")

nonexistent_lawyers = requests.get(f"{BASE_URL}/lawyers/?district=NonExistentCity")

print(f"   Status Code: {nonexistent_lawyers.status_code}")
if nonexistent_lawyers.status_code == 200:
    nonexistent_data = nonexistent_lawyers.json()
    print(f"   ✅ Request successful!")
    print(f"   Lawyers found: {len(nonexistent_data)}")
    if len(nonexistent_data) == 0:
        print(f"   ✅ Correctly returns empty list")
else:
    print(f"   Response: {nonexistent_lawyers.text}")

print()
print("=" * 60)

# Test 6: Verify response structure
print("Test 6: Verify response structure")
print("-" * 60)
print("6.1. Checking lawyer object structure...")

all_lawyers_check = requests.get(f"{BASE_URL}/lawyers/")
if all_lawyers_check.status_code == 200:
    lawyers = all_lawyers_check.json()
    if lawyers:
        lawyer = lawyers[0]
        required_fields = [
            'id', 'name', 'specialties', 'experience_years', 
            'email', 'phone', 'district', 'availability', 
            'rating', 'reviews_count', 'verification_status', 'is_active'
        ]
        
        has_all_fields = all(field in lawyer for field in required_fields)
        
        if has_all_fields:
            print(f"   ✅ Response structure is correct")
            print(f"   All required fields present:")
            for field in required_fields:
                print(f"     - {field}: {lawyer.get(field)}")
        else:
            missing = [f for f in required_fields if f not in lawyer]
            print(f"   ⚠️  Missing fields: {', '.join(missing)}")
    else:
        print(f"   ⚠️  No lawyers to verify structure")
else:
    print(f"   ❌ Failed to get lawyers")

print()
print("=" * 60)

# Test 7: Verify only active lawyers are returned (if applicable)
print("Test 7: Verify only appropriate lawyers are shown")
print("-" * 60)
print("7.1. Checking lawyer visibility...")

visibility_check = requests.get(f"{BASE_URL}/lawyers/")
if visibility_check.status_code == 200:
    lawyers = visibility_check.json()
    if lawyers:
        active_count = sum(1 for l in lawyers if l.get('is_active'))
        print(f"   Total Lawyers: {len(lawyers)}")
        print(f"   Active Lawyers: {active_count}")
        
        # Check if all are active or if inactive ones are shown
        all_active = all(l.get('is_active') for l in lawyers)
        if all_active:
            print(f"   ✅ Only active lawyers are shown")
        else:
            print(f"   ℹ️  Inactive lawyers are also shown")
    else:
        print(f"   ⚠️  No lawyers available")
else:
    print(f"   ❌ Failed")

print()
print("=" * 60)
print("All Tests Complete!")
print("=" * 60)
