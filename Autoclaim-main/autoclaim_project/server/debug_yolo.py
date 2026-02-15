"""Get detailed YOLO error information."""
from app.services.yolov8_damage_service import detect_vehicle_damage, get_model_info
import os

# Check model status
print("=== YOLO MODEL INFO ===")
info = get_model_info()
print(f"Available: {info.get('available')}")
print(f"Model loaded: {info.get('model_loaded')}")
print(f"Model path: {info.get('model_path')}")
print(f"GPU: {info.get('gpu_info', {}).get('available')}")

# Test on first damage image
upload_dir = "uploads"
damage_images = [f for f in os.listdir(upload_dir) if f.startswith("damage_")]

if damage_images:
    img_path = os.path.join(upload_dir, damage_images[0])
    print(f"\n=== TESTING ON {damage_images[0]} ===")
    
    result = detect_vehicle_damage(img_path)
    
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    print(f"Damage detected: {result.get('damage_detected')}")
    print(f"Detections: {result.get('detections')}")
    print(f"Summary: {result.get('summary')}")
    
    # Print full result
    print("\n=== FULL RESULT ===")
    import json
    print(json.dumps(result, indent=2, default=str))
