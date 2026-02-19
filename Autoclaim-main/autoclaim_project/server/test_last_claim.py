"""Test the last claim submitted by a user - writes output to test_output.txt."""
import sys
import json
from app.db.database import SessionLocal
from app.db.models import User, Claim, ForensicAnalysis

def test_last_claim(email="user@example.com"):
    output = []
    def p(msg=""):
        output.append(str(msg))
        print(msg)
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            p(f"User '{email}' not found")
            return
        
        p(f"User ID: {user.id}, Email: {user.email}")
        
        claims = db.query(Claim).filter(Claim.user_id == user.id).order_by(Claim.created_at.desc()).all()
        p(f"Total claims: {len(claims)}")
        
        if not claims:
            p("No claims found.")
            return
        
        c = claims[0]
        p(f"")
        p("=" * 60)
        p(f"LATEST CLAIM (ID: {c.id})")
        p("=" * 60)
        p(f"  Status:      {c.status}")
        p(f"  Description: {c.description}")
        p(f"  Created:     {c.created_at}")
        p(f"  Image paths: {c.image_paths}")
        
        fa = c.forensic_analysis
        if fa:
            p(f"")
            p("  --- Forensic Analysis ---")
            p(f"  Analyzed At:      {fa.analyzed_at}")
            p(f"  Damage Detected:  {fa.ai_damage_detected}")
            p(f"  Severity:         {fa.ai_severity}")
            p(f"  Damage Type:      {fa.ai_damage_type}")
            p(f"  Affected Parts:   {fa.ai_affected_parts}")
            p(f"  Damaged Panels:   {fa.ai_damaged_panels}")
            p(f"  Vehicle:          {fa.vehicle_make} {fa.vehicle_model} ({fa.vehicle_color})")
            p(f"  License Plate:    {fa.license_plate_text} (detected: {fa.license_plate_detected})")
            p(f"  Authenticity:     {fa.authenticity_score}")
            p(f"  Raw Response:     {'Present' if fa.ai_raw_response else 'None'}")
            
            if fa.ai_raw_response:
                try:
                    raw = json.loads(fa.ai_raw_response) if isinstance(fa.ai_raw_response, str) else fa.ai_raw_response
                    p("")
                    p("  --- Raw AI Response Summary ---")
                    final = raw.get("final_assessment", {})
                    p(f"  Overall Confidence: {final.get('overall_confidence_score', 'N/A')}")
                    p(f"  Recommendation:     {final.get('recommendation', 'N/A')}")
                    p(f"  Fraud Probability:  {final.get('fraud_probability', 'N/A')}")
                    p(f"  Decision Reasoning: {final.get('decision_reasoning', 'N/A')}")
                    
                    vehicle = raw.get("vehicle_identification", {})
                    p("")
                    p("  --- Vehicle (from AI) ---")
                    p(f"  Make:  {vehicle.get('make', 'N/A')}")
                    p(f"  Model: {vehicle.get('model', 'N/A')}")
                    p(f"  Color: {vehicle.get('color', 'N/A')}")
                    lp = vehicle.get("license_plate", {})
                    p(f"  License Plate: {lp.get('text', 'N/A')} (confidence: {lp.get('confidence', 'N/A')})")
                    
                    damage = raw.get("damage_assessment", {})
                    p("")
                    p("  --- Damage Assessment (from AI) ---")
                    p(f"  Damage Detected: {damage.get('damage_detected', 'N/A')}")
                    p(f"  Severity:        {damage.get('overall_severity', 'N/A')}")
                    panels = damage.get("damaged_panels", [])
                    for panel in panels:
                        p(f"    - {panel.get('panel_name', '?')}: {panel.get('damage_type', '?')} ({panel.get('severity', '?')})")
                    
                    cost = damage.get("estimated_repair_cost", {})
                    p(f"  Estimated Cost: ${cost.get('min_usd', '?')} - ${cost.get('max_usd', '?')}")
                    
                    risks = raw.get("risk_flags", [])
                    if risks:
                        p("")
                        p("  --- Risk Flags ---")
                        for r in risks:
                            p(f"    - {r}")
                except Exception as e:
                    p(f"  Error parsing raw response: {e}")
        else:
            p("")
            p("  No Forensic Analysis record found for this claim.")
            p("  The AI analysis may not have run or may have failed.")
        
    except Exception as e:
        p(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    # Write to file
    with open("test_output.txt", "w") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "user@example.com"
    test_last_claim(email)
