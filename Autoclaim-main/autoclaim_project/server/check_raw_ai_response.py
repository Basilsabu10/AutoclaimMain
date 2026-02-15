"""Check the raw AI response from the database."""
from app.db.database import SessionLocal
from app.db.models import ForensicAnalysis
import json

db = SessionLocal()
f = db.query(ForensicAnalysis).filter(ForensicAnalysis.claim_id == 1).first()

if f and f.ai_raw_response:
    print("=== RAW AI RESPONSE ===\n")
    print(json.dumps(f.ai_raw_response, indent=2))
    
    print("\n\n=== AI ANALYSIS SECTION ===\n")
    ai_analysis = f.ai_raw_response.get("ai_analysis", {})
    print(json.dumps(ai_analysis, indent=2))
else:
    print("No raw response found")

db.close()
