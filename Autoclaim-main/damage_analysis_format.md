# STRICT DATA FORMAT SPECIFICATION
## AI Vehicle Damage Analysis - AutoClaim System

---

## 1. STANDARDIZED OUTPUT FORMAT (JSON Schema)

```json
{
  "analysis_id": "string (UUID v4)",
  "timestamp": "string (ISO 8601: YYYY-MM-DDTHH:mm:ss.sssZ)",
  "image_metadata": {
    "file_name": "string",
    "file_size_bytes": "integer",
    "dimensions": {
      "width": "integer",
      "height": "integer"
    },
    "format": "string (JPEG|PNG|HEIC)",
    "exif_data": {
      "gps_coordinates": {
        "latitude": "float (6 decimal places)",
        "longitude": "float (6 decimal places)",
        "status": "string (PRESENT|ABSENT|STRIPPED)"
      },
      "timestamp": "string (ISO 8601) | null",
      "device_make": "string | null",
      "device_model": "string | null",
      "camera_settings": {
        "iso": "integer | null",
        "aperture": "string | null",
        "shutter_speed": "string | null"
      }
    }
  },
  
  "forensic_analysis": {
    "authenticity_score": "float (0.00-100.00, 2 decimals)",
    "forgery_detection": {
      "ela_analysis": {
        "status": "string (PASS|FAIL|INCONCLUSIVE)",
        "anomaly_regions": [
          {
            "bounding_box": {"x": "int", "y": "int", "width": "int", "height": "int"},
            "severity": "string (LOW|MEDIUM|HIGH|CRITICAL)"
          }
        ],
        "confidence": "float (0.00-100.00)"
      },
      "noise_analysis": {
        "status": "string (PASS|FAIL|INCONCLUSIVE)",
        "inconsistencies_detected": "boolean",
        "confidence": "float (0.00-100.00)"
      },
      "reverse_image_search": {
        "status": "string (ORIGINAL|DUPLICATE_FOUND|ERROR)",
        "match_count": "integer",
        "top_match_url": "string | null",
        "similarity_score": "float (0.00-100.00) | null"
      }
    },
    "digital_manipulation_indicators": [
      "string (e.g., 'Clone stamp detected', 'Inconsistent lighting', 'JPEG artifacts')"
    ]
  },

  "vehicle_identification": {
    "detection_status": "string (DETECTED|NOT_DETECTED|MULTIPLE_VEHICLES)",
    "vehicle_details": {
      "make": "string | null",
      "model": "string | null",
      "year": "integer | null",
      "color": "string (standardized: BLACK|WHITE|SILVER|RED|BLUE|GREEN|YELLOW|ORANGE|BROWN|GREY|OTHER)",
      "confidence": "float (0.00-100.00)"
    },
    "license_plate": {
      "detected": "boolean",
      "number": "string (uppercase, no spaces) | null",
      "region": "string (state/province code) | null",
      "confidence": "float (0.00-100.00)",
      "ocr_method": "string (ANPR|MANUAL_REVIEW_REQUIRED)",
      "plate_condition": "string (CLEAR|PARTIALLY_OBSCURED|DIRTY|DAMAGED|ILLEGIBLE)"
    },
    "vin_visible": "boolean",
    "vin_number": "string | null"
  },

  "damage_assessment": {
    "damage_detected": "boolean",
    "damage_locations": [
      {
        "panel": "string (FRONT_BUMPER|REAR_BUMPER|HOOD|TRUNK|DOOR_FL|DOOR_FR|DOOR_RL|DOOR_RR|FENDER_FL|FENDER_FR|FENDER_RL|FENDER_RR|ROOF|WINDSHIELD|REAR_WINDOW|SIDE_WINDOW_L|SIDE_WINDOW_R|HEADLIGHT_L|HEADLIGHT_R|TAILLIGHT_L|TAILLIGHT_R|MIRROR_L|MIRROR_R|WHEEL_FL|WHEEL_FR|WHEEL_RL|WHEEL_RR|UNDERCARRIAGE|OTHER)",
        "damage_type": "string (DENT|SCRATCH|CRACK|SHATTERED|TEAR|CRUSHED|BENT|BROKEN|PAINT_DAMAGE|MISSING_PART)",
        "severity": "string (MINOR|MODERATE|SEVERE|TOTALED)",
        "bounding_box": {
          "x": "integer",
          "y": "integer", 
          "width": "integer",
          "height": "integer"
        },
        "area_percentage": "float (0.00-100.00, % of panel affected)",
        "confidence": "float (0.00-100.00)"
      }
    ],
    "estimated_damage_cost": {
      "min": "float (currency)",
      "max": "float (currency)",
      "currency": "string (INR|USD|EUR)",
      "confidence": "float (0.00-100.00)"
    },
    "total_damage_score": "float (0.00-100.00, weighted severity index)"
  },

  "pre_existing_damage_indicators": {
    "detected": "boolean",
    "indicators": [
      {
        "type": "string (RUST|OXIDATION|PAINT_FADING|DIRT_ACCUMULATION|OLD_REPAIR_MARKS|WEATHERING|PREVIOUS_DENT)",
        "location": "string (panel name)",
        "confidence": "float (0.00-100.00)",
        "evidence": "string (description)"
      }
    ],
    "overall_condition": "string (NEW|GOOD|FAIR|POOR|HEAVILY_WORN)"
  },

  "contextual_analysis": {
    "environment": {
      "lighting_condition": "string (DAYLIGHT|OVERCAST|DUSK|NIGHT|ARTIFICIAL_LIGHT|MIXED)",
      "weather_apparent": "string (CLEAR|RAINY|SNOWY|FOGGY|UNKNOWN)",
      "location_type": "string (HIGHWAY|CITY_STREET|PARKING_LOT|RESIDENTIAL|RURAL|UNKNOWN)",
      "shadows_present": "boolean",
      "shadow_direction": "string (N|NE|E|SE|S|SW|W|NW) | null"
    },
    "collision_indicators": {
      "debris_present": "boolean",
      "debris_types": ["string (GLASS|PLASTIC|METAL|PAINT_CHIPS|FLUID_LEAK)"],
      "impact_direction": "string (FRONT|REAR|SIDE_LEFT|SIDE_RIGHT|ROLLOVER|MULTIPLE) | null",
      "airbag_deployed": "boolean | null",
      "consistency_with_claim": "string (CONSISTENT|INCONSISTENT|UNCLEAR)"
    }
  },

  "cross_verification_checks": {
    "policy_match": {
      "vehicle_make_model_match": "boolean | null",
      "license_plate_match": "boolean | null",
      "vin_match": "boolean | null",
      "mismatch_details": "string | null"
    },
    "metadata_verification": {
      "gps_location_match": {
        "claimed_location": "string (lat, lon)",
        "photo_location": "string (lat, lon) | null",
        "distance_km": "float | null",
        "match": "boolean | null"
      },
      "timestamp_match": {
        "claimed_datetime": "string (ISO 8601)",
        "photo_datetime": "string (ISO 8601) | null",
        "time_difference_minutes": "integer | null",
        "match": "boolean | null"
      },
      "weather_consistency": {
        "claimed_weather": "string | null",
        "photo_weather": "string | null",
        "historical_weather": "string | null",
        "match": "boolean | null"
      }
    },
    "narrative_consistency": {
      "claim_description": "string (user narrative)",
      "visual_evidence_matches": "boolean",
      "inconsistencies": ["string (description of mismatches)"],
      "consistency_score": "float (0.00-100.00)"
    }
  },

  "risk_flags": [
    {
      "flag_type": "string (HIGH_RISK|MEDIUM_RISK|LOW_RISK)",
      "category": "string (FORGERY|MISMATCH|PRE_EXISTING|METADATA_ISSUE|NARRATIVE_CONFLICT|SUSPICIOUS_PATTERN)",
      "description": "string (detailed explanation)",
      "action_required": "string (AUTO_REJECT|HUMAN_REVIEW|REQUEST_ADDITIONAL_INFO)"
    }
  ],

  "final_assessment": {
    "overall_confidence_score": "float (0.00-100.00, weighted average of all checks)",
    "recommendation": "string (AUTO_APPROVE|ESCALATE_TO_AGENT|REJECT|REQUEST_MORE_EVIDENCE)",
    "decision_reasoning": "string (concise explanation for recommendation)",
    "human_review_priority": "string (IMMEDIATE|HIGH|MEDIUM|LOW|NONE)",
    "estimated_processing_time": "integer (seconds)"
  },

  "technical_metadata": {
    "ai_model_version": "string (e.g., 'damage-detection-v2.3.1')",
    "processing_duration_ms": "integer",
    "modules_executed": ["string (e.g., 'EXIF', 'ELA', 'ANPR', 'Object_Detection')"],
    "error_log": ["string (any warnings or errors encountered)"]
  }
}
```

