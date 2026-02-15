"""Test EXIF metadata extraction"""
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import json

image_path = 'C:/Users/basil/.gemini/antigravity/brain/d3160f3a-7a50-4452-aa74-4043ba64e52b/uploaded_media_1770265264264.jpg'

print('=' * 50)
print('EXIF METADATA TEST')
print('=' * 50)

img = Image.open(image_path)
print(f"\nImage: {image_path}")
print(f"Size: {img.size}")
print(f"Format: {img.format}")

exif_data = img._getexif()

if exif_data:
    print(f"\n[EXIF DATA FOUND - {len(exif_data)} tags]")
    
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        
        # Skip binary data
        if isinstance(value, bytes):
            continue
            
        # Handle GPS data specially
        if tag == "GPSInfo":
            print(f"\n[GPS DATA]")
            for gps_tag_id, gps_value in value.items():
                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                print(f"  {gps_tag}: {gps_value}")
        else:
            # Print other tags
            val_str = str(value)[:100]
            print(f"  {tag}: {val_str}")
else:
    print("\n[NO EXIF DATA IN IMAGE]")
    print("This image may have been:")
    print("  - Taken with a camera that doesn't save EXIF")
    print("  - Edited/resized (which often strips EXIF)")
    print("  - Downloaded from the web (metadata removed)")
    print("  - Received via messaging apps (they strip metadata)")

print("\n[TEST COMPLETE]")
