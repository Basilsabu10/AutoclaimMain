import sys
import os

# Add the current directory to sys.path to ensure we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db import models
from app.services.background_tasks import process_claim_ai_analysis
from app.services.yolov8_damage_service import init_yolo_model
import json

def trigger_analysis(claim_id):
    print("Initializing AI models...")
    init_yolo_model()
    
    db = SessionLocal()
    try:
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            print(f"Claim {claim_id} not found.")
            return

        print(f"Triggering analysis for Claim {claim_id}...")
        print(f"Description: {claim.description}")
        print(f"Image Paths: {claim.image_paths}")
        print(f"Front Image: {claim.front_image_path}")
        
        # Ensure image paths are a list
        damage_images = claim.image_paths if claim.image_paths else []
        if isinstance(damage_images, str):
             try:
                 damage_images = json.loads(damage_images)
             except:
                 damage_images = [damage_images]

        process_claim_ai_analysis(
            claim_id=claim.id,
            damage_image_paths=damage_images,
            front_image_path=claim.front_image_path,
            description=claim.description or ""
        )
        print("Analysis finished.")

    except Exception as e:
        print(f"Error triggering analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    claim_id = 5  # Hardcoded based on previous finding, can be arg
    if len(sys.argv) > 1:
        claim_id = int(sys.argv[1])
    
    trigger_analysis(claim_id)
