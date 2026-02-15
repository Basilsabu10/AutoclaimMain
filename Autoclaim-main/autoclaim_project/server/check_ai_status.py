"""Check if AI analysis was attempted for the claim."""
from app.db.database import SessionLocal
from app.db.models import Claim, ForensicAnalysis
import os

db = SessionLocal()

claim = db.query(Claim).order_by(Claim.created_at.desc()).first()

if claim:
    print(f"\nClaim ID: {claim.id}")
    print(f"Status: {claim.status}")
    print(f"Image paths: {claim.image_paths}")
    print(f"Front image: {claim.front_image_path}")
    
    # Check if images exist
    if claim.image_paths:
        for path in claim.image_paths:
            exists = os.path.exists(path)
            print(f"  - {path}: {'EXISTS' if exists else 'MISSING'}")
    
    if claim.front_image_path:
        exists = os.path.exists(claim.front_image_path)
        print(f"  - Front: {claim.front_image_path}: {'EXISTS' if exists else 'MISSING'}")
    
    # Check AI results stored in claim
    print(f"\nAI Results in Claim:")
    print(f"  - Number plate: {claim.vehicle_number_plate}")
    print(f"  - AI recommendation: {claim.ai_recommendation}")
    print(f"  - Cost estimate: {claim.estimated_cost_min} - {claim.estimated_cost_max}")
    
    forensics = db.query(ForensicAnalysis).filter(ForensicAnalysis.claim_id == claim.id).first()
    print(f"\nForensic record exists: {forensics is not None}")
    
    if forensics and hasattr(forensics, 'ai_raw_response'):
        print(f"Raw AI response stored: {forensics.ai_raw_response is not None}")

db.close()
