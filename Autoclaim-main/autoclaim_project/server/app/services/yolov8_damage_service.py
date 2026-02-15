"""
Self-hosted YOLOv8 service for vehicle damage detection.
Runs locally with GPU acceleration - no API costs.
"""
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Check for ultralytics availability
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARNING] YOLOv8 not available. Run: pip install ultralytics torch")

# Global model instance (loaded once on startup)
damage_model = None
MODEL_INITIALIZED = False


def check_gpu_available() -> Dict[str, Any]:
    """Check if CUDA GPU is available for acceleration."""
    if not YOLO_AVAILABLE:
        return {"available": False, "reason": "ultralytics not installed"}
    
    try:
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            return {
                "available": True,
                "device": torch.cuda.get_device_name(0),
                "memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                "cuda_version": torch.version.cuda
            }
        else:
            return {
                "available": False,
                "reason": "CUDA not available - will use CPU (slower)",
                "device": "cpu"
            }
    except Exception as e:
        return {"available": False, "reason": str(e), "device": "cpu"}


def init_yolo_model(model_name: str = "yolov8n.pt") -> bool:
    """
    Initialize YOLOv8 model on startup.
    
    Args:
        model_name: Model filename or Hugging Face repo
        
    Returns:
        bool: Success status
    """
    global damage_model, MODEL_INITIALIZED
    
    if not YOLO_AVAILABLE:
        print("[ERROR] Cannot initialize YOLO - ultralytics not installed")
        return False
    
    if MODEL_INITIALIZED and damage_model is not None:
        print("[INFO] YOLOv8 model already initialized")
        return True
    
    try:
        # Check GPU
        gpu_info = check_gpu_available()
        print(f"[INFO] GPU Status: {gpu_info}")
        
        # Try to download specialized car damage model from Hugging Face
        try:
            from huggingface_hub import hf_hub_download
            
            print("[INFO] Downloading specialized car damage model from Hugging Face...")
            model_path = hf_hub_download(
                repo_id="nezahatkorkmaz/car-damage-level-detection-yolov8",
                filename="best.pt",
                cache_dir="./models"
            )
            damage_model = YOLO(model_path)
            print(f"[OK] YOLOv8 car damage model loaded: {model_path}")
        except Exception as e:
            print(f"[WARNING] Could not load specialized model: {e}")
            print("[INFO] Falling back to base YOLOv8 model...")
            damage_model = YOLO(model_name)
            print(f"[OK] Base YOLOv8 model loaded: {model_name}")
        
        # Set device (GPU if available, else CPU)
        if gpu_info["available"]:
            damage_model.to('cuda')
            print(f"[OK] Model running on GPU: {gpu_info['device']}")
        else:
            print(f"[INFO] Model running on CPU (slower)")
        
        MODEL_INITIALIZED = True
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize YOLOv8: {e}")
        import traceback
        traceback.print_exc()
        return False


def detect_vehicle_damage(image_path: str, conf_threshold: float = 0.25) -> Dict[str, Any]:
    """
    Detect vehicle damage using self-hosted YOLOv8.
    
    Args:
        image_path: Path to the damage image
        conf_threshold: Confidence threshold (0.0 to 1.0)
        
    Returns:
        dict with damage detection results
    """
    if not YOLO_AVAILABLE:
        return {
            "success": False,
            "error": "YOLOv8 not available - install ultralytics"
        }
    
    if damage_model is None:
        return {
            "success": False,
            "error": "YOLOv8 model not initialized - call init_yolo_model() first"
        }
    
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image not found: {image_path}"
        }
    
    try:
        # Run inference
        results = damage_model(image_path, conf=conf_threshold, verbose=False)
        
        # Extract detections
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id] if class_id in result.names else "unknown"
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Calculate area percentage
                    area_pct = calculate_area_percentage(bbox, result.orig_shape)
                    
                    detection = {
                        "class_name": class_name,
                        "class_id": class_id,
                        "confidence": confidence,
                        "bbox": bbox,
                        "area_percentage": area_pct
                    }
                    detections.append(detection)
        
        # Determine overall severity and affected parts
        severity = determine_severity(detections)
        affected_parts = extract_affected_parts(detections)
        
        return {
            "success": True,
            "vehicle_detected": True,
            "damage_detected": len(detections) > 0,
            "detections": detections,
            "total_detections": len(detections),
            "severity": severity,
            "affected_parts": affected_parts,
            "summary": generate_summary(detections, severity)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Detection failed: {str(e)}"
        }


def calculate_area_percentage(bbox: List[float], image_shape: tuple) -> float:
    """Calculate percentage of image covered by bounding box."""
    x1, y1, x2, y2 = bbox
    box_area = (x2 - x1) * (y2 - y1)
    image_area = image_shape[0] * image_shape[1]  # height * width
    return round((box_area / image_area) * 100, 2)


def determine_severity(detections: List[Dict]) -> str:
    """
    Determine overall damage severity from detections.
    Priority: severe > moderate > minor > none
    """
    if not detections:
        return "none"
    
    # Check for severity in class names
    for det in detections:
        class_name = det["class_name"].lower()
        if "severe" in class_name or "major" in class_name:
            return "severe"
    
    for det in detections:
        class_name = det["class_name"].lower()
        if "moderate" in class_name or "medium" in class_name:
            return "moderate"
    
    # Check by area coverage - large damaged area = severe
    max_area = max([det["area_percentage"] for det in detections], default=0)
    if max_area > 30:
        return "severe"
    elif max_area > 15:
        return "moderate"
    
    return "minor"


def extract_affected_parts(detections: List[Dict]) -> List[str]:
    """Extract list of affected vehicle parts from detections."""
    parts = set()
    
    for det in detections:
        class_name = det["class_name"].lower()
        
        # Map detection classes to vehicle parts
        if "bumper" in class_name or "front" in class_name:
            parts.add("front_bumper")
        elif "door" in class_name:
            parts.add("door")
        elif "hood" in class_name:
            parts.add("hood")
        elif "fender" in class_name:
            parts.add("fender")
        elif "windshield" in class_name or "glass" in class_name:
            parts.add("windshield")
        elif "headlight" in class_name or "lamp" in class_name:
            parts.add("headlight")
        else:
            parts.add(class_name.replace(" ", "_"))
    
    return list(parts)


def generate_summary(detections: List[Dict], severity: str) -> str:
    """Generate human-readable summary of damage."""
    if not detections:
        return "No damage detected"
    
    num_damages = len(detections)
    avg_confidence = sum(d["confidence"] for d in detections) / num_damages
    
    return f"{severity.capitalize()} damage detected - {num_damages} area(s) affected with {avg_confidence:.1%} average confidence"


def get_model_info() -> Dict[str, Any]:
    """Get information about loaded model and system."""
    gpu_info = check_gpu_available()
    
    return {
        "yolo_available": YOLO_AVAILABLE,
        "model_initialized": MODEL_INITIALIZED,
        "gpu_info": gpu_info,
        "model_type": str(type(damage_model).__name__) if damage_model else None
    }
