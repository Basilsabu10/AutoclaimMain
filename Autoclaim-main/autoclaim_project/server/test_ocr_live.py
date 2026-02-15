"""Test OCR service with uploaded front images"""
import os
from app.services.ocr_service import extract_number_plate, OCR_AVAILABLE, init_ocr

print("="*80)
print("OCR SERVICE TEST")
print("="*80)
print(f"OCR Available: {OCR_AVAILABLE}\n")

# Initialize OCR
init_ocr()

# Find front images in uploads
uploads_dir = "uploads"
front_images = [f for f in os.listdir(uploads_dir) if f.startswith("front_")]

print(f"Found {len(front_images)} front images in uploads/\n")

if front_images:
    # Test with first 3 front images
    for i, img_file in enumerate(front_images[:3], 1):
        img_path = os.path.join(uploads_dir, img_file)
        print(f"\n--- Testing Image {i}: {img_file} ---")
        print(f"Path: {img_path}")
        print(f"Exists: {os.path.exists(img_path)}")
        
        result = extract_number_plate(img_path)
        print(f"\nOCR Result:")
        print(f"  Plate Text: {result['plate_text']}")
        print(f"  Confidence: {result['confidence']}")
        print("-"*80)
else:
    print("No front images found to test!")
    print("\nTip: Upload a claim with a front image first")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
