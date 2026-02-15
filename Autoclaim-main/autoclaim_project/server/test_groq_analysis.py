"""Test Groq damage analysis directly on the images."""
from app.services.groq_service import analyze_damage
import os

upload_dir = "uploads"

# Get all images
damage_images = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.startswith("damage_")]

print("Testing Groq AI analysis on uploaded damage images...\n")
print("=" * 80)

if damage_images:
    print(f"Found {len(damage_images)} damage images")
    print(f"Images: {[os.path.basename(p) for p in damage_images]}")
    
    description = "Vehicle: 2020 Kia Seltos\nLicense Plate: KL-07-CU-7475\nAccident Date: 2026-01-31\nClaim Amount: ₹40000\n\nrear ended"
    
    print(f"\nDescription: {description}")
    print("\nCalling Groq AI...")
    
    result = analyze_damage(damage_images, description, yolo_context=None)
    
    print("\n=== GROQ ANALYSIS RESULT ===\n")
    import json
    print(json.dumps(result, indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("\nSUMMARY:")
    print(f"Damage Type: {result.get('damage_type')}")
    print(f"Severity: {result.get('severity')}")
    print(f"Recommendation: {result.get('recommendation')}")
    print(f"Cost Range: ${result.get('cost_min')} - ${result.get('cost_max')}")
    print(f"Affected Parts: {result.get('affected_parts')}")
else:
    print("No damage images found")
