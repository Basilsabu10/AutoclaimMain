# Database ER Diagram - AutoClaim

## ER Diagram (5 Tables)

```mermaid
erDiagram
    USER ||--o{ POLICY : "has"
    USER ||--o{ CLAIM : "submits"
    POLICY_PLAN ||--o{ POLICY : "defines"
    POLICY ||--o{ CLAIM : "covers"
    CLAIM ||--|| FORENSIC_ANALYSIS : "has"
    
    USER {
        int id PK
        string email UK
        string password_hash
        string role
    }
    
    POLICY_PLAN {
        int id PK
        string name
        text description
        int coverage_amount
        float premium_monthly
        float premium_yearly
        int deductible
        json coverage_types
        bool is_active
        datetime created_at
    }
    
    POLICY {
        int id PK
        int user_id FK
        int plan_id FK
        string policy_number UK
        string vehicle_make
        string vehicle_model
        int vehicle_year
        string vehicle_registration
        datetime start_date
        datetime end_date
        string status
        datetime created_at
    }
    
    CLAIM {
        int id PK
        int user_id FK
        int policy_id FK
        text description
        json image_paths
        string status
        datetime created_at
        string front_image_path
        string estimate_bill_path
        string vehicle_number_plate
        string ai_recommendation
        int estimated_cost_min
        int estimated_cost_max
    }
    
    FORENSIC_ANALYSIS {
        int id PK
        int claim_id FK,UK
        datetime exif_timestamp
        float exif_gps_lat
        float exif_gps_lon
        string exif_location_name
        string ocr_plate_text
        float ocr_plate_confidence
        string ai_damage_type
        string ai_severity
        json ai_affected_parts
        string ai_recommendation
        int ai_cost_min
        int ai_cost_max
        datetime analyzed_at
    }
```

## Tables Summary

| Table | Columns | Purpose |
|-------|---------|---------|
| `users` | 4 | User accounts |
| `policy_plans` | 10 | Insurance plan templates |
| `policies` | 12 | User policy subscriptions |
| `claims` | 12 | Damage claims |
| `forensic_analyses` | 19 | AI analysis storage |

## Relationships
- User → Policies (1:N)
- User → Claims (1:N)
- PolicyPlan → Policies (1:N)
- Policy → Claims (1:N)
- Claim → ForensicAnalysis (1:1)

### Claim Table - OCR Fields
| Field | Type | Purpose |
|-------|------|---------|
| `vehicle_number_plate` | String | Extracted plate text |
| `plate_confidence` | Float | OCR confidence (0-1) |

### Claim Table - AI Analysis
| Field | Type | Purpose |
|-------|------|---------|
| `ai_analysis` | JSON | Full AI response |
| `ai_recommendation` | String | approve/review/reject |
| `estimated_cost_min` | Integer | Cost estimate low |
| `estimated_cost_max` | Integer | Cost estimate high |
