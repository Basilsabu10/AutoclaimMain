from app.db.database import SessionLocal
from app.db.models import User, Claim
import sys

# Add the current directory to sys.path
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.email == "user@example.com").first()
        if user:
            print(f"User found: {user.email} (ID: {user.id})")
            claim = db.query(Claim).filter(Claim.user_id == user.id).order_by(Claim.created_at.desc()).first()
            if claim:
                print(f"LATEST_CLAIM_ID:{claim.id}")
                print(f"Status: {claim.status}")
                print(f"Images: {claim.image_paths}")
            else:
                print("NO_CLAIMS")
        else:
            print("USER_NOT_FOUND")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()
