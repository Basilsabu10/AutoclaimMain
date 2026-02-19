import sys
import os
import json

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import Claim

def check(claim_id):
    output_lines = []
    def log(msg):
        print(msg)
        output_lines.append(str(msg))

    db = SessionLocal()
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            log(f"Claim {claim_id} not found")
            return
        
        log(f"Claim ID: {claim.id}")
        log(f"Status: {claim.status}")
        
        fa = claim.forensic_analysis
        if fa:
            log("Forensic Analysis: FOUND")
            log(f"Damage Detected: {fa.ai_damage_detected}")
            log(f"Severity: {fa.ai_severity}")
            log(f"License Plate: {fa.license_plate_text}")
            log(f"Recommendation: {claim.ai_recommendation}")
            
            if fa.ai_raw_response:
                log("Raw Response: PRESENT")
                try:
                    raw = fa.ai_raw_response
                    if isinstance(raw, str):
                        raw = json.loads(raw)
                    
                    log("--- Raw Response Summary ---")
                    log(json.dumps(raw, indent=2))
                except Exception as e:
                    log(f"Error parsing raw response: {e}")
            else:
                log("Raw Response: MISSING")
            
            # Check mapped fields
            log("--- Mapped Fields ---")
            log(f"Vehicle Make: {fa.vehicle_make}")
            log(f"Vehicle Model: {fa.vehicle_model}")
            log(f"Damaged Panels: {fa.ai_damaged_panels}")
            
        else:
            log("Forensic Analysis: MISSING")
            
    except Exception as e:
        log(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    with open("verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

if __name__ == "__main__":
    check(5)
