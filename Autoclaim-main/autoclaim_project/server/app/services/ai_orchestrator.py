"""
AI Service Orchestrator - Pure Data Extraction + Rule-Based Decisions.
Combines self-hosted YOLOv8 with Groq for data extraction, then applies Python rules for decisions.
"""

import os
from typing import Dict, Any, List, Optional

# Import individual services
from app.services.exif_service import extract_metadata
from app.services.ocr_service import extract_number_plate

# Import YOLOv8 self-hosted service
try:
    from app.services.yolov8_damage_service import (
        detect_vehicle_damage,
        init_yolo_model,
        get_model_info,
        YOLO_AVAILABLE
    )
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARNING] YOLOv8 service not available")

# Import Groq service for data extraction
try:
    from app.services.groq_service import extract_vehicle_data
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[WARNING] Groq service not available")


def prepare_verification_data(
    extracted_data: Dict[str, Any],
    metadata: Dict[str, Any],
    ocr: Dict[str, Any],
    yolo_damage: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Transform AI extraction results into the format expected by verification_rules.py.
    
    Args:
        extracted_data: Groq extraction results (identity, damage, forensics, scene)
        metadata: EXIF metadata
        ocr: OCR results
        yolo_damage: YOLO detection results
        
    Returns:
        dict structured for VerificationRules.verify_claim()
    """
    identity = extracted_data.get("identity", {})
    damage = extracted_data.get("damage", {})
    forensics = extracted_data.get("forensics", {})
    scene = extracted_data.get("scene", {})
    
    # Build the comprehensive analysis structure
    ai_analysis = {
        # EXIF Metadata
        "exif_metadata": {
            "timestamp": metadata.get("timestamp"),
            "gps_coordinates": {
                "latitude": metadata.get("gps_lat"),
                "longitude": metadata.get("gps_lon"),
            },
            "location_name": metadata.get("location_name"),
            "camera_make": metadata.get("camera_make"),
            "camera_model": metadata.get("camera_model"),
        },
        
        # OCR Data
        "ocr_data": {
            "plate_text": ocr.get("plate_text"),
            "confidence": ocr.get("confidence") or 0.0,
            "chase_number": None,  # Not currently extracted
            "chase_number_confidence": 0.0,
        },
        
        # YOLO Results
        "yolo_results": {
            "yolo_damage_detected": yolo_damage.get("damage_detected", False),
            "yolo_severity": yolo_damage.get("severity", "none"),
            "yolo_detections": yolo_damage.get("detections", []),
        },
        
        # Vehicle Identification
        "vehicle_identification": {
            "make": identity.get("vehicle_make"),
            "model": identity.get("vehicle_model"),
            "year": identity.get("vehicle_year"),
            "color": identity.get("vehicle_color"),
            "detected_confidence": identity.get("identification_confidence", 0.0),
            "license_plate_visible": identity.get("license_plate_visible", False),
            "license_plate_obscured": identity.get("license_plate_obscured", False),
        },
        
        # Forensic Indicators
        "forensic_indicators": {
            "is_screen_recapture": forensics.get("is_screen_recapture", False),
            "has_ui_elements": forensics.get("has_ui_elements", False),
            "has_watermarks": forensics.get("has_watermarks", False),
            "image_quality": forensics.get("image_quality", "high"),
            "is_blurry": forensics.get("is_blurry", False),
            "multiple_light_sources": forensics.get("multiple_light_sources", False),
            "shadows_inconsistent": forensics.get("shadows_inconsistent", False),
        },
        
        # Authenticity Indicators
        "authenticity_indicators": {
            "stock_photo_likelihood": "unknown",  # Not currently available
            "editing_detected": False,
            "lighting_consistent": not forensics.get("multiple_light_sources", False),
            "shadows_natural": not forensics.get("shadows_inconsistent", False),
            "compression_uniform": True,
        },
        
        # Damage Assessment
        "damage_assessment": {
            "ai_damage_detected": damage.get("damage_detected", False),
            "ai_severity": damage.get("severity", "none"),
            "damaged_panels": damage.get("damaged_panels", []),
            "damage_type": damage.get("damage_type"),
            "severity_score": damage.get("severity_score", 0.0),
            "airbags_deployed": damage.get("airbags_deployed", False),
            "fluid_leaks_visible": damage.get("fluid_leaks_visible", False),
            "parts_missing": damage.get("parts_missing", False),
            "ai_cost_min": damage.get("cost_estimate_min"),
            "ai_cost_max": damage.get("cost_estimate_max"),
        },
        
        # Pre-existing Indicators
        "pre_existing_indicators": {
            "rust_detected": damage.get("is_rust_present", False),
            "paint_fading": damage.get("is_paint_faded_around_damage", False),
            "dirt_accumulation": damage.get("is_dirt_in_damage", False),
            "old_repairs_visible": False,
        },
        
        # Narrative Consistency
        "narrative_consistency": {
            "visual_evidence_matches": scene.get("consistent_with_narrative", True),
            "inconsistencies": [],
        },
        
        # Multi-image Analysis (placeholder - would need orchestrator to aggregate)
        "multi_image_analysis": {},
    }
    
    return ai_analysis



def analyze_claim(
    damage_image_paths: List[str],
    front_image_path: Optional[str],
    description: str,
    claim_amount: int = 0,
    policy_data: Optional[Dict] = None,
    claim_history: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Perform complete claim analysis using AI extraction + rule-based decisions.
    
    Pipeline:
    1. Extract EXIF metadata (timestamp, GPS) from images
    2. Extract number plate from front image using OCR
    3. Detect damage using self-hosted YOLOv8 (FAST, FREE)
    4. Extract vehicle data using Groq (identity, damage, forensics, scene)
    5. Apply comprehensive rule-based verification (16 checks across 5 phases)
    
    Args:
        damage_image_paths: List of damage photo paths
        front_image_path: Front view image for plate detection
        description: User's claim description
        claim_amount: Claimed repair/loss amount in ₹
        policy_data: Policy data for cross-checking (vehicle, dates, coverage)
        claim_history: List of prior claims for duplicate detection
        
    Returns:
        dict with metadata, ocr, yolo_damage, ai_analysis, and verification results
    """
    from app.services.verification_rules import VerificationRules
    
    result = {
        "metadata": {
            "timestamp": None,
            "gps_lat": None,
            "gps_lon": None,
            "location_name": None,
            "camera_type": None,
            "filename_parsed": False,
            "source": None
        },
        "ocr": {
            "plate_text": None,
            "confidence": None
        },
        "yolo_damage": {
            "success": False,
            "damage_detected": False,
            "detections": [],
            "severity": "none",
            "affected_parts": [],
            "summary": "YOLOv8 not run"
        },
        "ai_analysis": {
            "damage_type": None,
            "severity": None,
            "affected_parts": [],
            "recommendation": "review",
            "cost_min": None,
            "cost_max": None,
            "analysis_text": None,
            "risk_flags": [],
            "provider": None
        },
        "verification": None  # Will hold VerificationResult
    }
    
    # 1. Extract EXIF/filename metadata from first available image
    if damage_image_paths:
        for path in damage_image_paths:
            if os.path.exists(path):
                exif = extract_metadata(path)
                if exif.get("timestamp") or exif.get("gps_lat"):
                    result["metadata"] = exif
                    break
                elif exif.get("filename_parsed"):
                    result["metadata"] = exif
                    break
    
    # 2. Extract number plate from front image
    if front_image_path and os.path.exists(front_image_path):
        result["ocr"] = extract_number_plate(front_image_path)
    
    # 3. YOLOv8 damage detection (self-hosted, FREE, FAST)
    if YOLO_AVAILABLE and damage_image_paths:
        for path in damage_image_paths:
            if os.path.exists(path):
                yolo_result = detect_vehicle_damage(path)
                if yolo_result["success"]:
                    result["yolo_damage"] = yolo_result
                    print(f"[YOLOv8] {yolo_result.get('summary', 'Detection complete')}")
                    break
                else:
                    result["yolo_damage"]["summary"] = yolo_result.get("error", "YOLOv8 failed")
    else:
        result["yolo_damage"]["summary"] = "YOLOv8 not available" if not YOLO_AVAILABLE else "No images provided"
    
    # 4. Groq data extraction - ALWAYS RUN for insurance claims
    if GROQ_AVAILABLE:
        all_images = (damage_image_paths or []).copy()
        if front_image_path:
            all_images.append(front_image_path)
        
        print("[AI] Running Groq data extraction...")
        extraction_result = extract_vehicle_data(
            image_paths=all_images,
            description=description,
            policy_data=policy_data
        )
        
        if extraction_result.get("success"):
            # Store extraction results
            result["ai_analysis"] = {
                **extraction_result,
                "provider": "groq",
            }
            
            # 5. Apply comprehensive rule-based verification
            try:
                # Prepare data for verification engine
                verification_data = prepare_verification_data(
                    extracted_data=extraction_result,
                    metadata=result["metadata"],
                    ocr=result["ocr"],
                    yolo_damage=result["yolo_damage"]
                )
                
                # Run verification engine
                verification_engine = VerificationRules()
                verification_result = verification_engine.verify_claim(
                    claim_amount=claim_amount,
                    ai_analysis=verification_data,
                    policy_data=policy_data or {},
                    history=claim_history
                )
                
                # Store verification results
                result["verification"] = verification_result.to_dict()
                
                print(f"[Verification] Status: {verification_result.status}, "
                      f"Confidence: {verification_result.confidence_level}, "
                      f"Score: {verification_result.severity_score:.1f}, "
                      f"Passed: {len(verification_result.passed_checks)}, "
                      f"Failed: {len(verification_result.failed_checks)}")
                
                # Also add key verification fields to ai_analysis for backward compatibility
                result["ai_analysis"]["verification_status"] = verification_result .status
                result["ai_analysis"]["ai_recommendation"] = verification_result.status
                result["ai_analysis"]["overall_confidence_score"] = verification_result.confidence_score
                result["ai_analysis"]["fraud_probability"] = "HIGH" if verification_result.status == "REJECTED" else "MEDIUM" if verification_result.status == "FLAGGED" else "LOW"
                result["ai_analysis"]["ai_risk_flags"] = [f.rule_id for f in verification_result.failed_checks]
                result["ai_analysis"]["human_review_priority"] = "CRITICAL" if verification_result.status == "REJECTED" else "HIGH" if verification_result.requires_human_review else "LOW"
                result["ai_analysis"]["ai_reasoning"] = verification_result.decision_reason
                
            except Exception as e:
                print(f"[Verification] Error: {e}")
                result["verification"] = {"error": str(e)}
                # Fall back to extraction-only results
                result["ai_analysis"]["ai_reasoning"] = f"Verification engine error: {e}"
        else:
            result["ai_analysis"]["analysis_text"] = extraction_result.get("error", "Extraction failed")
            result["ai_analysis"]["provider"] = "groq"
    else:
        # Groq not available - use YOLO results if available
        if YOLO_AVAILABLE and result["yolo_damage"].get("damage_detected"):
            result["ai_analysis"]["provider"] = "yolo"
            result["ai_analysis"]["severity"] = result["yolo_damage"].get("severity")
            result["ai_analysis"]["affected_parts"] = result["yolo_damage"].get("affected_parts", [])
            result["ai_analysis"]["analysis_text"] = result["yolo_damage"].get("summary")
        else:
            result["ai_analysis"]["analysis_text"] = "No AI service available for damage analysis"
            result["ai_analysis"]["provider"] = "none"
    
    return result



def initialize_services() -> Dict[str, bool]:
    """Initialize all AI services and return status."""
    status = {
        "yolo": False,
        "groq": GROQ_AVAILABLE
    }
    
    # Initialize YOLOv8 model on startup
    if YOLO_AVAILABLE:
        status["yolo"] = init_yolo_model()
        
        # Print model info
        info = get_model_info()
        gpu_status = "GPU ✓" if info["gpu_info"].get("available") else "CPU (slower)"
        print(f"[AI Services] YOLOv8: {status['yolo']} ({gpu_status}), Groq: {status['groq']}")
    else:
        print(f"[AI Services] YOLOv8: {status['yolo']}, Groq: {status['groq']}")
    
    return status
