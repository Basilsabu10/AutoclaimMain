"""Trigger claim re-analysis using the admin API."""
import requests

# Get admin token
from app.core.security import create_access_token
token = create_access_token({"sub": "admin@autoclaim.com", "role": "admin", "user_id": 1})

# Trigger re-analysis
response = requests.post(
    "http://127.0.0.1:8000/claims/1/analyze",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Re-analysis triggered successfully!")
else:
    print(f"❌ Error: {response.text}")
