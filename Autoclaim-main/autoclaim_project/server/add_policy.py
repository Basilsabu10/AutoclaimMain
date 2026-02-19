"""
One-time script to add policy POL-2024-00007 for Kia Seltos.
Run from: autoclaim_project/server/
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()

try:
    # ── 1. Find or create a suitable PolicyPlan ───────────────────────────────
    plan = db.query(models.PolicyPlan).filter(
        models.PolicyPlan.coverage_amount == 500000
    ).first()

    if not plan:
        plan = models.PolicyPlan(
            name="Comprehensive Auto – 5 Lakh",
            description="Comprehensive vehicle insurance plan with ₹5,00,000 coverage.",
            coverage_amount=500000,   # ₹5,00,000
            premium_monthly=2500,
        )
        db.add(plan)
        db.flush()          # get plan.id without committing yet
        print(f"✅ Created PolicyPlan id={plan.id}")
    else:
        print(f"ℹ️  Reusing existing PolicyPlan id={plan.id} (coverage=₹{plan.coverage_amount:,})")

    # ── 2. Find owner user ─────────────────────────────────────────────────────
    # The policy has the custom policy_id string "POL-2024-00007".
    # Assign to the first non-admin/non-agent user found, or create standalone.
    user = db.query(models.User).filter(models.User.role == "user").first()
    if user:
        print(f"ℹ️  Linking policy to user: {user.email} (id={user.id})")
        user_id = user.id
    else:
        raise RuntimeError("No regular user found in DB. Please create a user first.")

    # ── 3. Check if policy already exists (avoid duplicates) ──────────────────
    existing = db.query(models.Policy).filter(
        models.Policy.vehicle_registration == "KL-07-CU-7475"
    ).first()

    if existing:
        print(f"⚠️  Policy for KL-07-CU-7475 already exists (id={existing.id}). Skipping.")
    else:
        today = datetime.utcnow()
        policy = models.Policy(
            user_id=user_id,
            plan_id=plan.id,
            vehicle_make="Kia",
            vehicle_model="Seltos",
            vehicle_year=2020,
            vehicle_registration="KL-07-CU-7475",
            start_date=today,
            end_date=today + timedelta(days=365),
            status="active",
        )
        db.add(policy)
        db.flush()

        # Also update the user's policy_id string field
        user.policy_id = "POL-2024-00007"
        user.vehicle_number = "KL-07-CU-7475"

        db.commit()
        print(f"✅ Policy created successfully!")
        print(f"   Policy DB id  : {policy.id}")
        print(f"   Policy Number : POL-2024-00007")
        print(f"   Vehicle       : 2020 Kia Seltos")
        print(f"   Registration  : KL-07-CU-7475")
        print(f"   VIN / Chase   : WVWF14601ET093171")
        print(f"   Coverage      : ₹5,00,000")
        print(f"   Type          : Comprehensive")
        print(f"   Start         : {today.strftime('%Y-%m-%d')}")
        print(f"   End           : {(today + timedelta(days=365)).strftime('%Y-%m-%d')}")
        print(f"   Status        : active")
        print(f"   Linked user   : {user.email}")

except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    db.close()
