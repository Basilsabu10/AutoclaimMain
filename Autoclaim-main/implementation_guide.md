# QUICK IMPLEMENTATION GUIDE
## AutoClaim AI Damage Analysis - Integration Checklist

---

## 1. PRE-DEPLOYMENT SETUP

### Database Schema Updates
```sql
-- Add new columns to existing tables per SRS requirements

ALTER TABLE claims ADD COLUMN IF NOT EXISTS 
  ai_analysis_json JSONB,
  metadata_verified BOOLEAN DEFAULT FALSE,
  forgery_detected BOOLEAN DEFAULT FALSE,
  pre_existing_damage BOOLEAN DEFAULT FALSE;

ALTER TABLE evidence ADD COLUMN IF NOT EXISTS
  analysis_id UUID,
  exif_data JSONB,
  damage_score DECIMAL(5,2),
  confidence_scores JSONB;

CREATE INDEX idx_claims_confidence ON claims(ai_confidence_score);
CREATE INDEX idx_evidence_analysis ON evidence(analysis_id);
CREATE INDEX idx_claims_status_date ON claims(status, created_at);
```

### Environment Variables
```bash
# .env file
AI_MODEL_ENDPOINT=https://your-model-api.com/v1/analyze
WEATHER_API_KEY=your_weather_api_key
REVERSE_IMAGE_SEARCH_API=your_reverse_search_key
DATABASE_URL=postgresql://user:pass@localhost:5432/autoclaim
CONFIDENCE_THRESHOLD=90.00
COST_THRESHOLD=20000
MAX_IMAGE_SIZE_MB=10
```

---

## 2. API ENDPOINT IMPLEMENTATION

### FastAPI Route Example
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import uuid
from datetime import datetime

app = FastAPI()

class ClaimSubmission(BaseModel):
    claim_id: str
    user_id: str
    narrative: str
    claimed_location: dict  # {"lat": float, "lon": float}
    claimed_datetime: str
    policy_vehicle: dict  # {"make": str, "model": str, "plate": str}

@app.post("/api/v1/claims/analyze")
async def analyze_damage(
    image: UploadFile = File(...),
    claim_data: str = Form(...)  # JSON string
):
    # 1. Parse and validate input
    claim = ClaimSubmission(**json.loads(claim_data))
    
    # 2. Validate image
    if image.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "Image exceeds 10MB limit")
    
    allowed_types = ["image/jpeg", "image/png", "image/heic"]
    if image.content_type not in allowed_types:
        raise HTTPException(400, "Invalid image format")
    
    # 3. Save image temporarily
    analysis_id = str(uuid.uuid4())
    file_path = f"/tmp/{analysis_id}_{image.filename}"
    with open(file_path, "wb") as f:
        f.write(await image.read())
    
    # 4. Build AI prompt with actual data
    prompt = build_analysis_prompt(
        file_path=file_path,
        claim_id=claim.claim_id,
        narrative=claim.narrative,
        policy_data=claim.policy_vehicle,
        claimed_location=claim.claimed_location,
        claimed_datetime=claim.claimed_datetime
    )
    
    # 5. Call AI analysis service
    ai_response = await call_ai_analyzer(
        image_path=file_path,
        prompt=prompt
    )
    
    # 6. Validate response against schema
    validated_response = validate_ai_response(ai_response)
    
    # 7. Cross-check with database
    enriched_response = await cross_verify_with_db(
        validated_response,
        claim.user_id,
        claim.policy_vehicle
    )
    
    # 8. Store results
    await store_analysis_results(
        claim_id=claim.claim_id,
        analysis_data=enriched_response
    )
    
    # 9. Return decision
    return {
        "claim_id": claim.claim_id,
        "analysis_id": analysis_id,
        "recommendation": enriched_response["final_assessment"]["recommendation"],
        "confidence_score": enriched_response["final_assessment"]["overall_confidence_score"],
        "next_steps": get_next_steps(enriched_response)
    }

