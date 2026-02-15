"""Export forensic analysis data to text file"""
from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()

with open('forensic_analysis_data.txt', 'w', encoding='utf-8') as f:
    f.write('='*100 + '\n')
    f.write('FORENSIC ANALYSIS TABLE - COMPLETE DATA\n')
    f.write('='*100 + '\n\n')
    
    forensics = db.query(models.ForensicAnalysis).all()
    f.write(f'Total Records: {len(forensics)}\n\n')
    
    for i, fa in enumerate(forensics, 1):
        f.write(f'\n{"="*100}\n')
        f.write(f'RECORD #{i} - Forensic Analysis ID: {fa.id}\n')
        f.write(f'{"="*100}\n')
        f.write(f'Claim ID: {fa.claim_id}\n\n')
        
        # EXIF/Metadata
        f.write('📍 IMAGE METADATA:\n')
        f.write(f'  Timestamp: {fa.exif_timestamp}\n')
        f.write(f'  GPS Coordinates: Lat {fa.exif_gps_lat}, Lon {fa.exif_gps_lon}\n')
        f.write(f'  Location Name: {fa.exif_location_name}\n')
        f.write(f'  Camera: {fa.exif_camera_make} {fa.exif_camera_model}\n\n')
        
        # OCR
        f.write('🔤 OCR - NUMBER PLATE DETECTION:\n')
        f.write(f'  Plate Text: {fa.ocr_plate_text}\n')
        f.write(f'  Confidence: {fa.ocr_plate_confidence}\n')
        f.write(f'  Raw OCR Texts: {fa.ocr_raw_texts}\n\n')
        
        # AI Damage Analysis
        f.write('🤖 AI DAMAGE ANALYSIS:\n')
        f.write(f'  Damage Type: {fa.ai_damage_type}\n')
        f.write(f'  Severity: {fa.ai_severity}\n')
        f.write(f'  Affected Parts: {fa.ai_affected_parts}\n')
        f.write(f'  Recommendation: {fa.ai_recommendation}\n')
        f.write(f'  Estimated Cost: ${fa.ai_cost_min} - ${fa.ai_cost_max}\n')
        f.write(f'  AI Confidence: {fa.ai_confidence}\n')
        f.write(f'  Risk Flags: {fa.ai_risk_flags}\n\n')
        
        # AI Reasoning
        f.write('💭 AI REASONING:\n')
        f.write(f'  {fa.ai_reasoning or "N/A"}\n\n')
        
        # Analysis Metadata
        f.write('ℹ️ ANALYSIS METADATA:\n')
        f.write(f'  Analyzed At: {fa.analyzed_at}\n')
        f.write(f'  Analysis Version: {fa.analysis_version}\n')
        
        f.write('\n' + '-'*100 + '\n')
    
    f.write('\n' + '='*100 + '\n')
    f.write('END OF FORENSIC ANALYSIS DATA\n')
    f.write('='*100 + '\n')

db.close()
print(f'✅ Forensic analysis data exported to: forensic_analysis_data.txt')
print(f'   Total records exported: {len(forensics)}')
