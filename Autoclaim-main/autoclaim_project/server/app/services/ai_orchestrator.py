"""
AI Service Orchestrator - YOLOv8 + Groq Hybrid.
Combines self-hosted YOLOv8 for fast damage detection with Groq for detailed analysis.
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

# Import Groq service for detailed analysis
try:
    from app.services.groq_service import analyze_damage as groq_analyze
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[WARNING] Groq service not available")


def analyze_claim(
    damage_image_paths: List[str],
    front_image_path: Optional[str],
    description: str
) -> Dict[str, Any]:
    """
    Perform complete claim analysis using YOLOv8 + Groq hybrid approach.
    
    Pipeline:
    1. Extract EXIF metadata (timestamp, GPS) from images
    2. Extract number plate from front image using OCR
    3. Detect damage using self-hosted YOLOv8 (FAST, FREE)
    4. Analyze damage using Groq for detailed reasoning (when damage detected)
    
    Args:
        damage_image_paths: List of damage photo paths
        front_image_path: Front view image for plate detection
        description: User's claim description
        
    Returns:
        dict with metadata, ocr, yolo_damage, and ai_analysis results
    """
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
        }
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
    
    # 4. Groq detailed analysis - ALWAYS RUN for insurance claims
    # Note: YOLO base model (yolov8n) only detects objects (car, person), NOT damage
    # We need Groq's vision model for actual damage assessment
    if GROQ_AVAILABLE:
        all_images = (damage_image_paths or []).copy()
        if front_image_path:
            all_images.append(front_image_path)
        
        # Pass YOLO context to Groq if available (for reference)
        yolo_context = result["yolo_damage"] if result["yolo_damage"]["success"] else None
        
        print("[AI] Running Groq damage analysis...")
        ai_result = groq_analyze(all_images, description, yolo_context)
        ai_result["provider"] = "groq"
        result["ai_analysis"] = ai_result
        
        # If YOLO detected damage, merge results for best accuracy
        if yolo_context and yolo_context.get("damage_detected"):
            # Merge YOLO and Groq results for best accuracy
            if not ai_result.get("severity"):
                ai_result["severity"] = yolo_context.get("severity", "minor")
            if not ai_result.get("affected_parts"):
                ai_result["affected_parts"] = yolo_context.get("affected_parts", [])
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