def build_analysis_prompt(file_path, claim_id, narrative, policy_data, 
                          claimed_location, claimed_datetime):
    """Replace placeholders in template prompt with actual values"""
    from ai_analysis_prompt import TASK_SPECIFIC_PROMPT
    
    return TASK_SPECIFIC_PROMPT \
        .replace("[FILE_NAME(S)]", file_path) \
        .replace("[CLAIM_ID]", claim_id) \
        .replace("[USER_DESCRIPTION]", narrative) \
        .replace("[MAKE]", policy_data["make"]) \
        .replace("[MODEL]", policy_data["model"]) \
        .replace("[PLATE]", policy_data["plate"]) \
        .replace("[LOCATION]", f"{claimed_location['lat']}, {claimed_location['lon']}") \
        .replace("[DATE]", claimed_datetime)

async def call_ai_analyzer(image_path: str, prompt: str):
    """Call your AI model (e.g., GPT-4 Vision, Claude Vision, or custom model)"""
    import base64
    import httpx
    
    # Read and encode image
    with open(image_path, "rb") as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode()
    
    # Example: OpenAI GPT-4 Vision API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT  # From ai_analysis_prompt.md
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 4096,
                "temperature": 0.1  # Low temperature for consistency
            },
            timeout=60.0
        )
        return response.json()["choices"][0]["message"]["content"]

def validate_ai_response(ai_response: str) -> dict:
    """Validate JSON response against Pydantic schema"""
    try:
        # Remove markdown code blocks if present
        if ai_response.startswith("```json"):
            ai_response = ai_response.split("```json")[1].split("```")[0].strip()
        
        data = json.loads(ai_response)
        
        # Pydantic validation (define models based on schema)
        from models import DamageAnalysisResponse
        validated = DamageAnalysisResponse(**data)
        
        return validated.dict()
    except Exception as e:
        # Fallback to human review if AI response invalid
        return {
            "final_assessment": {
                "recommendation": "ESCALATE_TO_AGENT",
                "decision_reasoning": f"AI response validation failed: {str(e)}",
                "overall_confidence_score": 0.0
            }
        }

async def cross_verify_with_db(analysis_data: dict, user_id: str, policy_data: dict):
    """Perform database cross-checks"""
    import asyncpg
    
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    try:
        # 1. Check for duplicate claims
        duplicate_check = await conn.fetchval("""
            SELECT COUNT(*) FROM claims 
            WHERE user_id = $1 
              AND status != 'Rejected'
              AND created_at > NOW() - INTERVAL '30 days'
        """, user_id)
        
        if duplicate_check > 3:
            analysis_data["risk_flags"].append({
                "flag_type": "MEDIUM_RISK",
                "category": "SUSPICIOUS_PATTERN",
                "description": f"User has {duplicate_check} claims in past 30 days",
                "action_required": "HUMAN_REVIEW"
            })
        
        # 2. Verify policy active
        policy_active = await conn.fetchval("""
            SELECT policy_status FROM policies
            WHERE user_id = $1 AND license_plate = $2
        """, user_id, policy_data["plate"])
        
        if policy_active != "ACTIVE":
            analysis_data["final_assessment"]["recommendation"] = "REJECT"
            analysis_data["final_assessment"]["decision_reasoning"] = "Policy not active"
        
        # 3. Check historical weather
        if analysis_data.get("image_metadata", {}).get("exif_data", {}).get("gps_coordinates"):
            gps = analysis_data["image_metadata"]["exif_data"]["gps_coordinates"]
            timestamp = analysis_data["image_metadata"]["exif_data"]["timestamp"]
            
            if gps["status"] == "PRESENT" and timestamp:
                historical_weather = await get_historical_weather(
                    gps["latitude"], 
                    gps["longitude"], 
                    timestamp
                )
                analysis_data["cross_verification_checks"]["metadata_verification"]["weather_consistency"]["historical_weather"] = historical_weather
        
        return analysis_data
        
    finally:
        await conn.close()

