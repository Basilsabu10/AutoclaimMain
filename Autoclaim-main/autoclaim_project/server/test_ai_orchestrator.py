"""Test what the AI orchestrator returns for debugging."""
import sys
import os

# Get the actual image paths from the claim
from app.db.database import SessionLocal
from app.db.models import Claim

db = SessionLocal()
claim = db.query(Claim).order_by(Claim.created_at.desc()).first()

if claim:
    print(f"Testing AI orchestrator with claim {claim.id}")
    print(f"Images: {claim.image_paths}")
    print(f"Front: {claim.front_image_path}")
    print(f"Description: {claim.description[:100]}...")
    
    # Now test the AI orchestrator
    from app.services import ai_orchestrator
    
    print("\n=== CALLING AI ORCHESTRATOR ===\n")
    result = ai_orchestrator.analyze_claim(
        damage_image_paths=claim.image_paths or [],
        front_image_path=claim.front_image_path,
        description=claim.description or ""
    )
    
    print("\n=== AI ORCHESTRATOR RESULT ===\n")
    import json
    print(json.dumps(result, indent=2, default=str))
    
    # Check what keys are at the top level
    print("\n=== TOP LEVEL KEYS ===")
    if isinstance(result, dict):
        for key in result.keys():
            print(f"  - {key}")
    
else:
    print("No claim found")

db.close()
