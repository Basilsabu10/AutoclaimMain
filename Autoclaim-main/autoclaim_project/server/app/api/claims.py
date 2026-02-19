"""
Claims API routes.
Handles claim submission, retrieval, and management.
"""

import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.core.config import settings
from app.core.dependencies import get_current_user, require_admin

# Try to import AI service
try:
    from app.services import ai_orchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI service not available")

# Import forensic mapper
from app.services.forensic_mapper import map_forensic_to_db, extract_simple_fields


router = APIRouter(prefix="/claims", tags=["Claims"])

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


async def save_upload_file(upload_file: UploadFile, prefix: str = "") -> Optional[str]:
    """
    Save an uploaded file and return the path.
    Preserves original filename if it contains a date pattern (for metadata extraction),
    otherwise uses UUID for anonymity.
    """
    if not upload_file or not upload_file.filename:
        return None
    
    import re
    
    file_extension = os.path.splitext(upload_file.filename)[1]
    original_name = os.path.splitext(upload_file.filename)[0]
    
    # Check if filename contains a date pattern (for metadata extraction)
    date_patterns = [
        r'PXL_\d{8}_\d{9}',  # Google Pixel
        r'(?:IMG_)?\d{8}_\d{6}',  # Samsung/Android
        r'IMG-\d{8}-WA',  # WhatsApp
        r'Screenshot_\d{8}-\d{6}',  # Screenshot
        r'Photo_\d{4}-\d{2}-\d{2}',  # iPhone
        r'VID_\d{8}_\d{6}',  # Video
        r'\d{8}',  # Generic date
    ]
    
    has_date_pattern = any(re.search(pattern, original_name) for pattern in date_patterns)
    
    if has_date_pattern:
        # Preserve original filename for metadata extraction
        unique_filename = f"{prefix}{original_name}{file_extension}"
    else:
        # Use UUID for files without date patterns
        unique_filename = f"{prefix}{uuid.uuid4()}{file_extension}"
    
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path


