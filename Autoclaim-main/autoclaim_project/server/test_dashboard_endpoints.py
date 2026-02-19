import requests
import sys
import os

# Add server directory to path to import app modules if needed for direct DB access
sys.path.append(os.path.join(os.getcwd(), 'app'))

BASE_URL = "http://localhost:8000"

def test_user_dashboard():
    print("\n=== Testing User Dashboard ===")
    
    # 1. Register a test user
    email = "testuser@example.com"
    password = "password123"
    
    print(f"1. Registering/Logging in user: {email}")
    register_payload = {
        "email": email,
        "password": password,
        "name": "Test User",
        "vehicle_number": "KL-07-TEST-0001"
    }
    
    # Try registration
    resp = requests.post(f"{BASE_URL}/register", json=register_payload)
    if resp.status_code == 200:
        print("   Registration successful")
    elif resp.status_code == 400 and "already registered" in resp.text:
        print("   User already exists, proceeding to login")
    else:
        print(f"   Registration failed: {resp.status_code} {resp.text}")
        return

    # 2. Login to get token
    login_data = {
        "username": email,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/login", data=login_data)
    if resp.status_code != 200:
        print(f"   Login failed: {resp.status_code} {resp.text}")
        return
    
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("   Login successful, token obtained")

    # 3. Access User Dashboard Claims
    print("2. Fetching User Dashboard Claims (GET /claims/my)")
    resp = requests.get(f"{BASE_URL}/claims/my", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Success! User: {data.get('user_email')}, Claims: {data.get('total_claims')}")
        if data.get('claims'):
            print(f"   Sample Claim Status: {data['claims'][0]['status']}")
    else:
        print(f"   Failed: {resp.status_code} {resp.text}")

def test_admin_dashboard():
    print("\n=== Testing Admin Dashboard ===")
    
    # Needs a pre-existing admin user. 
    # Try typical defaults or we might need to create one via DB script if this fails.
    # Assuming 'admin@autoclaim.com' / 'admin123' based on typical patterns, 
    # or we will just use the test user and Expect Failure if they are not admin.
    
    email = "admin@autoclaim.com" 
    password = "admin" # Guessing common password, user mentioned admin login issues before
    
    print(f"1. Logging in as Admin: {email}")
    login_data = {
        "username": email,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/login", data=login_data)
    
    if resp.status_code != 200:
        print(f"   Admin login failed ({resp.status_code}). ")
        print("   NOTE: You may need to create an admin user manually in the DB if one doesn't exist.")
        return

    token = resp.json().get("access_token")
    role = resp.json().get("role")
    
    if role != "admin":
        print(f"   Login successful but role is '{role}', not 'admin'. Skipping admin tests.")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    print("   Admin Login successful")

    # 2. Access Admin Dashboard Claims
    print("2. Fetching Admin All Claims (GET /claims/all)")
    resp = requests.get(f"{BASE_URL}/claims/all", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Success! Total System Claims: {data.get('total_claims')}")
    else:
        print(f"   Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    try:
        # Check if server is running
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("Server is up.")
    except requests.exceptions.ConnectionError:
        print("Error: Server not running at http://localhost:8000")
        sys.exit(1)

    test_user_dashboard()
    test_admin_dashboard()
