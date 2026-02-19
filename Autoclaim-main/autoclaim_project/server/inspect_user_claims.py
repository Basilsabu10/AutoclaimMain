import sys
from app.db.database import SessionLocal
from app.db.models import User, Claim, ForensicAnalysis

def inspect_user_claims(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found.")
            return

        print(f"User: {user.email} (ID: {user.id})")
        
        claims = db.query(Claim).filter(Claim.user_id == user.id).order_by(Claim.created_at.desc()).all()
        if not claims:
            print("No claims found for this user.")
            return

        print(f"Found {len(claims)} claims.")
        
        for claim in claims: # Just show the latest one or all? Let's show all briefly, detailed for latest
            print(f"\nClaim ID: {claim.id}")
            print(f"Created At: {claim.created_at}")
            print(f"Status: {claim.status}")
            print(f"Image Paths: {claim.image_paths}")
            
            if claim.forensic_analysis:
                fa = claim.forensic_analysis
                print(f"Forensic Analysis ID: {fa.id}")
                print(f"Analyzed At: {fa.analyzed_at}")
                print(f"Values: Damage={fa.ai_damage_detected}, Severity={fa.ai_severity}")
                print(f"Raw Response present: {'Yes' if fa.ai_raw_response else 'No'}")
            else:
                print("No Forensic Analysis record found.")
            
            print("-" * 20)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "user@example.com"
    inspect_user_claims(email)
