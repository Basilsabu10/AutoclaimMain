"""Get raw AI response from forensic analysis."""
from app.db.database import SessionLocal
from app.db.models import ForensicAnalysis
import json

db = SessionLocal()
f = db.query(ForensicAnalysis).first()

if f:
    print("\n=== RAW AI RESPONSE ===\n")
    if hasattr(f, 'ai_raw_response') and f.ai_raw_response:
        if isinstance(f.ai_raw_response, dict):
            print(json.dumps(f.ai_raw_response, indent=2))
        else:
            print(f.ai_raw_response)
    else:
        print("No raw response stored")
        
    print("\n=== ALL FORENSIC FIELDS ===")
    for col in f.__table__.columns:
        val = getattr(f, col.name)
        if val is not None:
            print(f"{col.name}: {val}")
else:
    print("No forensic record found")

db.close()
