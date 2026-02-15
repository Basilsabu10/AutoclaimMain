"""
Database migration script to add comprehensive forensic analysis fields.
Run this to update the ForensicAnalysis table with new fields.
"""

# SQL to add new columns to forensic_analyses table
ALTER_TABLE_SQL = """
-- Forensic Analysis (Image Integrity)
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS authenticity_score FLOAT;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS forgery_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS forgery_indicators JSONB DEFAULT '[]';
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS digital_manipulation_confidence FLOAT;

-- Vehicle Identification
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vehicle_make VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vehicle_model VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vehicle_year VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vehicle_color VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vehicle_identification_confidence FLOAT;

-- License Plate Details  
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS license_plate_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS license_plate_text VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS license_plate_confidence FLOAT;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS license_plate_match_status VARCHAR;

-- VIN
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vin_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS vin_number VARCHAR;

-- YOLO Detection
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS yolo_damage_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS yolo_detections JSONB DEFAULT '[]';
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS yolo_severity VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS yolo_summary TEXT;

-- Enhanced Damage Assessment
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_damage_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_damaged_panels JSONB DEFAULT '[]';
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_structural_damage BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_safety_concerns JSONB DEFAULT '[]';
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_cost_confidence FLOAT;

-- Pre-existing Damage
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS pre_existing_damage_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS pre_existing_indicators JSONB DEFAULT '[]';
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS pre_existing_description TEXT;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS pre_existing_confidence FLOAT;

-- Contextual Analysis
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS location_type VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS weather_conditions VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS lighting_quality VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS photo_quality VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS consistent_with_narrative BOOLEAN;

-- Cross-verification
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS narrative_match BOOLEAN;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS policy_match BOOLEAN;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS timeline_consistent BOOLEAN;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS verification_discrepancies JSONB DEFAULT '[]';

-- Risk Assessment
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS fraud_probability VARCHAR;

-- Final Assessment
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS overall_confidence_score FLOAT;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS human_review_priority VARCHAR;
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS recommended_actions JSONB DEFAULT '[]';

-- Metadata
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_provider VARCHAR DEFAULT 'groq';
ALTER TABLE forensic_analyses ADD COLUMN IF NOT EXISTS ai_model VARCHAR;

-- Update analysis_version to 2.0
UPDATE forensic_analyses SET analysis_version = '2.0';
"""

if __name__ == "__main__":
    print("Run this SQL in your PostgreSQL/SQLite database:")
    print(ALTER_TABLE_SQL)
