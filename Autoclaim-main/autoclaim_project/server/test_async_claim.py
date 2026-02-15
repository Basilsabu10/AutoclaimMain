"""
Test script to verify async AI analysis after claim submission.
"""

import requests
import time
import json
import os

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_EMAIL = "userm@gmail.com"
LOGIN_PASSWORD = "user123"

# Test image paths
TEST_IMAGES_DIR = "uploads"  # Adjust as needed
DAMAGE_IMAGE = os.path.join(TEST_IMAGES_DIR, "damage_test.jpg")
FRONT_IMAGE = os.path.join(TEST_IMAGES_DIR, "front_test.jpg")


def login(email, password):
    """Login and get JWT token."""
    # OAuth2PasswordRequestForm expects form data, not JSON
    # The 'username' field should contain the email
    response = requests.post(
        f"{BASE_URL}/login",
        data={
            "username": email,  # OAuth2 uses 'username' field for email
            "password": password
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None


def submit_claim(token, description="Test claim for async AI analysis"):
    """Submit a claim with test images."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Prepare multipart form data
    files = []
    data = {"description": description}
    
    # Add test images if they exist
    if os.path.exists(DAMAGE_IMAGE):
        files.append(("images", open(DAMAGE_IMAGE, "rb")))
    if os.path.exists(FRONT_IMAGE):
        files.append(("front_image", open(FRONT_IMAGE, "rb")))
    
    # If no test images exist, create dummy ones
    if not files:
        print("⚠️  No test images found. Creating dummy image data...")
        # Create a minimal valid JPEG file
        dummy_jpg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
        files.append(("images", ("test_damage.jpg", dummy_jpg, "image/jpeg")))
    
    response = requests.post(
        f"{BASE_URL}/claims",
        headers=headers,
        data=data,
        files=files
    )
    
    # Close file handles
    for _, file_obj in files:
        if hasattr(file_obj, 'close'):
            file_obj.close()
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Claim submission failed: {response.text}")
        return None


def get_claim_details(token, claim_id):
    """Get claim details by ID."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/claims/{claim_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get claim details: {response.text}")
        return None


def main():
    """Test async AI analysis workflow."""
    print("=" * 60)
    print("Testing Async AI Analysis")
    print("=" * 60)
    
    # Step 1: Login
    print("\n[Step 1] Logging in...")
    token = login(LOGIN_EMAIL, LOGIN_PASSWORD)
    if not token:
        print("❌ Login failed. Make sure the user exists.")
        print(f"   Try creating user: {LOGIN_EMAIL}")
        return
    print(f"✅ Login successful")
    
    # Step 2: Submit claim
    print("\n[Step 2] Submitting claim...")
    start_time = time.time()
    result = submit_claim(token)
    submit_duration = time.time() - start_time
    
    if not result:
        print("❌ Claim submission failed")
        return
    
    claim_id = result["claim_id"]
    initial_status = result["data"]["status"]
    
    print(f"✅ Claim submitted in {submit_duration:.2f}s")
    print(f"   Claim ID: {claim_id}")
    print(f"   Status: {initial_status}")
    print(f"   Message: {result['message']}")
    
    # Verify it returned quickly (should be < 2 seconds)
    if submit_duration < 2.0:
        print(f"✅ Response was fast ({submit_duration:.2f}s) - async working!")
    else:
        print(f"⚠️  Response took {submit_duration:.2f}s - may be running synchronously")
    
    # Step 3: Poll for completion
    print("\n[Step 3] Waiting for AI analysis to complete...")
    max_wait = 30  # seconds
    poll_interval = 2  # seconds
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        
        claim = get_claim_details(token, claim_id)
        if not claim:
            print("❌ Failed to fetch claim details")
            break
        
        status = claim["status"]
        print(f"   [{elapsed}s] Status: {status}")
        
        if status == "completed":
            print(f"\n✅ AI analysis completed in ~{elapsed}s")
            print("\n📊 Analysis Results:")
            print(f"   Vehicle Plate: {claim.get('vehicle_number_plate', 'N/A')}")
            print(f"   AI Recommendation: {claim.get('ai_recommendation', 'N/A')}")
            print(f"   Estimated Cost: ${claim.get('estimated_cost_min', 0)} - ${claim.get('estimated_cost_max', 0)}")
            
            if claim.get("forensic_analysis"):
                forensic = claim["forensic_analysis"]
                print(f"\n🔍 Forensic Analysis:")
                print(f"   Damage Type: {forensic.get('ai_damage_type', 'N/A')}")
                print(f"   Severity: {forensic.get('ai_severity', 'N/A')}")
                print(f"   Affected Parts: {forensic.get('ai_affected_parts', [])}")
            
            return
        
        elif status == "failed":
            print(f"\n❌ AI analysis failed")
            return
    
    print(f"\n⚠️  AI analysis still running after {max_wait}s")
    print("   Final status:", claim["status"])


if __name__ == "__main__":
    main()
