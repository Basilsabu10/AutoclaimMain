"""
Quick verification script to test the new v3.0 schema.
Checks that all new fields exist in the database.
"""

from app.db.database import SessionLocal, engine
from app.db import models
from sqlalchemy import inspect

print("=" * 80)
print("VERIFYING v3.0 SCHEMA")
print("=" * 80)

# Get table columns
inspector = inspect(engine)
columns = inspector.get_columns('forensic_analyses')

print(f"\n✅ ForensicAnalysis table has {len(columns)} columns")

# Check for new v3.0 fields
new_fields_v3 = [
    'detected_objects',
    'license_plate_visible',
    'license_plate_obscured',
    'damage_severity_score',
    'impact_point',
    'paint_damage',
    'glass_damage',
    'is_rust_present',
    'rust_locations',
    'is_dirt_in_damage',
    'is_paint_faded_around_damage',
    'airbags_deployed',
    'fluid_leaks_visible',
    'parts_missing',
    'is_screen_recapture',
    'has_ui_elements',
    'has_watermarks',
    'image_quality',
    'is_blurry',
    'multiple_light_sources',
    'shadows_inconsistent',
    'time_of_day',
    'weather_visible',
    'debris_visible',
    'other_vehicles_visible',
    'is_moving_traffic',
    'fraud_score'
]

column_names = [col['name'] for col in columns]

print("\n📊 Checking v3.0 fields...")
missing = []
for field in new_fields_v3:
    if field in column_names:
        print(f"  ✓ {field}")
    else:
        missing.append(field)
        print(f"  ✗ {field} MISSING")

if missing:
    print(f"\n❌ {len(missing)} fields missing!")
else:
    print(f"\n✅ All {len(new_fields_v3)} v3.0 fields present!")

print("\n" + "=" * 80)
print("SCHEMA VERIFICATION COMPLETE")
print("=" * 80)
