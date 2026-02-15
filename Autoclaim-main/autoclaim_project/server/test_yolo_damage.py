"""Test YOLO damage detection on the uploaded images."""
from app.services.yolov8_damage_service import detect_vehicle_damage
import os

upload_dir = "uploads"

# Get all damage images
damage_images = [f for f in os.listdir(upload_dir) if f.startswith("damage_")]

print("Testing YOLO damage detection on uploaded images...\n")
print("=" * 80)

for img in damage_images:
    img_path = os.path.join(upload_dir, img)
    print(f"\n📷 Testing: {img}")
    print("-" * 80)
    
    result = detect_vehicle_damage(img_path)
    
    print(f"Success: {result.get('success')}")
    print(f"Damage Detected: {result.get('damage_detected')}")
    print(f"Severity: {result.get('severity')}")
    print(f"Number of detections: {len(result.get('detections', []))}")
    
    if result.get('detections'):
        print("\nDetections:")
        for i, det in enumerate(result.get('detections', [])[:5], 1):
            print(f"  {i}. Class: {det.get('class_name')} - Confidence: {det.get('confidence'):.2%}")
    
    print(f"\nSummary: {result.get('summary')}")
    
    if result.get('error'):
        print(f"❌ Error: {result.get('error')}")

print("\n" + "=" * 80)
