"""Test EXIF metadata extraction on uploaded images"""
import os
from app.services.exif_service import extract_metadata

print("="*80)
print("EXIF METADATA EXTRACTION TEST")
print("="*80)

# Test with uploaded damage images
uploads_dir = "uploads"
damage_images = [f for f in os.listdir(uploads_dir) if f.startswith("damage_")][:3]

print(f"\nTesting {len(damage_images)} damage images:\n")

for i, img_file in enumerate(damage_images, 1):
    img_path = os.path.join(uploads_dir, img_file)
    print(f"--- Image {i}: {img_file} ---")
    print(f"Path: {img_path}")
    
    result = extract_metadata(img_path)
    print(f"\nExtracted Metadata:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("-"*80 + "\n")

print("="*80)
print("TEST COMPLETE")
print("="*80)