---

## 2. FIELD VALIDATION RULES

### 2.1 Mandatory Fields (Cannot be NULL)
- `analysis_id`
- `timestamp`
- `image_metadata.file_name`
- `image_metadata.format`
- `forensic_analysis.authenticity_score`
- `damage_assessment.damage_detected`
- `final_assessment.overall_confidence_score`
- `final_assessment.recommendation`

### 2.2 Conditional Requirements
- IF `damage_detected = true` → `damage_locations` MUST contain ≥1 entry
- IF `license_plate.detected = true` → `license_plate.number` MUST NOT be null
- IF `recommendation = "ESCALATE_TO_AGENT"` → `risk_flags` MUST contain ≥1 entry
- IF `recommendation = "REJECT"` → `decision_reasoning` MUST include specific failure reason

### 2.3 Data Type Constraints
- All confidence scores: 0.00-100.00 (2 decimal precision)
- All bounding boxes: Non-negative integers
- GPS coordinates: -90.000000 to 90.000000 (latitude), -180.000000 to 180.000000 (longitude)
- Timestamps: UTC timezone (ISO 8601)
- Currency values: 2 decimal places

### 2.4 Enum Validation
All enum fields MUST use EXACT values from predefined lists (see JSON schema above). No variations or custom values allowed.

---

