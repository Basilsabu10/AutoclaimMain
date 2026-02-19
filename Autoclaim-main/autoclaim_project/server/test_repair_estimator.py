import sys
sys.path.insert(0, '.')
from app.services.repair_estimator_service import estimate_repair_cost

r = estimate_repair_cost(['front_bumper', 'hood', 'door_fl', 'windshield'], 'Toyota', 'Camry', '2020')
print(f"Parts priced: {len(r['breakdown'])}")
for p in r['breakdown']:
    print(f"  {p['icon']} {p['part']}: Rs{p['inr_min']:,} - Rs{p['inr_max']:,}  (${p['usd_min']}-${p['usd_max']})")
print(f"TOTAL: Rs{r['total_inr_min']:,} - Rs{r['total_inr_max']:,}")
print(f"Rate: {r['usd_to_inr_rate']}/USD")
print(f"Vehicle: {r['vehicle_info']}")
print(f"Unrecognized: {r['unrecognized_panels']}")
