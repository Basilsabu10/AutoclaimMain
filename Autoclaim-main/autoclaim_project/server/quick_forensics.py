"""Quick view of latest claim forensics."""
from app.db.database import SessionLocal
from app.db.models import Claim, ForensicAnalysis, User

db = SessionLocal()

claim = db.query(Claim).order_by(Claim.created_at.desc()).first()

if not claim:
    print("No claims found")
else:
    user = db.query(User).filter(User.id == claim.user_id).first()
    forensics = db.query(ForensicAnalysis).filter(ForensicAnalysis.claim_id == claim.id).first()
    
    print(f"\nClaim ID: {claim.id}")
    print(f"User: {user.email if user else 'Unknown'}")
    print(f"Status: {claim.status}")
    print(f"Submitted: {claim.created_at}")
    print(f"\nDescription: {claim.description[:100]}...")
    
    if not forensics:
        print("\n⚠️  No forensic analysis found")
    else:
        print(f"\n=== FORENSIC ANALYSIS ===")
        print(f"AI Recommendation: {forensics.ai_recommendation}")
        print(f"Overall Confidence: {forensics.overall_confidence_score}%")
        print(f"Fraud Probability: {forensics.fraud_probability}")
        print(f"Damage Detected: {forensics.ai_damage_detected}")
        print(f"Severity: {forensics.ai_severity}")
        print(f"License Plate: {forensics.license_plate_text}")
        if forensics.ai_cost_min:
            print(f"Cost Range: Rs {forensics.ai_cost_min:,} - Rs {forensics.ai_cost_max:,}")
        print(f"Vehicle: {forensics.vehicle_make} {forensics.vehicle_model} {forensics.vehicle_year}")

db.close()
