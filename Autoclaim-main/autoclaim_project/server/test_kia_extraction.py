"""
Quick test script using existing uploaded images or custom paths.
Tests the complete v3.0 pipeline: AI extraction + rule-based decisions.
"""

import os
import sys
from app.services.ai_orchestrator import analyze_claim
from app.db.database import SessionLocal
from app.db.models import Policy
import json

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for images in multiple locations
possible_image_dirs = [
    os.path.join(BASE_DIR, "test_images", "kia_seltos"),
    os.path.join(BASE_DIR, "uploads"),
]

# Find available images
available_images = []
for img_dir in possible_image_dirs:
    if os.path.exists(img_dir):
        for file in os.listdir(img_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                available_images.append(os.path.join(img_dir, file))

if not available_images:
    print("❌ No images found in test_images/ or uploads/")
    print("\n💡 Two options:")
    print("  1. Save images to: server/test_images/kia_seltos/")
    print("  2. Submit a claim via frontend: http://localhost:5173")
    sys.exit(1)

print("=" * 80)
print("TESTING AI EXTRACTION v3.0")
print("=" * 80)

print(f"\n📁 Found {len(available_images)} images:")
for img in available_images[:5]:  # Show first 5
    print(f"  ✓ {os.path.basename(img)}")
if len(available_images) > 5:
    print(f"  ... and {len(available_images) - 5} more")

# Use first 3 damage images and 1 front image
damage_images = available_images[:3]
front_image = available_images[3] if len(available_images) > 3 else None

# Get policy data
db = SessionLocal()
policy = db.query(Policy).first()  # Get any policy for testing

policy_data = None
if policy:
    policy_data = {
        "vehicle_make": policy.vehicle_make,
        "vehicle_model": policy.vehicle_model,
        "vehicle_year": policy.vehicle_year,
        "vehicle_registration": policy.vehicle_registration,
    }
    print(f"\n✓ Using policy: {policy.vehicle_make} {policy.vehicle_model} ({policy.vehicle_registration})")
else:
    print("\n⚠️  No policy found - testing without policy data")

db.close()

print(f"\n🔍 Running AI extraction on {len(damage_images)} damage images...")

# Run analysis
result = analyze_claim(
    damage_image_paths=damage_images,
    front_image_path=front_image,
    description="Vehicle damage assessment - testing v3.0 extraction system",
    policy_data=policy_data
)

print("\n" + "=" * 80)
print("EXTRACTION RESULTS")
print("=" * 80)

# Display results
if result.get("ai_analysis", {}).get("success"):
    extraction = result["ai_analysis"]
    
    print("\n🔍 IDENTITY EXTRACTION:")
    identity = extraction.get("identity", {})
    print(f"  Detected Objects: {identity.get('detected_objects', [])}")
    print(f"  Vehicle: {identity.get('vehicle_make')} {identity.get('vehicle_model')} {identity.get('vehicle_year')} ({identity.get('vehicle_color')})")
    print(f"  License Plate: {identity.get('license_plate_text')}")
    print(f"  Plate Visible: {identity.get('license_plate_visible')}")
    print(f"  Plate Obscured: {identity.get('license_plate_obscured')}")
    
    print("\n💥 DAMAGE EXTRACTION:")
    damage = extraction.get("damage", {})
    print(f"  Damage Detected: {damage.get('damage_detected')}")
    print(f"  Damage Type: {damage.get('damage_type')}")
    print(f"  Severity Score: {damage.get('severity_score')} (0.0-1.0)")
    print(f"  Impact Point: {damage.get('impact_point')}")
    print(f"  Damaged Panels: {damage.get('damaged_panels', [])}")
    print(f"  Paint Damage: {damage.get('paint_damage')}")
    print(f"  Glass Damage: {damage.get('glass_damage')}")
    print(f"  Rust Present: {damage.get('is_rust_present')}")
    print(f"  Dirt in Damage: {damage.get('is_dirt_in_damage')}")
    print(f"  Cost Range (INR): ₹{damage.get('estimated_cost_range_INR', {}).get('min')} - ₹{damage.get('estimated_cost_range_INR', {}).get('max')}")
    
    print("\n🔬 FORENSICS EXTRACTION:")
    forensics = extraction.get("forensics", {})
    print(f"  Screen Recapture: {forensics.get('is_screen_recapture')}")
    print(f"  Has UI Elements: {forensics.get('has_ui_elements')}")
    print(f"  Image Quality: {forensics.get('image_quality')}")
    print(f"  Is Blurry: {forensics.get('is_blurry')}")
    print(f"  Lighting Quality: {forensics.get('lighting_quality')}")
    
    print("\n🌍 SCENE EXTRACTION:")
    scene = extraction.get("scene", {})
    print(f"  Location Type: {scene.get('location_type')}")
    print(f"  Time of Day: {scene.get('time_of_day')}")
    print(f"  Weather: {scene.get('weather_visible')}")
    print(f"  Debris Visible: {scene.get('debris_visible')}")
    
    print("\n⚖️ RULE-BASED DECISIONS:")
    decisions = result.get("decisions", {})
    print(f"  Recommendation: {decisions.get('ai_recommendation')}")
    print(f"  Fraud Probability: {decisions.get('fraud_probability')}")
    print(f"  Fraud Score: {decisions.get('fraud_score')} (0.0-1.0)")
    print(f"  Risk Flags: {decisions.get('ai_risk_flags', [])}")
    print(f"  Overall Confidence: {decisions.get('overall_confidence_score')}%")
    print(f"  Review Priority: {decisions.get('human_review_priority')}")
    print(f"\n  Reasoning: {decisions.get('ai_reasoning')}")
    
    print("\n✅ EXTRACTION SUCCESSFUL")
    
else:
    print("\n❌ AI Analysis Failed:")
    error = result.get("ai_analysis", {}).get("error", 'Unknown error')
    print(f"  Error: {error}")
    
    # Check if it's a success flag issue
    if "ai_analysis" in result and isinstance(result["ai_analysis"], dict):
        print(f"\n  AI Analysis keys: {list(result['ai_analysis'].keys())}")

print("\n" + "=" * 80)

# Save full result to JSON for inspection
output_file = os.path.join(BASE_DIR, "test_extraction_result.json")
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2, default=str)
print(f"💾 Full result saved to: {output_file}")
print("=" * 80)
