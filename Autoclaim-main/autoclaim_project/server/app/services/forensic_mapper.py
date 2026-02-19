"""
Helper functions to map AI extracted data to database.
Works with v3.0 ForensicAnalysis model - Pure extraction + rule-based decisions.
"""

from typing import Dict, Any


def map_forensic_to_db(ai_result: Dict[str, Any], policy_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Map AI extracted data to ForensicAnalysis fields.
    
    AI now returns structured extraction:
    - identity: vehicle details, license plate, detected objects
    - damage: damage type, severity score, affected panels, indicators
    - forensics: image integrity checks, manipulation detection
    - scene: location, weather, time of day, environment
    
    Args:
        ai_result: Complete analysis result from AI orchestrator
        
    Returns:
        dict of field names → values for ForensicAnalysis model
    """
    
    # Extract sub-sections from Groq extraction
    # Logic updated to handle nested 'ai_analysis' structure from orchestrator
    ai_analysis_data = ai_result.get("ai_analysis", {})
    
    identity = ai_analysis_data.get("identity") or ai_result.get("identity", {})
    damage = ai_analysis_data.get("damage") or ai_result.get("damage", {})
    forensics = ai_analysis_data.get("forensics") or ai_result.get("forensics", {})
    scene = ai_analysis_data.get("scene") or ai_result.get("scene", {})
    
    # Extract orchest rator sections (metadata, OCR, YOLO)
    metadata = ai_result.get("metadata", {})
    ocr = ai_result.get("ocr", {})
    yolo_damage = ai_result.get("yolo_damage", {})
    
    # Extract computed decisions (from rule-based logic or verification engine)
    decisions = ai_result.get("decisions", {})
    verification = ai_result.get("verification", {})
    
    # Use verification results if available (v4.0), otherwise fall back to decisions (v3.0)
    if verification and not verification.get("error"):
        # Extract verification data
        ai_recommendation_value = verification.get("status")  # APPROVED, FLAGGED, REJECTED
        fraud_probability_value = _map_status_to_fraud_probability(verification.get("status"))
        fraud_score_value = verification.get("severity_score", 0.0) / 10.0  # Scale to 0-1
        confidence_score_value = verification.get("confidence_score")
        risk_flags_value = [failure["rule_id"] for failure in verification.get("failed_checks", [])]
        reasoning_value = verification.get("decision_reason")
        review_priority_value = "CRITICAL" if verification.get("status") == "REJECTED" else \
                                 "HIGH" if verification.get("requires_human_review") else \
                                 "LOW" if verification.get("status") == "APPROVED" else "MEDIUM"
    else:
        # Fall back to legacy decisions format
        ai_recommendation_value = decisions.get("ai_recommendation")
        fraud_probability_value = decisions.get("fraud_probability")
        fraud_score_value = decisions.get("fraud_score")
        confidence_score_value = decisions.get("overall_confidence_score")
        risk_flags_value = decisions.get("ai_risk_flags", [])
        reasoning_value = decisions.get("ai_reasoning")
        review_priority_value = decisions.get("human_review_priority")
    
    # Build field mapping
    forensic_data = {
        # ============================================================
        # EXIF METADATA
        # ============================================================
        "exif_timestamp": metadata.get("timestamp"),
        "exif_gps_lat": metadata.get("gps_lat"),
        "exif_gps_lon": metadata.get("gps_lon"),
        "exif_location_name": metadata.get("location_name"),
        "exif_camera_make": metadata.get("camera_make"),
        "exif_camera_model": metadata.get("camera_model"),
        
        # ============================================================
        # OCR RESULTS
        # ============================================================
        "ocr_plate_text": ocr.get("plate_text"),
        "ocr_plate_confidence": ocr.get("confidence"),
        "ocr_raw_texts": ocr.get("raw_texts", []),
        
        # ============================================================
        # YOLO DETECTION
        # ============================================================
        "yolo_damage_detected": yolo_damage.get("damage_detected", False),
        "yolo_detections": yolo_damage.get("detections", []),
        "yolo_severity": yolo_damage.get("severity"),
        "yolo_summary": yolo_damage.get("summary"),
        
        # ============================================================
        # IDENTITY EXTRACTION
        # ============================================================
        "detected_objects": identity.get("detected_objects", []),
        "vehicle_make": identity.get("vehicle_make"),
        "vehicle_model": identity.get("vehicle_model"),
        "vehicle_year": identity.get("vehicle_year"),
        "vehicle_color": identity.get("vehicle_color"),
        "license_plate_text": identity.get("license_plate_text") or ocr.get("plate_text"),
        "license_plate_visible": identity.get("license_plate_visible", False),
        "license_plate_obscured": identity.get("license_plate_obscured", False),
        "license_plate_detected": identity.get("license_plate_visible", False) or bool(ocr.get("plate_text")),
        
        # ============================================================
        # DAMAGE EXTRACTION
        # ============================================================
        "ai_damage_detected": damage.get("damage_detected", False),
        "ai_damage_type": damage.get("damage_type"),
        "damage_severity_score": damage.get("severity_score"),
        "ai_damaged_panels": damage.get("damaged_panels", []),
        "impact_point": damage.get("impact_point"),
        "paint_damage": damage.get("paint_damage", False),
        "glass_damage": damage.get("glass_damage", False),
        "is_rust_present": damage.get("is_rust_present", False),
        "rust_locations": damage.get("rust_locations", []),
        "is_dirt_in_damage": damage.get("is_dirt_in_damage", False),
        "is_paint_faded_around_damage": damage.get("is_paint_faded_around_damage", False),
        "airbags_deployed": damage.get("airbags_deployed", False),
        "fluid_leaks_visible": damage.get("fluid_leaks_visible", False),
        "parts_missing": damage.get("parts_missing", False),
        
        # Computed severity label and structural damage flag
        "ai_severity": _compute_severity_label(damage.get("severity_score")),
        "ai_affected_parts": damage.get("damaged_panels", []),  # backward compat alias
        "ai_structural_damage": (
            damage.get("airbags_deployed", False) or
            damage.get("fluid_leaks_visible", False) or
            (damage.get("severity_score") or 0) >= 8
        ),
        
        # Cost estimation from AI
        "ai_cost_min": damage.get("estimated_cost_range_INR", {}).get("min"),
        "ai_cost_max": damage.get("estimated_cost_range_INR", {}).get("max"),
        
        # ============================================================
        # FORENSICS EXTRACTION (Image Integrity)
        # ============================================================
        "is_screen_recapture": forensics.get("is_screen_recapture", False),
        "has_ui_elements": forensics.get("has_ui_elements", False),
        "has_watermarks": forensics.get("has_watermarks", False),
        "image_quality": forensics.get("image_quality"),
        "is_blurry": forensics.get("is_blurry", False),
        "lighting_quality": forensics.get("lighting_quality"),
        "multiple_light_sources": forensics.get("multiple_light_sources", False),
        "shadows_inconsistent": forensics.get("shadows_inconsistent", False),
        
        "forgery_detected": forensics.get("is_screen_recapture", False) or forensics.get("has_ui_elements", False),
        "forgery_indicators": _build_forgery_indicators(forensics),
        "authenticity_score": _compute_authenticity_score(forensics),
        
        # ============================================================
        # SCENE EXTRACTION
        # ============================================================
        "location_type": scene.get("location_type"),
        "time_of_day": scene.get("time_of_day"),
        "weather_visible": scene.get("weather_visible"),
        "weather_conditions": scene.get("weather_visible"),  # Alias
        "debris_visible": scene.get("debris_visible", False),
        "other_vehicles_visible": scene.get("other_vehicles_visible", False),
        "is_moving_traffic": scene.get("is_moving_traffic", False),
        "photo_quality": forensics.get("image_quality"),  # Alias
        
        # ============================================================
        # PRE-EXISTING DAMAGE (Computed from indicators)
        # ============================================================
        "pre_existing_damage_detected": damage.get("is_rust_present", False) or 
                                        damage.get("is_dirt_in_damage", False) or 
                                        damage.get("is_paint_faded_around_damage", False),
        "pre_existing_indicators": _build_pre_existing_indicators(damage),
        "pre_existing_description": _build_pre_existing_description(damage),
        "pre_existing_confidence": _compute_pre_existing_confidence(damage),
        
        # ============================================================
        # RULE-BASED DECISIONS / VERIFICATION RESULTS (Computed)
        # ============================================================
        "ai_risk_flags": risk_flags_value,
        "fraud_probability": fraud_probability_value,
        "fraud_score": fraud_score_value,
        "overall_confidence_score": confidence_score_value,
        "ai_recommendation": ai_recommendation_value,
        "ai_reasoning": reasoning_value,
        "human_review_priority": review_priority_value,
        
        # ============================================================
        # METADATA
        # ============================================================
        "ai_raw_response": ai_result,  # Store complete response
        "ai_provider": ai_result.get("provider", "groq"),
        "ai_model": ai_result.get("model"),
        "analysis_version": "4.0" if verification and not verification.get("error") else "3.0",
        
        # License plate match status (compare OCR vs policy)
        "license_plate_match_status": _compute_plate_match(
            ocr.get("plate_text") or identity.get("license_plate_text"),
            policy_data
        ),
    }
    
    # Remove None values and empty strings/lists to use database defaults
    return {k: v for k, v in forensic_data.items() if v not in (None, "", [])}


def _build_forgery_indicators(forensics: Dict[str, Any]) -> list:
    """Build list of forgery indicators from extracted forensics data."""
    indicators = []
    
    if forensics.get("is_screen_recapture"):
        indicators.append("SCREEN_RECAPTURE")
    if forensics.get("has_ui_elements"):
        indicators.append("UI_ELEMENTS")
    if forensics.get("has_watermarks"):
        indicators.append("WATERMARKS")
    if forensics.get("shadows_inconsistent"):
        indicators.append("INCONSISTENT_SHADOWS")
    if forensics.get("multiple_light_sources"):
        indicators.append("MULTIPLE_LIGHT_SOURCES")
    
    return indicators


def _build_pre_existing_indicators(damage: Dict[str, Any]) -> list:
    """Build list of pre-existing damage indicators from extracted damage data."""
    indicators = []
    
    if damage.get("is_rust_present"):
        indicators.append("RUST")
        if damage.get("rust_locations"):
            indicators.extend([f"RUST_{loc.upper()}" for loc in damage.get("rust_locations", [])])
    
    if damage.get("is_dirt_in_damage"):
        indicators.append("DIRT_IN_DAMAGE")
    
    if damage.get("is_paint_faded_around_damage"):
        indicators.append("FADED_PAINT")
    
    return indicators


def extract_simple_fields(ai_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract simplified fields for Claim table (denormalized for quick access).
    
    Args:
        ai_result: Complete analysis result
        
    Returns:
        dict with simplified fields for Claim model
    """
    ocr = ai_result.get("ocr", {})
    identity = ai_result.get("identity", {})
    damage = ai_result.get("damage", {})
    decisions = ai_result.get("decisions", {})
    verification = ai_result.get("verification", {})
    
    # Use verification if available
    if verification and not verification.get("error"):
        ai_recommendation = verification.get("status")
    else:
        ai_recommendation = decisions.get("ai_recommendation")
    
    return {
        "vehicle_number_plate": ocr.get("plate_text") or identity.get("license_plate_text"),
        "ai_recommendation": ai_recommendation,
        "estimated_cost_min": damage.get("estimated_cost_range_INR", {}).get("min"),
        "estimated_cost_max": damage.get("estimated_cost_range_INR", {}).get("max")
    }


def _map_status_to_fraud_probability(status: str) -> str:
    """
    Map verification status to fraud probability category.
    
    Args:
        status: Verification status (APPROVED, FLAGGED, REJECTED)
        
    Returns:
        Fraud probability category (VERY_LOW, LOW, MEDIUM, HIGH)
    """
    if status == "REJECTED":
        return "HIGH"
    elif status == "FLAGGED":
        return "MEDIUM"
    elif status == "APPROVED":
        return "VERY_LOW"
    else:
        return "LOW"


def _compute_severity_label(score) -> str:
    """
    Map severity_score (0-10) to a human-readable label.
    """
    if score is None:
        return None
    score = float(score)
    if score <= 0:
        return "none"
    elif score <= 3:
        return "minor"
    elif score <= 6:
        return "moderate"
    elif score <= 8:
        return "severe"
    else:
        return "totaled"


def _compute_authenticity_score(forensics: Dict[str, Any]) -> float:
    """
    Compute an authenticity score (0-100) from forensic indicators.
    Starts at 100 and deducts points for red flags.
    """
    score = 100.0
    
    if forensics.get("is_screen_recapture"):
        score -= 30
    if forensics.get("has_ui_elements"):
        score -= 20
    if forensics.get("has_watermarks"):
        score -= 10
    if forensics.get("shadows_inconsistent"):
        score -= 15
    if forensics.get("multiple_light_sources"):
        score -= 10
    if forensics.get("is_blurry"):
        score -= 5
    if (forensics.get("image_quality") or "").lower() == "low":
        score -= 10
    
    return max(0.0, score)


def _build_pre_existing_description(damage: Dict[str, Any]) -> str:
    """
    Build a human-readable description of pre-existing damage indicators.
    """
    parts = []
    
    if damage.get("is_rust_present"):
        locs = damage.get("rust_locations", [])
        if locs:
            parts.append(f"Rust detected on {', '.join(locs)}")
        else:
            parts.append("Rust detected on damaged area")
    
    if damage.get("is_dirt_in_damage"):
        parts.append("Dirt accumulation found inside damaged area, suggesting the damage is not recent")
    
    if damage.get("is_paint_faded_around_damage"):
        parts.append("Paint fading observed around the damaged area, indicating prolonged exposure")
    
    return ". ".join(parts) + "." if parts else None


def _compute_pre_existing_confidence(damage: Dict[str, Any]) -> float:
    """
    Compute a confidence percentage based on how many pre-existing indicators are present.
    """
    indicators = [
        damage.get("is_rust_present", False),
        damage.get("is_dirt_in_damage", False),
        damage.get("is_paint_faded_around_damage", False),
    ]
    count = sum(1 for i in indicators if i)
    if count == 0:
        return None
    # 1 indicator = 40%, 2 = 70%, 3 = 95%
    return {1: 40.0, 2: 70.0, 3: 95.0}[count]


def _compute_plate_match(detected_plate: str, policy_data: Dict[str, Any] = None) -> str:
    """
    Compare detected plate text against policy vehicle registration.
    Returns MATCH, MISMATCH, or UNKNOWN.
    """
    if not detected_plate:
        return "UNKNOWN"
    if not policy_data or not policy_data.get("vehicle_registration"):
        return "UNKNOWN"
    
    # Normalize: strip spaces, dashes, uppercase
    norm_detected = detected_plate.upper().replace(" ", "").replace("-", "")
    norm_policy = policy_data["vehicle_registration"].upper().replace(" ", "").replace("-", "")
    
    if norm_detected == norm_policy:
        return "MATCH"
    # Partial match — if one contains the other (handles OCR truncation)
    elif norm_detected in norm_policy or norm_policy in norm_detected:
        return "MATCH"
    else:
        return "MISMATCH"
