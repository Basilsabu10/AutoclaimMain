"""
Comprehensive AI Testing Script
Tests Groq, OCR, and full forensic analysis pipeline
"""
import os
import json
from datetime import datetime

# Import all AI services
from app.services.groq_service import analyze_damage, GROQ_AVAILABLE, init_groq
from app.services.ocr_service import extract_number_plate, OCR_AVAILABLE, init_ocr

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def test_groq_service(image_path):
    """Test Groq AI forensic analysis"""
    print_section("GROQ FORENSIC ANALYSIS TEST")
    
    print(f"Groq Available: {GROQ_AVAILABLE}")
    
    if not GROQ_AVAILABLE:
        print("[ERROR] Groq service not available. Check API key.")
        return None
    
    print(f"\n📸 Testing with image: {image_path}")
    print(f"Image exists: {os.path.exists(image_path)}")
    
    if not os.path.exists(image_path):
        print("[ERROR] Image file not found!")
        return None
    
    # Test with description
    description = "Car was parked in residential area when damage occurred"
    
    print(f"\n🤖 Calling Groq API...")
    print(f"Description: '{description}'")
    
    result = analyze_damage(
        image_paths=[image_path],
        description=description
    )
    
    # Check for errors
    if not result.get("success"):
        print(f"\n❌ GROQ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Check if it's a rate limit error
        error_msg = str(result.get('error', '')).lower()
        if 'rate' in error_msg or 'limit' in error_msg or 'quota' in error_msg:
            print("\n⚠️  GROQ API RATE LIMIT REACHED!")
            print("This is likely a temporary issue. Wait a few minutes and try again.")
        
        return result
    
    print(f"\n✅ GROQ SUCCESS!")
    print(f"Provider: {result.get('provider')}")
    print(f"Model: {result.get('model')}")
    
    # Extract key results
    print("\n" + "-"*80)
    print("KEY RESULTS:")
    print("-"*80)
    
    # Vehicle Identification
    vehicle_id = result.get('vehicle_identification', {})
    print(f"\n🚗 Vehicle Identification:")
    print(f"  Make: {vehicle_id.get('make')}")
    print(f"  Model: {vehicle_id.get('model')}")
    print(f"  Color: {vehicle_id.get('color')}")
    
    license_plate = vehicle_id.get('license_plate', {})
    print(f"  License Plate: {license_plate.get('text', 'Not detected')}")
    print(f"  Plate Confidence: {license_plate.get('confidence', 0)}%")
    
    # Damage Assessment
    damage = result.get('damage_assessment', {})
    print(f"\n💥 Damage Assessment:")
    print(f"  Damage Detected: {damage.get('damage_detected')}")
    print(f"  Overall Severity: {damage.get('overall_severity')}")
    
    cost_estimate = damage.get('estimated_repair_cost', {})
    print(f"  Estimated Cost: ${cost_estimate.get('min_usd', 0)} - ${cost_estimate.get('max_usd', 0)}")
    
    damaged_panels = damage.get('damaged_panels', [])
    if damaged_panels:
        print(f"\n  Damaged Panels ({len(damaged_panels)}):")
        for panel in damaged_panels[:5]:  # Show first 5
            print(f"    - {panel.get('panel_name')}: {panel.get('damage_type')} ({panel.get('severity')})")
    
    # Forensic Analysis
    forensic = result.get('forensic_analysis', {})
    print(f"\n🔍 Forensic Analysis:")
    print(f"  Authenticity Score: {forensic.get('authenticity_score')}%")
    print(f"  Digital Manipulation Detected: {forensic.get('digital_manipulation_detected')}")
    
    if forensic.get('forgery_indicators'):
        print(f"  Forgery Indicators: {', '.join(forensic.get('forgery_indicators'))}")
    
    # Pre-existing Damage
    pre_existing = result.get('pre_existing_damage', {})
    print(f"\n⚠️  Pre-existing Damage:")
    print(f"  Detected: {pre_existing.get('detected')}")
    if pre_existing.get('detected'):
        print(f"  Description: {pre_existing.get('description')}")
    
    # Risk Assessment
    risk_flags = result.get('risk_flags', [])
    if risk_flags:
        print(f"\n🚨 Risk Flags ({len(risk_flags)}):")
        for flag in risk_flags:
            print(f"    - {flag}")
    else:
        print(f"\n✅ No Risk Flags")
    
    # Final Assessment
    final = result.get('final_assessment', {})
    print(f"\n📋 Final Assessment:")
    print(f"  Overall Confidence: {final.get('overall_confidence_score')}%")
    print(f"  Recommendation: {final.get('recommendation')}")
    print(f"  Fraud Probability: {final.get('fraud_probability')}")
    print(f"  Human Review Priority: {final.get('human_review_priority')}")
    print(f"\n  Reasoning: {final.get('decision_reasoning')}")
    
    # Save full results to file
    output_file = "test_groq_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Full results saved to: {output_file}")
    
    return result

def test_ocr_service(image_path):
    """Test OCR license plate extraction"""
    print_section("OCR LICENSE PLATE TEST")
    
    print(f"OCR Available: {OCR_AVAILABLE}")
    
    if not OCR_AVAILABLE:
        print("[WARNING] OCR service not available")
        return None
    
    print(f"\n📸 Testing with image: {image_path}")
    
    result = extract_number_plate(image_path)
    
    print(f"\n🔤 OCR Result:")
    print(f"  Plate Text: {result.get('plate_text', 'Not detected')}")
    print(f"  Confidence: {result.get('confidence', 0)}%")
    
    return result

def main():
    """Run all tests"""
    print_section("AUTOCLAIM AI TESTING SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize services
    print("\n🔧 Initializing services...")
    init_groq()
    init_ocr()
    
    # Test image - using existing upload
    image_path = "uploads/front_415bec7b-dde4-4a8a-a88a-03ea95a53153.jpg"
    
    if not os.path.exists(image_path):
        print(f"\n❌ ERROR: Test image not found at: {image_path}")
        print("Please ensure the image is uploaded to the uploads folder.")
        return
    
    # Run tests
    groq_result = test_groq_service(image_path)
    ocr_result = test_ocr_service(image_path)
    
    # Summary
    print_section("TEST SUMMARY")
    
    groq_status = "✅ PASSED" if groq_result and groq_result.get("success") else "❌ FAILED"
    ocr_status = "✅ PASSED" if ocr_result and ocr_result.get('plate_text') else "⚠️  NO RESULT"
    
    print(f"\nGroq Forensic Analysis: {groq_status}")
    print(f"OCR License Plate: {ocr_status}")
    
    if groq_result and not groq_result.get("success"):
        error_msg = str(groq_result.get('error', '')).lower()
        if 'rate' in error_msg or 'limit' in error_msg or 'quota' in error_msg:
            print("\n" + "⚠️ "*40)
            print("GROQ API RATE LIMIT DETECTED!")
            print("The Groq API has reached its request limit.")
            print("This is usually temporary. Please wait and try again later.")
            print("⚠️ "*40)
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()
