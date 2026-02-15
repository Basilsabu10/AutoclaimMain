"""
Background task service for asynchronous AI processing.
Handles claim analysis without blocking the API response.
"""

import traceback
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db import models
from app.services import ai_orchestrator
from app.services.forensic_mapper import map_forensic_to_db


def process_claim_ai_analysis(
    claim_id: int,
    damage_image_paths: List[str],
    front_image_path: Optional[str],
    description: str
):
    """
    Background task to process AI analysis for a claim.
    Updates claim status and stores forensic analysis results.
    
    Args:
        claim_id: ID of the claim to analyze
        damage_image_paths: List of damage image paths
        front_image_path: Path to front image for OCR
        description: Claim description
    """
    db = SessionLocal()
    
    try:
        # Get the claim
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            print(f"[Background Task] Claim {claim_id} not found")
            return
        
        # Update status to processing
        claim.status = "processing"
        db.commit()
        print(f"[Background Task] Processing claim {claim_id}...")
        
        # Perform AI analysis
        ai_result = ai_orchestrator.analyze_claim(
            damage_image_paths=damage_image_paths,
            front_image_path=front_image_path,
            description=description
        )
        
        if ai_result:
            # Update claim with OCR results
            if ai_result.get("ocr"):
                claim.vehicle_number_plate = ai_result["ocr"].get("plate_text")
            
            # Update claim with AI analysis
            if ai_result.get("ai_analysis"):
                analysis = ai_result["ai_analysis"]
                claim.ai_recommendation = analysis.get("recommendation")
                claim.estimated_cost_min = analysis.get("cost_min")
                claim.estimated_cost_max = analysis.get("cost_max")
            
            # Create or update forensic analysis
            forensic_fields = map_forensic_to_db(ai_result)
            
            # Check if forensic analysis already exists
            existing_forensic = db.query(models.ForensicAnalysis).filter(
                models.ForensicAnalysis.claim_id == claim_id
            ).first()
            
            if existing_forensic:
                # Update existing forensic analysis
                for key, value in forensic_fields.items():
                    setattr(existing_forensic, key, value)
                print(f"[Background Task] Updated existing forensic analysis for claim {claim_id}")
            else:
                # Create new forensic analysis
                forensic = models.ForensicAnalysis(
                    claim_id=claim_id,
                    **forensic_fields
                )
                db.add(forensic)
                print(f"[Background Task] Created forensic analysis for claim {claim_id}")
            
            # Update claim status to completed
            claim.status = "completed"
            db.commit()
            print(f"[Background Task] ✓ Claim {claim_id} analysis completed successfully")
            
        else:
            # No AI result
            claim.status = "failed"
            db.commit()
            print(f"[Background Task] ✗ Claim {claim_id} analysis failed: No AI result")
            
    except Exception as e:
        # Handle errors
        print(f"[Background Task] ✗ Claim {claim_id} analysis failed: {e}")
        traceback.print_exc()
        
        try:
            claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
            if claim:
                claim.status = "failed"
                db.commit()
        except Exception as e2:
            print(f"[Background Task] Failed to update claim status: {e2}")
    
    finally:
        db.close()
