# AutoClaim AI Features Implementation Plan

## Overview
Add AI-powered analysis to the AutoClaim application:
- **Image Analysis**: Detect damage type, severity, affected parts (Gemini API)
- **EXIF Metadata**: Extract timestamp & GPS location from images
- **Number Plate OCR**: Extract vehicle registration using EasyOCR
- **Estimate Bill**: Upload repair estimate documents
- **Auto-Assessment**: Generate recommendations and cost estimates

---

## User Review Required

> [!IMPORTANT]
> **API Key Required**: Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

> [!NOTE]
> **New Upload Fields**: Users will upload:
> 1. Damage images (multiple)
> 2. Front view image (single - for number plate extraction)
> 3. Estimate bill (single - repair cost document)

---

## Proposed Changes

### Backend (`server/`)

---

#### [NEW] [ai_service.py](file:///c:/Users/basil/AutoClaim/autoclaim_project/server/ai_service.py)

```python
# Functions:
- extract_image_metadata(image_path) → {timestamp, gps_lat, gps_lon, location_name}
- extract_number_plate(front_image_path) → {plate_text, confidence}  # Using EasyOCR
- analyze_damage_images(image_paths) → {damage_type, severity, affected_parts}
- generate_assessment(all_data) → {recommendation, cost_estimate}
```

---

#### [MODIFY] [models.py](file:///c:/Users/basil/AutoClaim/autoclaim_project/server/models.py)

Add to `Claim` model:
```python
# New image fields
front_image_path = Column(String)      # Front view for plate extraction
estimate_bill_path = Column(String)    # Repair estimate document

# Extracted metadata
image_timestamp = Column(DateTime)     # From EXIF
image_location_lat = Column(Float)     # GPS latitude
image_location_lon = Column(Float)     # GPS longitude
image_location_name = Column(String)   # Reverse geocoded address

# OCR results
vehicle_number_plate = Column(String)  # Extracted plate text
plate_confidence = Column(Float)       # OCR confidence

# AI analysis
ai_analysis = Column(JSON)             # Full analysis
ai_recommendation = Column(String)     # approve/review/reject
estimated_cost_min = Column(Integer)
estimated_cost_max = Column(Integer)
```

---

#### [MODIFY] [main.py](file:///c:/Users/basil/AutoClaim/autoclaim_project/server/main.py)

Update `/upload-claim`:
- Accept `front_image` (single file) and `estimate_bill` (single file)
- Trigger EXIF extraction, OCR, and AI analysis
- Store all results in database

---

#### [MODIFY] [requirements.txt](file:///c:/Users/basil/AutoClaim/autoclaim_project/server/requirements.txt)

```
google-generativeai    # AI analysis
python-dotenv          # Environment variables
easyocr                # Number plate OCR
pillow                 # Image processing + EXIF
geopy                  # Reverse geocoding GPS → address
```

---

### Frontend (`client/src/`)

---

#### [MODIFY] [ClaimUpload.jsx](file:///c:/Users/basil/AutoClaim/autoclaim_project/client/src/components/ClaimUpload.jsx)

Add separate upload fields:
- **Damage Images** (multiple) - existing field
- **Front View Image** (single) - for number plate
- **Estimate Bill** (single) - PDF/image of repair estimate

---

#### [MODIFY] [AdminDashboard.jsx](file:///c:/Users/basil/AutoClaim/autoclaim_project/client/src/components/AdminDashboard.jsx)

Display extracted data:
- Image timestamp & location on map
- Extracted number plate
- AI damage analysis
- Cost estimate from bill

---

## Database Fields Summary

| Field | Type | Source |
|-------|------|--------|
| `front_image_path` | String | Upload |
| `estimate_bill_path` | String | Upload |
| `image_timestamp` | DateTime | EXIF |
| `image_location_lat/lon` | Float | EXIF GPS |
| `image_location_name` | String | Geocoding |
| `vehicle_number_plate` | String | EasyOCR |
| `plate_confidence` | Float | EasyOCR |
| `ai_analysis` | JSON | Gemini API |
| `ai_recommendation` | String | Gemini API |
| `estimated_cost_min/max` | Integer | Gemini API |

---

## Verification Plan

1. Upload claim with all 3 image types
2. Verify EXIF timestamp/location extracted
3. Verify number plate text extracted
4. Verify AI analysis stored in database
5. Verify all fields display in admin dashboard
