"""
Quick AI Service Status Check
Tests Groq API availability and OCR functionality
"""
import os
import sys

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("AUTOCLAIM AI SERVICE STATUS CHECK")
print("="*80)

# Test 1: Check Groq Service
print("\n1. Testing Groq Service...")
try:
    from app.services.groq_service import init_groq, GROQ_AVAILABLE, analyze_damage
    from app.core.config import settings
    
    print(f"   Groq API Key Set: {'Yes' if settings.GROQ_API_KEY else 'No'}")
    
    init_result = init_groq()
    print(f"   Groq Initialized: {init_result}")
    print(f"   Groq Available: {GROQ_AVAILABLE}")
    
    if GROQ_AVAILABLE:
        print(f"   Groq Model: {settings.GROQ_MODEL}")
        print("   ✅ Groq Service is READY")
    else:
        print("   ❌ Groq Service is NOT available")
except Exception as e:
    print(f"   ❌ Error importing Groq: {e}")

# Test 2: Check OCR Service
print("\n2. Testing OCR Service...")
try:
    from app.services.ocr_service import init_ocr, OCR_AVAILABLE, extract_number_plate
    
    init_ocr()
    print(f"   OCR Available: {OCR_AVAILABLE}")
    
    if OCR_AVAILABLE:
        print("   ✅ OCR Service is READY")
    else:
        print("   ⚠️  OCR Service is NOT available (optional)")
except Exception as e:
    print(f"   ❌ Error importing OCR: {e}")

# Test 3: Test with an actual image (if Groq is available)
if GROQ_AVAILABLE:
    print("\n3. Running Groq Analysis Test...")
    print("   Looking for test image...")
    
    # Find a front image
    uploads_dir = "uploads"
    test_image = None
    
    if os.path.exists(uploads_dir):
        images = [f for f in os.listdir(uploads_dir) if f.startswith("front_") and f.endswith(".jpg")]
        if images:
            test_image = os.path.join(uploads_dir, images[0])
            print(f"   Using image: {images[0]}")
    
    if test_image and os.path.exists(test_image):
        print(f"   Image size: {os.path.getsize(test_image) / 1024:.1f} KB")
        print("\n   🤖 Calling Groq API (this may take 10-30 seconds)...")
        
        try:
            result = analyze_damage(
                image_paths=[test_image],
                description="Test analysis of vehicle front image"
            )
            
            if result.get("success"):
                print("\n   ✅ GROQ API CALL SUCCESSFUL!")
                print(f"   Provider: {result.get('provider')}")
                print(f"   Model: {result.get('model')}")
                
                # Show key results
                vehicle = result.get('vehicle_identification', {})
                print(f"\n   Vehicle Detected:")
                print(f"     Make: {vehicle.get('make', 'UNKNOWN')}")
                print(f"     Model: {vehicle.get('model', 'UNKNOWN')}")
                print(f"     Color: {vehicle.get('color', 'UNKNOWN')}")
                
                damage = result.get('damage_assessment', {})
                print(f"\n   Damage Assessment:")
                print(f"     Damage Detected: {damage.get('damage_detected', False)}")
                print(f"     Severity: {damage.get('overall_severity', 'NONE')}")
                
                final = result.get('final_assessment', {})
                print(f"\n   Final Assessment:") 
                print(f"     Confidence: {final.get('overall_confidence_score', 0)}%")
                print(f"     Recommendation: {final.get('recommendation', 'UNKNOWN')}")
                
                print("\n   💾 Saving full results to 'quick_test_result.json'")
                import json
                with open('quick_test_result.json', 'w') as f:
                    json.dump(result, f, indent=2)
                
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"\n   ❌ GROQ API CALL FAILED!")
                print(f"   Error: {error_msg}")
                
                # Check for rate limit
                if any(word in str(error_msg).lower() for word in ['rate', 'limit', 'quota', 'exceeded']):
                    print("\n   " + "⚠️ "*30)
                    print("   GROQ API RATE LIMIT DETECTED!")
                    print("   The Groq API has reached its request limit.")
                    print("   This is usually a temporary issue (hourly/daily limit).")
                    print("   Please wait and try again later.")
                    print("   " + "⚠️ "*30)
                
        except Exception as e:
            print(f"\n   ❌ Exception during Groq call: {e}")
            if 'rate' in str(e).lower() or 'limit' in str(e).lower():
                print("\n   ⚠️  This appears to be a RATE LIMIT error!")
    else:
        print("   ⚠️  No test image found in uploads/")

print("\n" + "="*80)
print("STATUS CHECK COMPLETE")
print("="*80)
