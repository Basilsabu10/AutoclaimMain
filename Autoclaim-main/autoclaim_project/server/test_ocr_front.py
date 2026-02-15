"""Test OCR extraction on the front image to show license plate detection."""
from app.services.ocr_service import extract_number_plate
import os

# Get the front image path
front_image = "uploads/front_52d1dfcc-a048-444f-abbd-b8bd536b29b4.jpg"

print("=" * 80)
print("TESTING OCR LICENSE PLATE EXTRACTION")
print("=" * 80)
print(f"\nImage: {front_image}")
print(f"Size: {os.path.getsize(front_image) / 1024 / 1024:.2f} MB")

print("\n" + "-" * 80)
print("Running OCR extraction...")
print("-" * 80)

result = extract_number_plate(front_image)

print("\n=== OCR RESULT ===\n")
print(f"✓ License Plate: {result.get('plate_text')}")
print(f"✓ Confidence: {result.get('confidence')}%")

if result.get('raw_texts'):
    print(f"\n=== ALL TEXT DETECTED IN IMAGE ===\n")
    for i, text_info in enumerate(result.get('raw_texts', []), 1):
        text = text_info.get('text', 'N/A')
        conf = text_info.get('confidence', 0)
        print(f"{i}. '{text}' (confidence: {conf:.1f}%)")
else:
    print("\nNo raw text data available")

print("\n" + "=" * 80)
print("EXPLANATION:")
print("=" * 80)
print("""
The OCR service uses EasyOCR to:
1. Detect all text regions in the image
2. Filter for license plate patterns (e.g., KL-07-CU-7475)
3. Return the best match with confidence score

The license plate is extracted directly from the uploaded front image,
not from any database or external source.
""")
