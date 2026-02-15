"""Test CORS preflight request to /register endpoint."""
import requests

# Test OPTIONS (preflight) request
print("=" * 80)
print("Testing CORS Preflight Request")
print("=" * 80)

response = requests.options(
    'http://127.0.0.1:8000/register',
    headers={
        'Origin': 'http://localhost:5174',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
)

print(f"\nStatus Code: {response.status_code}")
print("\n--- All Response Headers ---")
for header, value in response.headers.items():
    print(f"{header}: {value}")

print("\n--- CORS-Specific Headers ---")
cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
if cors_headers:
    for header, value in cors_headers.items():
        print(f"✓ {header}: {value}")
else:
    print("❌ No CORS headers found!")

print("\n--- Verification ---")
has_allow_origin = any('access-control-allow-origin' in k.lower() for k in response.headers.keys())
has_allow_methods = any('access-control-allow-methods' in k.lower() for k in response.headers.keys())
has_allow_headers = any('access-control-allow-headers' in k.lower() for k in response.headers.keys())

print(f"Has Access-Control-Allow-Origin: {has_allow_origin}")
print(f"Has Access-Control-Allow-Methods: {has_allow_methods}")
print(f"Has Access-Control-Allow-Headers: {has_allow_headers}")

if has_allow_origin and has_allow_methods and has_allow_headers:
    print("\n✅ CORS is properly configured!")
else:
    print("\n❌ CORS is missing required headers!")

print("=" * 80)