@router.post("")
async def upload_claim(
    description: str = Form(""),
    images: List[UploadFile] = File(default=[]),
    front_image: Optional[UploadFile] = File(default=None),
    estimate_bill: Optional[UploadFile] = File(default=None),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new claim with AI analysis.
    
    Args:
        description: Natural language claim description
        images: Multiple damage images
        front_image: Front view of vehicle (for number plate OCR)
        estimate_bill: Repair estimate document
        background_tasks: FastAPI background tasks for async processing
    """
    # Get user from database
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save damage images
    saved_image_paths = []
    for image in images:
        path = await save_upload_file(image, "damage_")
        if path:
            saved_image_paths.append(path)
    
    # Save front image and estimate bill
    front_image_path = await save_upload_file(front_image, "front_") if front_image else None
    estimate_bill_path = await save_upload_file(estimate_bill, "bill_") if estimate_bill else None
    
    # Create claim with 'processing' status
    new_claim = models.Claim(
        user_id=user.id,
        description=description,
        image_paths=saved_image_paths,
        front_image_path=front_image_path,
        estimate_bill_path=estimate_bill_path,
        status="processing"  # Will be updated by background task
    )
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    
    # Schedule AI analysis as background task
    if AI_AVAILABLE and background_tasks:
        from app.services.background_tasks import process_claim_ai_analysis
        
        background_tasks.add_task(
            process_claim_ai_analysis,
            claim_id=new_claim.id,
            damage_image_paths=saved_image_paths,
            front_image_path=front_image_path,
            description=description
        )
        print(f"[API] Claim {new_claim.id} submitted. AI analysis scheduled in background.")
    else:
        # No AI available, set status to pending
        new_claim.status = "pending"
        db.commit()
        print(f"[API] Claim {new_claim.id} submitted. AI service not available.")
    
    # Return immediate response
    return {
        "status": "success",
        "message": "Claim submitted successfully. AI analysis in progress.",
        "claim_id": new_claim.id,
        "data": {
            "description": description,
            "images_count": len(saved_image_paths),
            "front_image": front_image_path is not None,
            "estimate_bill": estimate_bill_path is not None,
            "status": new_claim.status,
            "created_at": new_claim.created_at.isoformat(),
            "note": "AI analysis is being processed in the background. Check claim status later for results."
        }
    }


@router.get("/my")
def get_my_claims(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all claims for the current logged-in user."""
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    claims = db.query(models.Claim).filter(
        models.Claim.user_id == user.id
    ).order_by(models.Claim.created_at.desc()).all()
    
    return {
        "user_email": user.email,
        "total_claims": len(claims),
        "claims": [
            {
                "id": claim.id,
                "description": claim.description[:100] + "..." if claim.description and len(claim.description) > 100 else claim.description,
                "images_count": len(claim.image_paths) if claim.image_paths else 0,
                "status": claim.status,
                "created_at": claim.created_at.isoformat(),
                "vehicle_number_plate": claim.vehicle_number_plate,
                "ai_recommendation": claim.ai_recommendation,
                "estimated_cost_min": claim.estimated_cost_min,
                "estimated_cost_max": claim.estimated_cost_max
            }
            for claim in claims
        ]
    }


@router.get("/all")
def get_all_claims(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all claims from all users (Admin only)."""
    claims = db.query(models.Claim).order_by(models.Claim.created_at.desc()).all()
    
    return {
        "total_claims": len(claims),
        "claims": [
            {
                "id": claim.id,
                "user_email": claim.user.email,
                "description": claim.description[:100] + "..." if claim.description and len(claim.description) > 100 else claim.description,
                "images_count": len(claim.image_paths) if claim.image_paths else 0,
                "status": claim.status,
                "created_at": claim.created_at.isoformat(),
                "vehicle_number_plate": claim.vehicle_number_plate,
                "ai_recommendation": claim.ai_recommendation,
                "estimated_cost_min": claim.estimated_cost_min,
                "estimated_cost_max": claim.estimated_cost_max,
                "forensic": {
                    "exif_timestamp": claim.forensic_analysis.exif_timestamp.isoformat() if claim.forensic_analysis and claim.forensic_analysis.exif_timestamp else None,
                    "exif_location_name": claim.forensic_analysis.exif_location_name if claim.forensic_analysis else None,
                    "ai_damage_type": claim.forensic_analysis.ai_damage_type if claim.forensic_analysis else None,
                    "ai_severity": claim.forensic_analysis.ai_severity if claim.forensic_analysis else None
                } if claim.forensic_analysis else None
            }
            for claim in claims
        ]
    }


@router.get("/{claim_id}")
def get_claim_details(
    claim_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed claim information."""
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Check access
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    if current_user["role"] != "admin" and claim.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build forensic data if available
    forensic_data = None
    if claim.forensic_analysis:
        fa = claim.forensic_analysis
        forensic_data = {
            "exif_timestamp": fa.exif_timestamp.isoformat() if fa.exif_timestamp else None,
            "exif_gps_lat": fa.exif_gps_lat,
            "exif_gps_lon": fa.exif_gps_lon,
            "exif_location_name": fa.exif_location_name,
            "exif_camera_make": fa.exif_camera_make,
            "exif_camera_model": fa.exif_camera_model,
            "ocr_plate_text": fa.ocr_plate_text,
            "ocr_plate_confidence": fa.ocr_plate_confidence,
            "ai_damage_type": fa.ai_damage_type,
            "ai_severity": fa.ai_severity,
            "ai_affected_parts": fa.ai_affected_parts,
            "ai_damaged_panels": fa.ai_damaged_panels,
            "ai_structural_damage": fa.ai_structural_damage,
            "ai_recommendation": fa.ai_recommendation,
            "ai_reasoning": fa.ai_reasoning,
            "ai_cost_min": fa.ai_cost_min,
            "ai_cost_max": fa.ai_cost_max,
            "ai_risk_flags": fa.ai_risk_flags,
            "risk_flags": fa.ai_risk_flags,  # Alias for frontend
            "overall_confidence_score": fa.overall_confidence_score,
            "confidence_score": fa.overall_confidence_score,  # Alias for frontend
            "authenticity_score": fa.authenticity_score,
            "vehicle_make": fa.vehicle_make,
            "vehicle_model": fa.vehicle_model,
            "vehicle_year": fa.vehicle_year,
            "vehicle_color": fa.vehicle_color,
            "license_plate_text": fa.license_plate_text,
            "license_plate_match_status": fa.license_plate_match_status,
            "yolo_damage_detected": fa.yolo_damage_detected,
            "yolo_severity": fa.yolo_severity,
            "yolo_summary": fa.yolo_summary,
            "forgery_detected": fa.forgery_detected,
            "pre_existing_damage_detected": fa.pre_existing_damage_detected,
            "pre_existing_indicators": fa.pre_existing_indicators,
            "pre_existing_description": fa.pre_existing_description,
            "pre_existing_confidence": fa.pre_existing_confidence,
            "fraud_probability": fa.fraud_probability,
            "repair_cost_breakdown": fa.repair_cost_breakdown,
            "analyzed_at": fa.analyzed_at.isoformat() if fa.analyzed_at else None
        }
    
    return {
        "id": claim.id,
        "user_email": claim.user.email,
        "description": claim.description,
        "image_paths": claim.image_paths,
        "front_image_path": claim.front_image_path,
        "estimate_bill_path": claim.estimate_bill_path,
        "status": claim.status,
        "created_at": claim.created_at.isoformat(),
        "vehicle_number_plate": claim.vehicle_number_plate,
        "ai_recommendation": claim.ai_recommendation,
        "estimated_cost_min": claim.estimated_cost_min,
        "estimated_cost_max": claim.estimated_cost_max,
        "forensic_analysis": forensic_data
    }


@router.put("/{claim_id}/status")
def update_claim_status(
    claim_id: int,
    new_status: str = Query(..., description="New claim status"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update claim status (Admin only)."""
    if new_status not in ["pending", "approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use: pending, approved, rejected")
    
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim.status = new_status
    db.commit()
    
    return {"message": f"Claim {claim_id} status updated to {new_status}"}


@router.post("/{claim_id}/analyze")
def reanalyze_claim(
    claim_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Re-run AI analysis on a claim (Admin only)."""
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        ai_result = ai_orchestrator.analyze_claim(
            damage_image_paths=claim.image_paths or [],
            front_image_path=claim.front_image_path,
            description=claim.description or ""
        )
        
        if ai_result:
            # Update claim quick-access fields
            if ai_result.get("ocr"):
                claim.vehicle_number_plate = ai_result["ocr"].get("plate_text")
            
            if ai_result.get("ai_analysis"):
                analysis = ai_result["ai_analysis"]
                claim.ai_recommendation = analysis.get("recommendation")
                claim.estimated_cost_min = analysis.get("cost_min")
                claim.estimated_cost_max = analysis.get("cost_max")
            
            # Update or create forensic analysis
            if claim.forensic_analysis:
                fa = claim.forensic_analysis
            else:
                fa = models.ForensicAnalysis(claim_id=claim.id)
                db.add(fa)
            
            # Update forensic fields
            fa.exif_timestamp = ai_result.get("metadata", {}).get("timestamp")
            fa.exif_gps_lat = ai_result.get("metadata", {}).get("gps_lat")
            fa.exif_gps_lon = ai_result.get("metadata", {}).get("gps_lon")
            fa.exif_location_name = ai_result.get("metadata", {}).get("location_name")
            fa.ocr_plate_text = ai_result.get("ocr", {}).get("plate_text")
            fa.ocr_plate_confidence = ai_result.get("ocr", {}).get("confidence")
            fa.ai_damage_type = ai_result.get("ai_analysis", {}).get("damage_type")
            fa.ai_severity = ai_result.get("ai_analysis", {}).get("severity")
            fa.ai_affected_parts = ai_result.get("ai_analysis", {}).get("affected_parts", [])
            fa.ai_recommendation = ai_result.get("ai_analysis", {}).get("recommendation")
            fa.ai_reasoning = ai_result.get("ai_analysis", {}).get("analysis_text")
            fa.ai_cost_min = ai_result.get("ai_analysis", {}).get("cost_min")
            fa.ai_cost_max = ai_result.get("ai_analysis", {}).get("cost_max")
            fa.ai_risk_flags = ai_result.get("ai_analysis", {}).get("risk_flags", [])
            fa.ai_raw_response = ai_result
            
            db.commit()
        
        return {
            "message": "Analysis complete",
            "claim_id": claim_id,
            "ai_result": ai_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
