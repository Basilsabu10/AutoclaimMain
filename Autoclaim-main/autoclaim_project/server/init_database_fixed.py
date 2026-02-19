"""
Database initialization script for AutoClaim.
Creates sample data for testing: users, policy plans, policies, and claims.
"""

import sys
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, engine
from app.db import models

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password safely for bcrypt (max 72 chars)."""
    # Ensure password doesn't exceed bcrypt's 72-character limit
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def init_database():
    """Initialize database with sample data."""
    
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print(" Initializing AutoClaim database...")
        
        # Check if data already exists
        existing_users = db.query(models.User).count()
        if existing_users > 0:
            print(f"  Database already has {existing_users} users. Skipping initialization.")
            response = input("Do you want to clear and reinitialize? (yes/no): ")
            if response.lower() != "yes":
                print(" Initialization cancelled.")
                return
            
            # Clear existing data
            print("  Clearing existing data...")
            db.query(models.ForensicAnalysis).delete()
            db.query(models.Claim).delete()
            db.query(models.Policy).delete()
            db.query(models.PolicyPlan).delete()
            db.query(models.User).delete()
            db.commit()
        
        # 1. Create Policy Plans
        print("\n Creating policy plans...")
        
        basic_plan = models.PolicyPlan(
            name="Basic Coverage",
            description="Essential coverage for your vehicle with liability protection",
            coverage_amount=100000,
            premium_monthly=2500
        )
        
        standard_plan = models.PolicyPlan(
            name="Standard Coverage",
            description="Comprehensive coverage including collision and theft",
            coverage_amount=300000,
            premium_monthly=5000
        )
        
        premium_plan = models.PolicyPlan(
            name="Premium Coverage",
            description="Full coverage with zero depreciation and roadside assistance",
            coverage_amount=500000,
            premium_monthly=8000
        )
        
        db.add_all([basic_plan, standard_plan, premium_plan])
        db.commit()
        db.refresh(basic_plan)
        db.refresh(standard_plan)
        db.refresh(premium_plan)
        
        print(f"    Created {db.query(models.PolicyPlan).count()} policy plans")
        
        # 2. Create Users
        print("\n Creating users...")
        
        # Admin user
        admin = models.User(
            email="admin@autoclaim.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            name="Admin User"
        )
        
        # Agent user
        agent = models.User(
            email="agent@autoclaim.com",
            hashed_password=hash_password("agent123"),
            role="agent",
            name="Insurance Agent"
        )
        
        # Regular users
        user1 = models.User(
            email="john.doe@example.com",
            hashed_password=hash_password("password123"),
            role="user",
            name="John Doe",
            policy_id="POL-2026-001",
            vehicle_number="KL-01-AB-1234"
        )
        
        user2 = models.User(
            email="jane.smith@example.com",
            hashed_password=hash_password("password123"),
            role="user",
            name="Jane Smith",
            policy_id="POL-2026-002",
            vehicle_number="KL-02-CD-5678"
        )
        
        db.add_all([admin, agent, user1, user2])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        print(f"    Created {db.query(models.User).count()} users")
        print(f"      - admin@autoclaim.com (password: admin123)")
        print(f"      - agent@autoclaim.com (password: agent123)")
        print(f"      - john.doe@example.com (password: password123)")
        print(f"      - jane.smith@example.com (password: password123)")
        
        # 3. Create Policies
        print("\n Creating policies...")
        
        policy1 = models.Policy(
            user_id=user1.id,
            plan_id=standard_plan.id,
            vehicle_make="Honda",
            vehicle_model="City",
            vehicle_year=2022,
            vehicle_registration="KL-01-AB-1234",
            start_date=datetime.now() - timedelta(days=180),
            end_date=datetime.now() + timedelta(days=185),
            status="active"
        )
        
        policy2 = models.Policy(
            user_id=user2.id,
            plan_id=premium_plan.id,
            vehicle_make="Toyota",
            vehicle_model="Fortuner",
            vehicle_year=2023,
            vehicle_registration="KL-02-CD-5678",
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now() + timedelta(days=275),
            status="active"
        )
        
        db.add_all([policy1, policy2])
        db.commit()
        db.refresh(policy1)
        db.refresh(policy2)
        
        print(f"    Created {db.query(models.Policy).count()} active policies")
        
        # 4. Create Sample Claims
        print("\n Creating sample claims...")
        
        # Claim 1: Processing (with AI analysis)
        claim1 = models.Claim(
            user_id=user1.id,
            policy_id=policy1.id,
            description="Front bumper damage after minor collision in parking lot",
            image_paths=["uploads/damage_front_bumper.jpg"],
            front_image_path="uploads/front_vehicle.jpg",
            status="processing",
            vehicle_number_plate="KL-01-AB-1234",
            ai_recommendation="REVIEW",
            estimated_cost_min=15000,
            estimated_cost_max=25000,
            created_at=datetime.now() - timedelta(days=2)
        )
        
        # Claim 2: Approved
        claim2 = models.Claim(
            user_id=user1.id,
            policy_id=policy1.id,
            description="Rear door dent from shopping cart impact",
            image_paths=["uploads/damage_door.jpg"],
            status="approved",
            vehicle_number_plate="KL-01-AB-1234",
            ai_recommendation="APPROVE",
            estimated_cost_min=8000,
            estimated_cost_max=12000,
            created_at=datetime.now() - timedelta(days=10)
        )
        
        # Claim 3: Pending (new submission)
        claim3 = models.Claim(
            user_id=user2.id,
            policy_id=policy2.id,
            description="Side mirror broken, need replacement",
            image_paths=["uploads/damage_mirror.jpg"],
            front_image_path="uploads/front_vehicle2.jpg",
            status="pending",
            vehicle_number_plate="KL-02-CD-5678",
            estimated_cost_min=5000,
            estimated_cost_max=8000,
            created_at=datetime.now() - timedelta(hours=6)
        )
        
        # Claim 4: Rejected
        claim4 = models.Claim(
            user_id=user2.id,
            policy_id=policy2.id,
            description="Windshield crack",
            image_paths=["uploads/damage_windshield.jpg"],
            status="rejected",
            vehicle_number_plate="KL-02-CD-5678",
            ai_recommendation="REJECT",
            estimated_cost_min=12000,
            estimated_cost_max=18000,
            created_at=datetime.now() - timedelta(days=15)
        )
        
        db.add_all([claim1, claim2, claim3, claim4])
        db.commit()
        db.refresh(claim1)
        
        print(f"    Created {db.query(models.Claim).count()} sample claims")
        
        # 5. Create Forensic Analysis for claim1
        print("\n Creating forensic analysis...")
        
        forensic1 = models.ForensicAnalysis(
            claim_id=claim1.id,
            exif_timestamp=datetime.now() - timedelta(days=2, hours=3),
            exif_location_name="Kochi, Kerala",
            ocr_plate_text="KL01AB1234",
            ocr_plate_confidence=0.95,
            ai_damage_detected=True,
            ai_damaged_panels=["front_bumper", "hood"],
            ai_damage_type="dent",
            ai_severity="moderate",
            ai_affected_parts=["front_bumper", "hood"],
            ai_cost_min=15000,
            ai_cost_max=25000,
            ai_recommendation="REVIEW",
            ai_reasoning="Moderate damage detected. Requires professional inspection to verify extent of damage.",
            overall_confidence_score=78.5,
            fraud_probability="LOW",
            ai_risk_flags=["cost_above_threshold"],
            analyzed_at=datetime.now() - timedelta(days=2)
        )
        
        db.add(forensic1)
        db.commit()
        
        print(f"    Created forensic analysis for claim #{claim1.id}")
        
        print("\n Database initialization complete!")
        print("\n" + "="*60)
        print(" Summary:")
        print(f"   - Policy Plans: {db.query(models.PolicyPlan).count()}")
        print(f"   - Users: {db.query(models.User).count()}")
        print(f"   - Policies: {db.query(models.Policy).count()}")
        print(f"   - Claims: {db.query(models.Claim).count()}")
        print(f"   - Forensic Analyses: {db.query(models.ForensicAnalysis).count()}")
        print("="*60)
        
    except Exception as e:
        print(f"\n Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
