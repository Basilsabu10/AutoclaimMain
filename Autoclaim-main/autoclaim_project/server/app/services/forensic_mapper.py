"""
Helper functions to map comprehensive forensic analysis data to database.
Works with comprehensive ForensicAnalysis model after v2.0 migration.
"""

from typing import Dict, Any


def map_forensic_to_db(ai_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map comprehensive Groq AI response to ForensicAnalysis fields.
    
    This version populates ALL comprehensive forensic fields in the database model.
    
    Args:
        ai_result: Complete analysis result from AI orchestrator
        
    Returns:
        dict of field names → values for ForensicAnalysis model
    """
    
    # Extract sub-sections from orchestrator output
    metadata = ai_result.get("metadata", {})
    ocr = ai_result.get("ocr", {})
    yolo_damage = ai_result.get("yolo_damage", {})
    ai_analysis = ai_result.get("ai_analysis", {})
    
    # The AI analysis might be nested OR flat depending on the Groq response
    # Try to extract comprehensive sections if they exist, otherwise use flat structure
    forensic_analysis = ai_analysis.get("forensic_analysis", {})
    vehicle_identification = ai_analysis.get("vehicle_identification", {})
    damage_assessment = ai_analysis.get("damage_assessment", {})
    pre_existing = ai_analysis.get("pre_existing_damage", {})
    contextual = ai_analysis.get("contextual_analysis", {})
    cross_verification = ai_analysis.get("cross_verification", {})
    final_assessment = ai_analysis.get("final_assessment", {})
    
    # Build comprehensive field mapping with fallbacks to flat structure
    forensic_data = {
        # EXIF Metadata
        "exif_timestamp": metadata.get("timestamp"),
        "exif_gps_lat": metadata.get("gps_lat"),
        "exif_gps_lon": metadata.get("gps_lon"),
        "exif_location_name": metadata.get("location_name"),
        "exif_camera_make": metadata.get("camera_make"),
        "exif_camera_model": metadata.get("camera_model"),
        
        # OCR Results
        "ocr_plate_text": ocr.get("plate_text"),
        "ocr_plate_confidence": ocr.get("confidence"),
        "ocr_raw_texts": ocr.get("raw_texts", []),
        
        # YOLOv8 Detection
        "yolo_damage_detected": yolo_damage.get("damage_detected", False),
        "yolo_detections": yolo_damage.get("detections", []),
        "yolo_severity": yolo_damage.get("severity"),
        "yolo_summary": yolo_damage.get("summary"),
        
        # Forensic Analysis (Image Integrity)
        "authenticity_score": forensic_analysis.get("authenticity_score"),
        "forgery_detected": forensic_analysis.get("digital_manipulation_detected", False),
        "forgery_indicators": forensic_analysis.get("forgery_indicators", []),
        "digital_manipulation_confidence": forensic_analysis.get("manipulation_confidence"),
        
        # Vehicle Identification (with fallbacks)
        "vehicle_make": (
            vehicle_identification.get("make") or 
            vehicle_identification.get("vehicle_details", {}).get("make") or
            ai_analysis.get("vehicle_make")
        ),
        "vehicle_model": (
            vehicle_identification.get("model") or 
            vehicle_identification.get("vehicle_details", {}).get("model") or
            ai_analysis.get("vehicle_model")
        ),
        "vehicle_year": str(
            vehicle_identification.get("year") or 
            vehicle_identification.get("vehicle_details", {}).get("year") or
            ai_analysis.get("vehicle_year") or
            ""
        ),
        "vehicle_color": (
            vehicle_identification.get("color") or 
            vehicle_identification.get("vehicle_details", {}).get("color") or
            ai_analysis.get("vehicle_color")
        ),
        "vehicle_identification_confidence": (
            vehicle_identification.get("identification_confidence") or 
            vehicle_identification.get("vehicle_details", {}).get("confidence")
        ),
        
        # License Plate (with OCR fallback)
        "license_plate_detected": (
            vehicle_identification.get("license_plate", {}).get("detected", False) or
            bool(ocr.get("plate_text"))
        ),
        "license_plate_text": (
            vehicle_identification.get("license_plate", {}).get("text") or
            ocr.get("plate_text")
        ),
        "license_plate_confidence": (
            vehicle_identification.get("license_plate", {}).get("confidence") or
            ocr.get("confidence")
        ),
        "license_plate_match_status": vehicle_identification.get("license_plate", {}).get("match_status"),
        
        # VIN
        "vin_detected": vehicle_identification.get("vin_detected", False),
        "vin_number": vehicle_identification.get("vin_number"),
        
        # Enhanced Damage Assessment (with YOLO and flat fallbacks)
        "ai_damage_detected": (
            damage_assessment.get("damage_detected", False) or
            yolo_damage.get("damage_detected", False) or
            ai_analysis.get("damage_detected", False)
        ),
        "ai_damaged_panels": (
            damage_assessment.get("damaged_panels", []) or
            ai_analysis.get("damaged_panels", [])
        ),
        "ai_damage_type": (
            damage_assessment.get("damage_type") or
            ai_analysis.get("damage_type")
        ),
        "ai_severity": (
            damage_assessment.get("overall_severity") or 
            ai_analysis.get("severity") or
            yolo_damage.get("severity")
        ),
        "ai_affected_parts": (
            damage_assessment.get("affected_parts", []) or
            ai_analysis.get("affected_parts", []) or
            yolo_damage.get("affected_parts", [])
        ),
        "ai_structural_damage": damage_assessment.get("structural_damage", False),
        "ai_safety_concerns": damage_assessment.get("safety_concerns", []),
        
        # Cost Estimation (with flat fallbacks)
        "ai_cost_min": (
            damage_assessment.get("estimated_repair_cost", {}).get("min_usd") or 
            ai_analysis.get("cost_min")
        ),
        "ai_cost_max": (
            damage_assessment.get("estimated_repair_cost", {}).get("max_usd") or 
            ai_analysis.get("cost_max")
        ),
        "ai_cost_confidence": damage_assessment.get("estimated_repair_cost", {}).get("confidence"),
        
        # Pre-existing Damage
        "pre_existing_damage_detected": pre_existing.get("detected", False),
        "pre_existing_indicators": pre_existing.get("indicators", []),
        "pre_existing_description": pre_existing.get("description"),
        "pre_existing_confidence": pre_existing.get("confidence"),
        
        # Contextual Analysis
        "location_type": contextual.get("location_type"),
        "weather_conditions": contextual.get("weather_conditions"),
        "lighting_quality": contextual.get("lighting_quality"),
        "photo_quality": contextual.get("photo_quality"),
        "consistent_with_narrative": contextual.get("consistent_with_narrative"),
        
        # Cross-verification
        "narrative_match": cross_verification.get("narrative_match"),
        "policy_match": cross_verification.get("policy_match"),
        "timeline_consistent": cross_verification.get("timeline_consistent"),
        "verification_discrepancies": cross_verification.get("discrepancies", []),
        
        # Risk Assessment (with flat fallbacks)
        "ai_risk_flags": (
            ai_analysis.get("risk_flags", []) or
            final_assessment.get("risk_flags", [])
        ),
        "fraud_probability": (
            final_assessment.get("fraud_probability") or
            ai_analysis.get("fraud_probability")
        ),
        
        # Final Assessment (with flat fallbacks)
        "overall_confidence_score": (
            final_assessment.get("overall_confidence_score") or
            ai_analysis.get("confidence") or
            ai_analysis.get("overall_confidence_score")
        ),
        "ai_recommendation": (
            final_assessment.get("recommendation") or 
            ai_analysis.get("recommendation")
        ),
        "ai_reasoning": (
            final_assessment.get("decision_reasoning") or 
            ai_analysis.get("reasoning") or
            ai_analysis.get("analysis_text")
        ),
        "human_review_priority": final_assessment.get("human_review_priority"),
        "recommended_actions": final_assessment.get("recommended_actions", []),
        
        # Metadata
        "ai_raw_response": ai_result,  # Store complete response
        "ai_provider": ai_analysis.get("provider", "groq"),
        "ai_model": ai_analysis.get("model"),
        "ai_confidence": (
            final_assessment.get("overall_confidence_score") or 
            ai_analysis.get("confidence")
        ),
        "analysis_version": "2.0"
    }
    
    # Remove None values and empty strings/lists to use database defaults
    return {k: v for k, v in forensic_data.items() if v not in (None, "", [])}


def extract_simple_fields(ai_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract simplified fields for Claim table (denormalized for quick access).
    
    Args:
        ai_result: Complete analysis result
        
    Returns:
        dict with simplified fields for Claim model
    """
    ai_analysis = ai_result.get("ai_analysis", {})
    ocr = ai_result.get("ocr", {})
    final_assessment = ai_analysis.get("final_assessment", {})
    damage_assessment = ai_analysis.get("damage_assessment", {})
    
    return {
        "vehicle_number_plate": ocr.get("plate_text"),
        "ai_recommendation": final_assessment.get("recommendation") or ai_analysis.get("recommendation"),
        "estimated_cost_min": damage_assessment.get("estimated_repair_cost", {}).get("min_usd") or ai_analysis.get("cost_min"),
        "estimated_cost_max": damage_assessment.get("estimated_repair_cost", {}).get("max_usd") or ai_analysis.get("cost_max")
    }
