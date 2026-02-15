"""Test script for AI services - ASCII safe output"""
import ai_service
import json

# Test with the uploaded image
image_path = 'C:/Users/basil/.gemini/antigravity/brain/d3160f3a-7a50-4452-aa74-4043ba64e52b/uploaded_media_1770264582613.jpg'

result = ai_service.analyze_claim(
    damage_image_paths=[image_path],
    front_image_path=image_path,
    description='Front view of Volkswagen for testing'
)

print('=' * 50)
print('AI ANALYSIS RESULTS')
print('=' * 50)

print('\n[EXIF METADATA]')
meta = result.get('metadata', {})
print(f"  Timestamp: {meta.get('timestamp', 'Not found')}")
print(f"  GPS Lat: {meta.get('gps_lat', 'Not found')}")
print(f"  GPS Lon: {meta.get('gps_lon', 'Not found')}")
print(f"  Location: {meta.get('location_name', 'Not found')}")

print('\n[OCR RESULTS]')
ocr = result.get('ocr', {})
print(f"  Plate Text: {ocr.get('plate_text', 'Not detected')}")
print(f"  Confidence: {ocr.get('confidence', 'N/A')}")

print('\n[AI ANALYSIS]')
ai = result.get('ai_analysis', {})
print(f"  Damage Type: {ai.get('damage_type', 'Unknown')}")
print(f"  Severity: {ai.get('severity', 'Unknown')}")
print(f"  Recommendation: {ai.get('recommendation', 'Unknown')}")
print(f"  Cost Range: ${ai.get('cost_min', 0)} - ${ai.get('cost_max', 0)}")
print(f"  Affected Parts: {ai.get('affected_parts', [])}")
print(f"  Analysis: {ai.get('analysis_text', 'No analysis')}")

print('\n[TEST COMPLETE]')

# Save full result to JSON file
with open('test_result.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
print('Full result saved to test_result.json')
