"""
Test database storage by simulating background task storage.
"""

from app.db.database import SessionLocal
from app.db.models import Claim, User, Policy, ForensicAnalysis
from app.services.forensic_mapper import map_forensic_to_db
from datetime import datetime
import json

# Load the test result
with open('test_extraction_result.json', 'r') as f:
    ai_result = json.load(f)

db = SessionLocal()

try:
    # Get the first user and policy
    user = db.query(User).first()
    policy = db.query(Policy).first()
    
    if not user or not policy:
        print("❌ No user or policy found. Run seed_kia_policy.py first.")
        exit(1)
    
    # Create a new claim
    claim = Claim(
        user_id=user.id,
        policy_id=policy.id,
        description="Test claim for v3.0 storage validation",
        status="processing"
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    
    print(f"✓ Created test claim ID: {claim.id}")
    
    # Update claim with OCR and decisions (simulating background task)
    if ai_result.get("ocr"):
        claim.vehicle_number_plate = ai_result["ocr"].get("plate_text")
    
    if ai_result.get("decisions"):
        decisions = ai_result["decisions"]
        claim.ai_recommendation = decisions.get("ai_recommendation")
        if ai_result.get("ai_analysis", {}).get("damage", {}).get("estimated_cost_range_INR"):
            cost_range = ai_result["ai_analysis"]["damage"]["estimated_cost_range_INR"]
            claim.estimated_cost_min = cost_range.get("min")
            claim.estimated_cost_max = cost_range.get("max")
    
    # Create forensic analysis
    forensic_fields = map_forensic_to_db(ai_result)
    
    forensic = ForensicAnalysis(
        claim_id=claim.id,
        **forensic_fields
    )
    db.add(forensic)
    
    claim.status = "completed"
    db.commit()
    
    print(f"✓ Created forensic analysis for claim {claim.id}")
    print(f"\n📊 Stored Data:")
    print(f"  Claim Status: {claim.status}")
    print(f"  Recommendation: {claim.ai_recommendation}")
    print(f"  Cost Range: ₹{claim.estimated_cost_min} - ₹{claim.estimated_cost_max}")
    print(f"\n🔍 Forensic Fields Stored:")
    print(f"  Vehicle: {forensic.vehicle_make} {forensic.vehicle_model} ({forensic.vehicle_color})")
    print(f"  Plate: {forensic.ocr_plate_text}")
    print(f"  Damage Severity: {forensic.damage_severity_score}")
    print(f"  Impact Point: {forensic.impact_point}")
    print(f"  Fraud Score: {forensic.fraud_score}")
    print(f"  Fraud Probability: {forensic.fraud_probability}")
    print(f"  Risk Flags: {forensic.ai_risk_flags}")
    print(f"  Screen Recapture: {forensic.is_screen_recapture}")
    print(f"  Rust Present: {forensic.is_rust_present}")
    print(f"  Analysis Version: {forensic.analysis_version}")
    
    print(f"\n✅ Database storage test SUCCESSFUL!")
    
except Exception as e:
    db.rollback()
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
