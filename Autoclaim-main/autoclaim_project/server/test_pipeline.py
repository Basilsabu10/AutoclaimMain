"""Test YOLO + Groq pipeline on damage image"""
import ai_service

image_path = 'C:/Users/basil/.gemini/antigravity/brain/f2fbaada-4bb5-4f3b-b496-9a9b6fcedb14/media__1770268325991.jpg'

print('=== TESTING NEW AI PIPELINE ===')
print('Services Status:')
status = ai_service.initialize_services()
print(f"  YOLO: {'OK' if status['yolo'] else 'N/A'}")
print(f"  Groq: {'OK' if status['groq'] else 'N/A'}")
print(f"  Gemini: {'OK' if status['gemini'] else 'N/A'}")

print('\nRunning analysis on damage image...')
result = ai_service.analyze_claim(
    damage_image_paths=[image_path],
    front_image_path=None,
    description='Scratch on car door'
)

print('\n=== YOLO DETECTION ===')
yolo = result.get('yolo', {})
print(f"Vehicle Detected: {yolo.get('vehicle_detected', False)}")
print(f"Summary: {yolo.get('summary', 'N/A')}")
for det in yolo.get('detections', [])[:5]:
    print(f"  - {det['class']}: {det['confidence']*100:.1f}%")

print('\n=== AI DAMAGE ANALYSIS ===')
ai = result.get('ai_analysis', {})
print(f"Provider: {ai.get('provider', 'N/A')}")
print(f"Damage Type: {ai.get('damage_type', 'N/A')}")
print(f"Severity: {ai.get('severity', 'N/A')}")
print(f"Recommendation: {ai.get('recommendation', 'N/A')}")
print(f"Cost: ${ai.get('cost_min', 0)} - ${ai.get('cost_max', 0)}")
print(f"Parts: {', '.join(ai.get('affected_parts', []))}")
print(f"\nAnalysis: {ai.get('analysis_text', 'N/A')[:500]}")

print('\n=== DONE ===')
