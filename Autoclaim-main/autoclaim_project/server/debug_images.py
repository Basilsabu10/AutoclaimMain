import sys
import os
import json
from app.db.database import SessionLocal
from app.db import models
from PIL import Image
import traceback

def debug_images(claim_id):
    db = SessionLocal()
    try:
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
        if not claim:
            print(f"Claim {claim_id} not found.")
            return

        print(f"Claim ID: {claim.id}")
        
        # Check Front Image
        front_path = claim.front_image_path
        print(f"\nFront Image Path: {front_path}")
        if front_path:
            if os.path.exists(front_path):
                try:
                    img = Image.open(front_path)
                    img.verify() # Verify it's an image
                    print(f"  [OK] PIL opened image. Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
                except Exception as e:
                    print(f"  [ERROR] PIL failed to open: {e}")
            else:
                print("  [ERROR] File does not exist")
        else:
            print("  No front image path in DB")

        # Check Damage Images
        print(f"\nDamage Images:")
        damage_images = claim.image_paths
        if isinstance(damage_images, str):
             try:
                 damage_images = json.loads(damage_images)
             except:
                 damage_images = [damage_images]
        
        if damage_images:
            for i, path in enumerate(damage_images):
                print(f"  Image {i+1}: {path}")
                if path and os.path.exists(path):
                    try:
                        img = Image.open(path)
                        img.verify()
                        print(f"    [OK] PIL opened image. Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
                    except Exception as e:
                        print(f"    [ERROR] PIL failed to open: {e}")
                else:
                    print("    [ERROR] File does not exist or path is empty")
        else:
            print("  No damage images.")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    claim_id = 5
    if len(sys.argv) > 1:
        claim_id = int(sys.argv[1])
    debug_images(claim_id)