## 3. QUALITY ASSURANCE THRESHOLDS

### 3.1 Minimum Confidence Requirements
| Check Type | Minimum Confidence for Auto-Approval |
|------------|-------------------------------------|
| Forensic Analysis (Authenticity) | 85.00% |
| Vehicle Identification | 90.00% |
| License Plate OCR | 95.00% |
| Damage Detection | 80.00% |
| Narrative Consistency | 75.00% |
| **Overall Confidence** | **90.00%** |

### 3.2 Auto-Rejection Triggers
- Forgery detected with confidence > 70%
- License plate mismatch
- VIN mismatch (if visible)
- GPS location > 10km from claimed location
- Timestamp difference > 48 hours from claimed time
- Reverse image search finds exact duplicate

---

## 4. ERROR HANDLING PROTOCOL

### 4.1 Missing/Corrupt EXIF Data
```json
{
  "exif_data": {
    "gps_coordinates": {"status": "STRIPPED"},
    "timestamp": null
  },
  "risk_flags": [{
    "flag_type": "MEDIUM_RISK",
    "category": "METADATA_ISSUE",
    "description": "EXIF data absent or stripped - potential authenticity concern",
    "action_required": "HUMAN_REVIEW"
  }]
}
```

### 4.2 Multiple Vehicles Detected
```json
{
  "vehicle_identification": {
    "detection_status": "MULTIPLE_VEHICLES"
  },
  "risk_flags": [{
    "flag_type": "MEDIUM_RISK",
    "category": "SUSPICIOUS_PATTERN",
    "description": "Multiple vehicles in frame - requires verification of claimed vehicle",
    "action_required": "REQUEST_ADDITIONAL_INFO"
  }]
}
```

### 4.3 Processing Failures
If any module fails critically, return:
```json
{
  "final_assessment": {
    "recommendation": "ESCALATE_TO_AGENT",
    "decision_reasoning": "Technical error in [MODULE_NAME] - manual review required"
  },
  "technical_metadata": {
    "error_log": ["Detailed error message with stack trace"]
  }
}
```

---

## 5. DATABASE INTEGRATION MAPPING

### 5.1 Claims Table Updates
```sql
UPDATE claims SET
  ai_confidence_score = final_assessment.overall_confidence_score,
  status = CASE 
    WHEN final_assessment.recommendation = 'AUTO_APPROVE' THEN 'Approved'
    WHEN final_assessment.recommendation = 'REJECT' THEN 'Rejected'
    ELSE 'Escalated'
  END,
  flagged_reason = final_assessment.decision_reasoning
WHERE claim_id = ?;
```

### 5.2 Evidence Table Updates
```sql
INSERT INTO evidence (claim_id, file_path, metadata_gps, is_forged, rust_detected, plate_number_detected)
VALUES (
  ?,
  image_metadata.file_name,
  jsonb_build_object('lat', exif_data.gps_coordinates.latitude, 'lon', exif_data.gps_coordinates.longitude),
  forensic_analysis.forgery_detection.ela_analysis.status = 'FAIL',
  pre_existing_damage_indicators.detected,
  vehicle_identification.license_plate.number
);
```

---

## 6. CROSS-REFERENCE QUERIES FOR VALIDATION

### 6.1 Policy Database Lookup
```sql
SELECT vehicle_make, vehicle_model, license_plate, vin
FROM policies
WHERE user_id = ? AND policy_status = 'ACTIVE';
```

### 6.2 Historical Claims Check (Fraud Detection)
```sql
SELECT COUNT(*) as claim_count, 
       SUM(claim_amount) as total_claimed
FROM claims
WHERE user_id = ? 
  AND created_at > NOW() - INTERVAL '1 year'
  AND status != 'Rejected';
```

### 6.3 Weather API Integration
```python
# Example API call for historical weather verification
import requests
response = requests.get(
    f"https://api.weather.com/historical",
    params={
        "lat": metadata.gps_coordinates.latitude,
        "lon": metadata.gps_coordinates.longitude,
        "date": metadata.timestamp,
        "api_key": WEATHER_API_KEY
    }
)
historical_weather = response.json()["condition"]
```

---

## 7. VERSIONING & CHANGELOG

**Current Version**: 1.0.0  
**Last Updated**: 2026-02-06  

### Version History
- v1.0.0 (2026-02-06): Initial specification release

### Future Enhancements
- v1.1.0: Add 3D damage modeling coordinates
- v1.2.0: Integrate telematics data (if available)
- v2.0.0: Multi-image analysis correlation

---

**Note**: All timestamps in this specification use UTC. Convert to local timezone for user-facing displays only.