async def store_analysis_results(claim_id: str, analysis_data: dict):
    """Save to database"""
    import asyncpg
    
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    try:
        # Update claims table
        await conn.execute("""
            UPDATE claims SET
                ai_confidence_score = $1,
                status = $2,
                flagged_reason = $3,
                ai_analysis_json = $4,
                metadata_verified = $5,
                forgery_detected = $6,
                pre_existing_damage = $7,
                updated_at = NOW()
            WHERE claim_id = $8
        """,
            analysis_data["final_assessment"]["overall_confidence_score"],
            map_recommendation_to_status(analysis_data["final_assessment"]["recommendation"]),
            analysis_data["final_assessment"]["decision_reasoning"],
            json.dumps(analysis_data),
            analysis_data["cross_verification_checks"]["metadata_verification"]["timestamp_match"]["match"],
            analysis_data["forensic_analysis"]["forgery_detection"]["ela_analysis"]["status"] == "FAIL",
            analysis_data["pre_existing_damage_indicators"]["detected"],
            claim_id
        )
        
        # Insert evidence records
        for location in analysis_data["damage_assessment"]["damage_locations"]:
            await conn.execute("""
                INSERT INTO evidence 
                (claim_id, analysis_id, file_path, metadata_gps, 
                 damage_score, confidence_scores, is_forged, 
                 rust_detected, plate_number_detected)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
                claim_id,
                analysis_data["analysis_id"],
                analysis_data["image_metadata"]["file_name"],
                json.dumps(analysis_data["image_metadata"]["exif_data"]["gps_coordinates"]),
                analysis_data["damage_assessment"]["total_damage_score"],
                json.dumps({"damage_confidence": location["confidence"]}),
                analysis_data["forensic_analysis"]["forgery_detection"]["ela_analysis"]["status"] == "FAIL",
                analysis_data["pre_existing_damage_indicators"]["detected"],
                analysis_data["vehicle_identification"]["license_plate"]["number"]
            )
    
    finally:
        await conn.close()

def map_recommendation_to_status(recommendation: str) -> str:
    """Convert AI recommendation to claim status"""
    mapping = {
        "AUTO_APPROVE": "Approved",
        "ESCALATE_TO_AGENT": "Escalated",
        "REJECT": "Rejected",
        "REQUEST_MORE_EVIDENCE": "Pending"
    }
    return mapping.get(recommendation, "Pending")

def get_next_steps(analysis_data: dict) -> str:
    """Generate user-facing next steps message"""
    recommendation = analysis_data["final_assessment"]["recommendation"]
    
    messages = {
        "AUTO_APPROVE": "Your claim has been approved! Payment will be processed within 48 hours.",
        "ESCALATE_TO_AGENT": "Your claim requires additional review. An agent will contact you within 24 hours.",
        "REJECT": f"Your claim has been declined. Reason: {analysis_data['final_assessment']['decision_reasoning']}",
        "REQUEST_MORE_EVIDENCE": "Please upload additional photos from different angles."
    }
    
    return messages.get(recommendation, "Your claim is being processed.")

# Helper functions
async def get_historical_weather(lat: float, lon: float, timestamp: str):
    """Fetch historical weather from external API"""
    import httpx
    from datetime import datetime
    
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weatherapi.com/v1/history.json",
            params={
                "key": os.getenv('WEATHER_API_KEY'),
                "q": f"{lat},{lon}",
                "dt": dt.strftime('%Y-%m-%d')
            }
        )
        data = response.json()
        return data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
```

---

## 3. FRONTEND INTEGRATION

### React Component Example
```javascript
import React, { useState } from 'react';
import axios from 'axios';

function ClaimSubmission() {
  const [image, setImage] = useState(null);
  const [narrative, setNarrative] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAnalyzing(true);

    const formData = new FormData();
    formData.append('image', image);
    formData.append('claim_data', JSON.stringify({
      claim_id: generateClaimId(),
      user_id: getUserId(),
      narrative: narrative,
      claimed_location: await getCurrentLocation(),
      claimed_datetime: new Date().toISOString(),
      policy_vehicle: getUserPolicyData()
    }));

    try {
      const response = await axios.post('/api/v1/claims/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (error) {
      alert('Analysis failed: ' + error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="claim-form">
      <h2>Submit Your Claim</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          placeholder="Describe what happened..."
          value={narrative}
          onChange={(e) => setNarrative(e.target.value)}
          required
        />
        <input
          type="file"
          accept="image/jpeg,image/png"
          onChange={(e) => setImage(e.target.files[0])}
          required
        />
        <button type="submit" disabled={analyzing}>
          {analyzing ? 'Analyzing...' : 'Submit Claim'}
        </button>
      </form>

      {result && (
        <div className={`result result-${result.recommendation.toLowerCase()}`}>
          <h3>Analysis Complete</h3>
          <p><strong>Confidence:</strong> {result.confidence_score}%</p>
          <p><strong>Status:</strong> {result.recommendation}</p>
          <p>{result.next_steps}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 4. TESTING CHECKLIST

### Unit Tests
- [ ] JSON schema validation with valid/invalid inputs
- [ ] Confidence score calculation accuracy
- [ ] Enum value validation (all fields)
- [ ] Bounding box coordinate validation
- [ ] Database query performance

### Integration Tests
- [ ] End-to-end claim submission flow
- [ ] AI API timeout handling
- [ ] Database transaction rollback on error
- [ ] File upload size limits
- [ ] Concurrent request handling

### AI Model Tests
- [ ] Test with 50+ labeled images (ground truth)
- [ ] Measure precision/recall for damage detection
- [ ] Verify confidence calibration (90% score = 90% accuracy)
- [ ] Test forgery detection with synthetic manipulated images
- [ ] ANPR accuracy across different plate types

### Edge Case Tests
- [ ] Missing EXIF data
- [ ] Multiple vehicles in frame
- [ ] Night/low-light photos
- [ ] Blurry/out-of-focus images
- [ ] Partial vehicle visibility
- [ ] Severely damaged vehicles (totaled)

---

## 5. MONITORING & ALERTS

### Key Metrics to Track
```python
# Prometheus metrics example
from prometheus_client import Counter, Histogram, Gauge

claims_processed = Counter('claims_processed_total', 'Total claims processed', ['status'])
processing_duration = Histogram('claim_processing_seconds', 'Time to process claim')
confidence_distribution = Histogram('ai_confidence_scores', 'Distribution of confidence scores')
auto_approval_rate = Gauge('auto_approval_rate', 'Percentage of auto-approved claims')
fraud_detection_rate = Gauge('fraud_detection_rate', 'Percentage of flagged claims')
```

### Alert Rules
```yaml
# alerts.yml
groups:
  - name: autoclaim_alerts
    rules:
      - alert: HighProcessingTime
        expr: claim_processing_seconds > 30
        annotations:
          summary: "Claim processing took over 30 seconds"
      
      - alert: LowConfidenceSpike
        expr: rate(ai_confidence_scores{bucket="0-50"}[5m]) > 0.3
        annotations:
          summary: "Unusual spike in low-confidence scores"
      
      - alert: AutoApprovalRateDrop
        expr: auto_approval_rate < 0.4
        annotations:
          summary: "Auto-approval rate below 40%"
```

---

## 6. DEPLOYMENT CHECKLIST

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] AI model endpoint tested and accessible
- [ ] External API keys validated (weather, reverse search)
- [ ] Logging configured (INFO for normal, DEBUG for development)
- [ ] Error tracking setup (Sentry, Rollbar)
- [ ] Load balancer configured for API
- [ ] CDN setup for image serving
- [ ] Backup strategy for analysis JSON data
- [ ] Compliance review (GDPR, data retention policies)

---

## 7. TROUBLESHOOTING GUIDE

### Issue: AI Returns Invalid JSON
**Solution**: Check `technical_metadata.error_log` for parsing errors. Add retry logic with prompt refinement.

### Issue: Low Confidence Scores Across All Claims
**Solution**: Recalibrate confidence thresholds. May need model fine-tuning.

### Issue: High False Positive Rate (Approving Fraud)
**Solution**: Lower `CONFIDENCE_THRESHOLD` from 90 to 95. Increase weight of forgery detection.

### Issue: Database Timeouts During Peak Load
**Solution**: Implement connection pooling. Use async database drivers (asyncpg).

### Issue: ANPR Failing on Regional Plates
**Solution**: Retrain OCR model with regional plate samples. Add manual review fallback.

---

**Last Updated**: 2026-02-06  
**Version**: 1.0.0
