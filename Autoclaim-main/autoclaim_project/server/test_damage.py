"""Test AI damage analysis on uploaded image"""
import ai_service
import json

image_path = 'C:/Users/basil/.gemini/antigravity/brain/d3160f3a-7a50-4452-aa74-4043ba64e52b/uploaded_media_1770267257249.jpg'

print('Analyzing damage image...')
result = ai_service.analyze_claim(
    damage_image_paths=[image_path],
    front_image_path=None,
    description='Scratch on car door'
)

print('\n=== DAMAGE ANALYSIS RESULTS ===')
print(f"OCR Plate: {result.get('ocr', {}).get('plate_text', 'N/A')}")

ai = result.get('ai_analysis', {})
print(f"\nDamage Type: {ai.get('damage_type', 'Unknown')}")
print(f"Severity: {ai.get('severity', 'Unknown')}")
print(f"Recommendation: {ai.get('recommendation', 'review')}")
print(f"Cost Range: ${ai.get('cost_min', 0)} - ${ai.get('cost_max', 0)}")
print(f"Affected Parts: {ai.get('affected_parts', [])}")
print(f"\nAnalysis: {ai.get('analysis_text', 'No analysis')}")

# Save result
with open('damage_result.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
print('\nFull result saved to damage_result.json')
