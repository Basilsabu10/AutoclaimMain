"""
YOLO Service for Vehicle and Damage Detection.
Uses YOLOv8 for object detection.
"""

import os
from typing import Dict, Any
from pathlib import Path

from app.core.config import settings

# Try to import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARNING] ultralytics not installed. Run: pip install ultralytics")

# Model instance
yolo_model = None


def init_yolo(model_path: str = None) -> bool:
    """
    Initialize YOLO model.
    
    Args:
        model_path: Path to model file (defaults to config setting)
    
    Returns:
        True if initialization successful
    """
    global yolo_model
    
    if not YOLO_AVAILABLE:
        print("[ERROR] YOLO not available")
        return False
    
    if yolo_model is not None:
        return True
    
    if model_path is None:
        model_path = settings.YOLO_MODEL_PATH
        
    # If path doesn't exist, try in current directory
    if not os.path.exists(model_path):
        model_path = "yolov8n.pt"
    
    try:
        yolo_model = YOLO(model_path)
        print(f"[OK] YOLO model loaded: {model_path}")
        return True
    except Exception as e:
        print(f"[ERROR] YOLO init failed: {e}")
        return False


def detect_objects(image_path: str, conf_threshold: float = 0.25) -> Dict[str, Any]:
    """
    Detect objects in an image using YOLO.
    
    Args:
        image_path: Path to the image
        conf_threshold: Minimum confidence threshold
        
    Returns:
        dict with detection results
    """
    result = {
        "success": False,
        "detections": [],
        "vehicle_detected": False,
        "damage_regions": [],
        "summary": ""
    }
    
    if not os.path.exists(image_path):
        result["summary"] = f"Image not found: {image_path}"
        return result
    
    if not init_yolo():
        result["summary"] = "YOLO model not available"
        return result
    
    try:
        detections = yolo_model(image_path, conf=conf_threshold, verbose=False)
        
        detected_objects = []
        vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
        
        for detection in detections:
            boxes = detection.boxes
            
            for i, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                cls_name = detection.names[cls_id]
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()
                
                obj = {
                    "class": cls_name,
                    "confidence": round(confidence, 3),
                    "bbox": [round(x, 1) for x in bbox]
                }
                detected_objects.append(obj)
                
                if cls_name.lower() in vehicle_classes:
                    result["vehicle_detected"] = True
        
        result["detections"] = detected_objects
        result["success"] = True
        
        if detected_objects:
            obj_counts = {}
            for obj in detected_objects:
                cls = obj["class"]
                obj_counts[cls] = obj_counts.get(cls, 0) + 1
            
            summary_parts = [f"{count} {cls}" for cls, count in obj_counts.items()]
            result["summary"] = f"Detected: {', '.join(summary_parts)}"
        else:
            result["summary"] = "No objects detected"
            
    except Exception as e:
        result["summary"] = f"Detection failed: {str(e)}"
        
    return result


def analyze_vehicle_damage(image_path: str) -> Dict[str, Any]:
    """
    Analyze vehicle damage regions.
    Uses standard YOLO to detect the vehicle.
    
    Returns:
        dict with vehicle analysis
    """
    result = {
        "vehicle_found": False,
        "vehicle_type": None,
        "vehicle_bbox": None,
        "potential_damage": False,
        "analysis_notes": []
    }
    
    detection = detect_objects(image_path)
    
    if not detection["success"]:
        result["analysis_notes"].append(detection["summary"])
        return result
    
    for obj in detection["detections"]:
        if obj["class"].lower() in ['car', 'truck', 'bus', 'motorcycle']:
            result["vehicle_found"] = True
            result["vehicle_type"] = obj["class"]
            result["vehicle_bbox"] = obj["bbox"]
            result["analysis_notes"].append(
                f"Vehicle detected: {obj['class']} ({obj['confidence']*100:.1f}% confidence)"
            )
            break
    
    if not result["vehicle_found"]:
        result["analysis_notes"].append("No vehicle detected - may be a close-up damage shot")
        result["potential_damage"] = True
    else:
        result["analysis_notes"].append("Vehicle detected - image suitable for damage analysis")
    
    return result
