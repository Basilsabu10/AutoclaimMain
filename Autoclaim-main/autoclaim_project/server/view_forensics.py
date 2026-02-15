"""Script to view detailed forensic analysis data"""
from app.db.database import SessionLocal
from app.db import models
import json

db = SessionLocal()

print('='*80)
print('FORENSIC ANALYSIS TABLE - DETAILED VIEW')
print('='*80)

forensics = db.query(models.ForensicAnalysis).all()
print(f'\nTotal Records: {len(forensics)}\n')

for i, f in enumerate(forensics, 1):
    print(f'--- Record {i} (ID: {f.id}) ---')
    print(f'  Claim ID: {f.claim_id}')
    
    # EXIF Metadata
    print(f'\n  📍 EXIF Metadata:')
    print(f'    Timestamp: {f.exif_timestamp}')
    print(f'    GPS: ({f.exif_gps_lat}, {f.exif_gps_lon})')
    print(f'    Location: {f.exif_location_name}')
    print(f'    Camera: {f.exif_camera_make} {f.exif_camera_model}')
    
    # OCR Results
    print(f'\n  🔤 OCR Results:')
    print(f'    Plate Text: {f.ocr_plate_text}')
    print(f'    Confidence: {f.ocr_plate_confidence}')
    print(f'    Raw Texts: {f.ocr_raw_texts}')
    
    # AI Analysis
    print(f'\n  🤖 AI Damage Analysis:')
    print(f'    Damage Type: {f.ai_damage_type}')
    print(f'    Severity: {f.ai_severity}')
    print(f'    Affected Parts: {f.ai_affected_parts}')
    print(f'    Recommendation: {f.ai_recommendation}')
    print(f'    Cost Range: ${f.ai_cost_min} - ${f.ai_cost_max}')
    print(f'    Risk Flags: {f.ai_risk_flags}')
    print(f'    Confidence: {f.ai_confidence}')
    
    # Reasoning (truncated if too long)
    reasoning = f.ai_reasoning or "N/A"
    if len(reasoning) > 200:
        reasoning = reasoning[:200] + "..."
    print(f'    Reasoning: {reasoning}')
    
    # Metadata
    print(f'\n  ℹ️ Analysis Metadata:')
    print(f'    Analyzed At: {f.analyzed_at}')
    print(f'    Version: {f.analysis_version}')
    
    print('\n' + '-'*80 + '\n')

db.close()
print('='*80)
print('END OF FORENSIC ANALYSIS DATA')
print('='*80)
