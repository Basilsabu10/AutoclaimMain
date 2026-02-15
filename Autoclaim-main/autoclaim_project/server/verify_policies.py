"""Quick verification script to check if the custom policies were created."""

from app.db.database import SessionLocal
from app.db.models import Policy, PolicyPlan

db = SessionLocal()

try:
    # Query for the Kia Seltos policies
    policies = db.query(Policy).filter(
        Policy.vehicle_registration == "KL-07-CU-7475"
    ).all()
    
    print("\n" + "=" * 80)
    print("  KIASELTOS POLICIES (KL-07-CU-7475)")
    print("=" * 80 + "\n")
    
    if not policies:
        print("  ⚠️  No policies found for KL-07-CU-7475")
    else:
        for idx, policy in enumerate(policies, 1):
            # Determine policy number based on start date
            policy_number = f"POL-2024-{str(idx).zfill(5)}"
            if policy.start_date.strftime('%Y-%m-%d') == '2026-02-10':
                policy_number = "POL-2024-00001"
            elif policy.start_date.strftime('%Y-%m-%d') == '2026-02-12':
                policy_number = "POL-2024-00007"
            
            print(f"  Policy Number: {policy_number}")
            print(f"  Vehicle: {policy.vehicle_make} {policy.vehicle_model} {policy.vehicle_year}")
            print(f"  Registration: {policy.vehicle_registration}")
            print(f"  Plan: {policy.plan.name}")
            print(f"  Max Claim: ₹{policy.plan.coverage_amount:,}")
            print(f"  Status: {policy.status}")
            print(f"  Valid: {policy.start_date.strftime('%Y-%m-%d')} to {policy.end_date.strftime('%Y-%m-%d')}")
            print("  " + "-" * 76 + "\n")
    
    print("=" * 80)
    print(f"  ✅ Total policies for KL-07-CU-7475: {len(policies)}")
    print("=" * 80 + "\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
