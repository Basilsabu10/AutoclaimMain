"""Get complete forensic analysis."""
from app.db.database import SessionLocal
from app.db.models import ForensicAnalysis

db = SessionLocal()
f = db.query(ForensicAnalysis).order_by(ForensicAnalysis.analyzed_at.desc()).first()

if f:
    print('=== COMPLETE FORENSIC ANALYSIS ===\n')
    print(f'AI Recommendation: {f.ai_recommendation}')
    print(f'Severity: {f.ai_severity}')
    print(f'Damage Type: {f.ai_damage_type}')
    print(f'Affected Parts: {f.ai_affected_parts}')
    print(f'Cost Estimate: Rs {f.ai_cost_min} - Rs {f.ai_cost_max}')
    print(f'License Plate: {f.license_plate_text}')
    print(f'Damaged Panels: {f.ai_damaged_panels}')
    print(f'Provider: {f.ai_provider}')
    print(f'Overall Confidence: {f.overall_confidence_score}%')
    print(f'Fraud Probability: {f.fraud_probability}')
    
    print(f'\n=== REASONING ===')
    if f.ai_reasoning:
        print(f.ai_reasoning[:400] + '...' if len(f.ai_reasoning) > 400 else f.ai_reasoning)
    else:
        print('No reasoning provided')
else:
    print('No forensic analysis found')

db.close()
