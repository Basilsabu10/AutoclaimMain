"""Get the complete ai_analysis to see the error."""
from app.db.database import SessionLocal
from app.db.models import ForensicAnalysis
import json

db = SessionLocal()
f = db.query(ForensicAnalysis).filter(ForensicAnalysis.claim_id == 1).first()

if f and f.ai_raw_response:
    ai_analysis = f.ai_raw_response.get("ai_analysis", {})
    
    print("=== AI ANALYSIS COMPLETE ===\n")
    
    # Check for error
    if "error" in ai_analysis:
        print(f"❌ ERROR FOUND: {ai_analysis['error']}\n")
    
    # Print all keys
    print(f"Keys in ai_analysis: {list(ai_analysis.keys())}\n")
    
    # Print each field
    for key, value in ai_analysis.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            print(f"{key}: {value}")
        elif isinstance(value, list) and len(value) < 10:
            print(f"{key}: {value}")
        elif isinstance(value, dict):
            print(f"{key}: <dict with {len(value)} keys>")
        else:
            print(f"{key}: <{type(value).__name__}>")
    
    # Check success flag
    print(f"\nSuccess: {ai_analysis.get('success')}")
    
else:
    print("No raw response")

db.close()
