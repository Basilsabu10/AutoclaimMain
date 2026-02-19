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
from app.services.repair_estimator_service import estimate_repair_cost


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
        
        # Fetch policy data for verification
        policy_data = None
        if claim.policy_id:
            policy = db.query(models.Policy).filter(models.Policy.id == claim.policy_id).first()
            if policy:
                policy_data = {
                    "vehicle_make": policy.vehicle_make,
                    "vehicle_model": policy.vehicle_model,
                    "vehicle_year": policy.vehicle_year,
                    "vehicle_registration": policy.vehicle_registration,
                    "status": policy.status,
                    "start_date": policy.start_date.isoformat() if policy.start_date else None,
                    "end_date": policy.end_date.isoformat() if policy.end_date else None,
                    "plan_coverage": policy.plan.coverage_amount if policy.plan else None,
                    "location": None,  # Not stored in current schema
                }
                print(f"[Background Task] Loaded policy data for claim {claim_id}")
        
        # Fetch claim history for duplicate detection
        claim_history = []
        if claim.user_id:
            prior_claims = db.query(models.Claim).filter(
                models.Claim.user_id == claim.user_id,
                models.Claim.id != claim_id  # Exclude current claim
            ).all()
            
            for prior in prior_claims:
                claim_history.append({
                    "claim_id": prior.id,
                    "status": prior.status,
                    "created_at": prior.created_at.isoformat() if prior.created_at else None,
                    "vehicle_registration": prior.vehicle_number_plate,
                })
            
            if claim_history:
                print(f"[Background Task] Found {len(claim_history)} prior claims for user {claim.user_id}")
        
        # Determine claim amount (from estimated cost or default)
        claim_amount = 0
        if claim.estimated_cost_max:
            claim_amount = claim.estimated_cost_max
        elif claim.estimated_cost_min:
            claim_amount = claim.estimated_cost_min
        # If no estimate, verification will use 0 (which may trigger amount threshold checks)
        
        # Perform AI analysis with verification
        ai_result = ai_orchestrator.analyze_claim(
            damage_image_paths=damage_image_paths,
            front_image_path=front_image_path,
            description=description,
            claim_amount=claim_amount,
            policy_data=policy_data,
            claim_history=claim_history
        )
        
        if ai_result:
            # Update claim with OCR results
            if ai_result.get("ocr"):
                claim.vehicle_number_plate = ai_result["ocr"].get("plate_text")
            
            # Update claim with verification results (v4.0 - comprehensive rule-based verification)
            if ai_result.get("verification"):
                verification = ai_result["verification"]
                claim.ai_recommendation = verification.get("status")  # APPROVED, FLAGGED, REJECTED
                
            # Also check legacy decisions field for backward compatibility
            elif ai_result.get("decisions"):
                decisions = ai_result["decisions"]
                claim.ai_recommendation = decisions.get("ai_recommendation")
            
            # Create or update forensic analysis
            forensic_fields = map_forensic_to_db(ai_result)
            
            # ── Repair Cost Estimation ───────────────────────────────────────
            # Extract damaged panels and vehicle info from AI result.
            # ai_result["ai_analysis"] is the merged Groq extraction dict which
            # contains sub-keys: damage, identity, forensics, scene.
            ai_analysis = ai_result.get("ai_analysis", {})
            damaged_panels = (
                ai_analysis.get("damage", {}).get("damaged_panels")          # Groq nested path
                or forensic_fields.get("ai_damaged_panels")                  # already-mapped field
                or []
            )
            vehicle_make  = (ai_analysis.get("identity", {}).get("vehicle_make")
                             or forensic_fields.get("vehicle_make"))
            vehicle_model = (ai_analysis.get("identity", {}).get("vehicle_model")
                             or forensic_fields.get("vehicle_model"))
            vehicle_year  = (ai_analysis.get("identity", {}).get("vehicle_year")
                             or forensic_fields.get("vehicle_year"))
            
            if damaged_panels:
                cost_estimate = estimate_repair_cost(
                    damaged_panels=damaged_panels,
                    vehicle_make=vehicle_make,
                    vehicle_model=vehicle_model,
                    vehicle_year=vehicle_year
                )
                # Store part-by-part breakdown in forensic fields
                forensic_fields["repair_cost_breakdown"] = cost_estimate
                # Update claim cost fields with INR totals from estimator
                claim.estimated_cost_min = cost_estimate["total_inr_min"]
                claim.estimated_cost_max = cost_estimate["total_inr_max"]
                print(f"[Background Task] Repair estimate: "
                      f"₹{cost_estimate['total_inr_min']:,} – ₹{cost_estimate['total_inr_max']:,} "
                      f"({len(cost_estimate['breakdown'])} parts)")
            else:
                # Fall back to Groq's own INR estimate if no panels detected
                if ai_result.get("ai_analysis", {}).get("damage", {}).get("estimated_cost_range_INR"):
                    cost_range = ai_result["ai_analysis"]["damage"]["estimated_cost_range_INR"]
                    claim.estimated_cost_min = cost_range.get("min")
                    claim.estimated_cost_max = cost_range.get("max")
            # ────────────────────────────────────────────────────────────────
            
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
