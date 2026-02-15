"""
Quick test to check if AI analysis data is being stored properly
"""
from app.db.database import SessionLocal
from app.db import models
import json

db = SessionLocal()

# Get the latest claim with forensic analysis
latest = db.query(models.ForensicAnalysis).order_by(models.ForensicAnalysis.id.desc()).first()

if latest:
    print("=" * 80)
    print(f"LATEST FORENSIC ANALYSIS (ID: {latest.id}, Claim: {latest.claim_id})")
    print("=" * 80)
    
    print(f"\n📊 Basic Fields:")
    print(f"  Severity: {latest.ai_severity}")
    print(f"  Damage Type: {latest.ai_damage_type}")
    print(f"  Recommendation: {latest.ai_recommendation}")
    print(f"  Cost: ${latest.ai_cost_min} - ${latest.ai_cost_max}")
    print(f"  Confidence: {latest.ai_confidence}")
    print(f"  Risk Flags: {latest.ai_risk_flags}")
    
    print(f"\n📍 EXIF:")
    print(f"  Location: {latest.exif_location_name}")
    print(f"  GPS: ({latest.exif_gps_lat}, {latest.exif_gps_lon})")
    
    print(f"\n🔤 OCR:")
    print(f"  Plate: {latest.ocr_plate_text} (conf: {latest.ocr_plate_confidence})")
    
    if latest.ai_raw_response:
        print(f"\n🤖 Comprehensive AI Response Available:")
        ai_data = latest.ai_raw_response
        
        # Show forensic analysis section
        if "ai_analysis" in ai_data:
            ai_analysis = ai_data["ai_analysis"]
            
            # Check for comprehensive sections
            if "forensic_analysis" in ai_analysis:
                print(f"  ✅ Forensic Analysis (Authenticity, Forgery Detection)")
                fa = ai_analysis["forensic_analysis"]
                print(f"     Authenticity Score: {fa.get('authenticity_score')}")
                print(f"     Manipulation Detected: {fa.get('digital_manipulation_detected')}")
                
            if "vehicle_identification" in ai_analysis:
                print(f"  ✅ Vehicle Identification")
                vi = ai_analysis["vehicle_identification"]
                if "vehicle_details" in vi:
                    vd = vi["vehicle_details"]
                    print(f"     Make/Model: {vd.get('make')} {vd.get('model')}")
                
            if "pre_existing_damage" in ai_analysis:
                print(f"  ✅ Pre-existing Damage Detection")
                ped = ai_analysis["pre_existing_damage"]
                print(f"     Detected: {ped.get('detected')}")
                
            if "final_assessment" in ai_analysis:
                print(f"  ✅ Final Assessment")
                fa = ai_analysis["final_assessment"]
                print(f"     Fraud Probability: {fa.get('fraud_probability')}")
                print(f"     Review Priority: {fa.get('human_review_priority')}")
        
        # Show full JSON (truncated)
        print(f"\n📄 Full JSON Response (first 500 chars):")
        json_str = json.dumps(ai_data, indent=2)
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
    else:
        print("\n❌ No ai_raw_response data stored")
        
else:
    print("No forensic analyses found in database")

db.close()
