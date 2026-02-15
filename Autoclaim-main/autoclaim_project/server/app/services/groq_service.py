"""
Enhanced Groq service with comprehensive forensic analysis.
Implements full 8-phase workflow from ai_analysis_prompt.md
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional
from groq import Groq
from app.core.config import settings

# Initialize Groq client
groq_client = None
GROQ_AVAILABLE = False

def init_groq() -> bool:
    """Initialize Groq client."""
    global groq_client, GROQ_AVAILABLE
    
    if not settings.GROQ_API_KEY:
        print("[WARNING] GROQ_API_KEY not set")
        return False
    
    try:
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        GROQ_AVAILABLE = True
        print("[OK] Groq client initialized")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize Groq: {e}")
        return False


def encode_image_base64(image_path: str) -> Optional[str]:
    """
    Encode image to base64 with compression to avoid request_too_large errors.
    Resizes large images and compresses to reduce payload size.
    """
    try:
        from PIL import Image
        import io
        
        # Open and compress image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (removes alpha channel)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Resize if too large (max 1920x1080 to reduce payload)
        max_size = (1920, 1080)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"[INFO] Resized image from {Image.open(image_path).size} to {img.size}")
        
        # Compress to JPEG with quality 85
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # Encode to base64
        encoded = base64.b64encode(buffer.read()).decode('utf-8')
        
        # Check size (warn if still large)
        size_kb = len(encoded) / 1024
        if size_kb > 500:
            print(f"[WARNING] Compressed image still {size_kb:.0f}KB - may hit API limits")
        
        return encoded
        
    except Exception as e:
        print(f"[ERROR] Failed to encode image: {e}")
        return None


def build_comprehensive_prompt(description: str, yolo_context: Optional[Dict] = None, policy_data: Optional[Dict] = None) -> str:
    """
    Build comprehensive forensic analysis prompt.
    Based on ai_analysis_prompt.md specification.
    """
    
    # Extract policy data if provided
    policy_info = ""
    if policy_data:
        policy_info = f"""
Policy Data: Make={policy_data.get('vehicle_make', 'UNKNOWN')}, Model={policy_data.get('vehicle_model', 'UNKNOWN')}, 
Plate={policy_data.get('vehicle_registration', 'UNKNOWN')}, Location={policy_data.get('location', 'UNKNOWN')}"""
    
    # Extract YOLO context if provided
    yolo_info = ""
    if yolo_context and yolo_context.get('success'):
        yolo_info = f"""
YOLOv8 Pre-Analysis Results:
- Damage Detected: {yolo_context.get('damage_detected', False)}
- Severity: {yolo_context.get('severity', 'none')}
- Detections: {len(yolo_context.get('detections', []))} areas
- Summary: {yolo_context.get('summary', 'No summary')}"""
    
    prompt = f"""You are an expert forensic vehicle damage analyst with 20+ years of experience in insurance fraud detection, automotive engineering, and digital forensics.

TASK: Analyze the provided vehicle damage image(s) and generate a complete forensic assessment.

INPUT PROVIDED:
- User narrative: "{description if description else 'No description provided'}"{policy_info}{yolo_info}

ANALYSIS WORKFLOW (Execute in this exact order):

═══════════════════════════════════════════════════════════════════
PHASE 1: IMAGE INTEGRITY & METADATA VALIDATION
═══════════════════════════════════════════════════════════════════
- Assess image authenticity (look for editing signs, inconsistent lighting, cloning artifacts)
- Check for digital manipulation indicators
- Assign authenticity_score (0-100, where 100 = completely authentic)
- List any forgery indicators detected

═══════════════════════════════════════════════════════════════════
PHASE 2: VEHICLE IDENTIFICATION
═══════════════════════════════════════════════════════════════════
- Detect and identify vehicle make, model, year (if visible)
- Detect vehicle color
- Identify license plate (if visible)
- Cross-reference with policy data (if plate visible)

═══════════════════════════════════════════════════════════════════
PHASE 3: DAMAGE ASSESSMENT
═══════════════════════════════════════════════════════════════════
- Identify ALL damaged panels and parts
- Classify damage type: DENT, SCRATCH, CRACK, SHATTERED, CRUSHED, BROKEN, PAINT_DAMAGE, MISSING_PART
- Assess severity: MINOR (cosmetic), MODERATE (functional impact), SEVERE (safety-critical), TOTALED
- Estimate repair costs (USD)

═══════════════════════════════════════════════════════════════════
PHASE 4: PRE-EXISTING DAMAGE DETECTION
═══════════════════════════════════════════════════════════════════
- Look for rust, weathering, old paint repairs
- Identify unrelated damage (different impact patterns, aged damage)
- Distinguish fresh damage from old damage

═══════════════════════════════════════════════════════════════════
PHASE 5: CONTEXTUAL & ENVIRONMENTAL ANALYSIS
═══════════════════════════════════════════════════════════════════
- Analyze location type: street, parking lot, highway, residential
- Assess weather/lighting conditions
- Check if damage is consistent with narrative

═══════════════════════════════════════════════════════════════════
PHASE 6: CROSS-VERIFICATION
═══════════════════════════════════════════════════════════════════
- Verify damage matches user description
- Check timeline consistency
- Flag any discrepancies

═══════════════════════════════════════════════════════════════════
PHASE 7: RISK ASSESSMENT
═══════════════════════════════════════════════════════════════════
Assign risk flags (if applicable):
- FRAUD_INDICATORS_PRESENT
- PRE_EXISTING_DAMAGE_DETECTED
- INCONSISTENT_NARRATIVE
- POLICY_MISMATCH
- STAGED_DAMAGE_SUSPECTED
- METADATA_STRIPPED
- IMAGE_MANIPULATED
- EXCESSIVE_CLAIM_AMOUNT
- INSUFFICIENT_EVIDENCE

═══════════════════════════════════════════════════════════════════
PHASE 8: FINAL ASSESSMENT
═══════════════════════════════════════════════════════════════════
- Overall confidence score (0-100)
- Recommendation: APPROVE, REVIEW, REJECT
- Human review priority: LOW, MEDIUM, HIGH, CRITICAL


RESPOND WITH ONLY VALID JSON (no markdown, no code blocks):

{{
  "forensic_analysis": {{
    "authenticity_score": 0-100,
    "forgery_indicators": ["list of any manipulation signs detected"],
    "digital_manipulation_detected": true/false,
    "manipulation_confidence": 0-100
  }},
  "vehicle_identification": {{
    "make": "detected make or UNKNOWN",
    "model": "detected model or UNKNOWN",
    "year": "YYYY or UNKNOWN",
    "color": "primary color or UNKNOWN",
    "license_plate": {{
      "detected": true/false,
      "text": "plate number or null",
      "confidence": 0-100,
      "match_status": "MATCH | MISMATCH | UNKNOWN"
    }},
    "vin_detected": true/false,
    "identification_confidence": 0-100
  }},
  "damage_assessment": {{
    "damage_detected": true/false,
    "damaged_panels": [
      {{
        "panel_name": "FRONT_BUMPER | DOOR_FL | etc",
        "damage_type": "DENT | SCRATCH | etc",
        "severity": "MINOR | MODERATE | SEVERE",
        "area_percentage": 0-100,
        "confidence": 0-100
      }}
    ],
    "overall_severity": "NONE | MINOR | MODERATE | SEVERE | TOTALED",
    "estimated_repair_cost": {{
      "min_usd": 0,
      "max_usd": 0,
      "confidence": 0-100
    }},
    "structural_damage": true/false,
    "safety_concerns": ["list any safety issues"]
  }},
  "pre_existing_damage": {{
    "detected": true/false,
    "indicators": ["rust", "old paint repair", "unrelated damage", etc],
    "description": "details of pre-existing damage",
    "confidence": 0-100
  }},
  "contextual_analysis": {{
    "location_type": "STREET | PARKING_LOT | HIGHWAY | RESIDENTIAL | UNKNOWN",
    "weather_conditions": "description or UNKNOWN",
    "lighting_quality": "GOOD | FAIR | POOR",
    "photo_quality": "HIGH | MEDIUM | LOW",
    "consistent_with_narrative": true/false
  }},
  "cross_verification": {{
    "narrative_match": true/false,
    "policy_match": true/false,
    "timeline_consistent": true/false,
    "discrepancies": ["list any inconsistencies"]
  }},
  "risk_flags": [
    "list any applicable risk flags from Phase 7"
  ],
  "final_assessment": {{
    "overall_confidence_score": 0-100,
    "recommendation": "APPROVE | REVIEW | REJECT",
    "decision_reasoning": "detailed explanation of recommendation",
    "human_review_priority": "LOW | MEDIUM | HIGH | CRITICAL",
    "fraud_probability": "LOW | MEDIUM | HIGH",
    "recommended_actions": ["list next steps"]
  }}
}}

CRITICAL RULES:
- Respond with ONLY valid JSON
- Use null for unknown values
- Be specific and evidence-based
- Conservative scoring - flag for review if uncertain
- All confidence scores calibrated: 90%+ only when certainty is high"""
    
    return prompt


def analyze_damage(
    image_paths: List[str], 
    description: str = "",
    yolo_context: Dict[str, Any] = None,
    policy_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Perform comprehensive forensic damage analysis using Groq.
    
    Args:
        image_paths: List of image file paths
        description: User's claim description
        yolo_context: YOLOv8 detection results (optional)
        policy_data: Policy/vehicle information (optional)
        
    Returns:
        dict with comprehensive forensic analysis
    """
    if not groq_client:
        init_groq()
    
    if not groq_client:
        return {
            "error": "Groq client not initialized",
            "success": False
        }
    
    # Build comprehensive prompt
    prompt = build_comprehensive_prompt(description, yolo_context, policy_data)
    
    # Prepare images for API
    image_contents = []
    for path in image_paths[:3]:  # Limit to 3 images
        if not os.path.exists(path):
            continue
        
        # Encode image
        base64_image = encode_image_base64(path)
        if base64_image:
            image_contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
    
    if not image_contents:
        return {
            "error": "No valid images provided",
            "success": False
        }
    
    # Build message with images and prompt
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            *image_contents
        ]
    }]
    
    try:
        # Call Groq API with vision model
        response = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,  # llama-4-scout-17b-16e-instruct
            messages=messages,
            temperature=0.1,  # Low temperature for consistency
            max_tokens=4096,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        # Extract response
        response_text = response.choices[0].message.content
        
        # Parse JSON
        try:
            analysis = json.loads(response_text)
            analysis["success"] = True
            analysis["provider"] = "groq"
            analysis["model"] = settings.GROQ_MODEL
            
            # Extract simplified fields for backward compatibility
            analysis["damage_type"] = extract_damage_type(analysis)
            analysis["severity"] = extract_severity(analysis)
            analysis["affected_parts"] = extract_affected_parts(analysis)
            analysis["recommendation"] = extract_recommendation(analysis)
            analysis["reasoning"] = extract_reasoning(analysis)
            analysis["cost_min"] = extract_cost_min(analysis)
            analysis["cost_max"] = extract_cost_max(analysis)
            analysis["risk_flags"] = analysis.get("risk_flags", [])
            analysis["confidence"] = analysis.get("final_assessment", {}).get("overall_confidence_score", 0)
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse Groq JSON response: {e}")
            print(f"Response was: {response_text[:500]}")
            return {
                "error": "Invalid JSON response from Groq",
                "raw_response": response_text,
                "success": False
            }
    
    except Exception as e:
        print(f"[ERROR] Groq API call failed: {e}")
        return {
            "error": str(e),
            "success": False
        }


def extract_damage_type(analysis: Dict) -> str:
    """Extract primary damage type from comprehensive analysis."""
    damage_assessment = analysis.get("damage_assessment", {})
    damaged_panels = damage_assessment.get("damaged_panels", [])
    
    if not damaged_panels:
        return "none"
    
    # Get most severe damage type
    damage_types = [panel.get("damage_type", "other") for panel in damaged_panels]
    return damage_types[0].lower() if damage_types else "other"


def extract_severity(analysis: Dict) -> str:
    """Extract overall severity."""
    damage_assessment = analysis.get("damage_assessment", {})
    severity = damage_assessment.get("overall_severity", "none")
    return severity.lower()


def extract_affected_parts(analysis: Dict) -> List[str]:
    """Extract list of affected parts."""
    damage_assessment = analysis.get("damage_assessment", {})
    damaged_panels = damage_assessment.get("damaged_panels", [])
    return [panel.get("panel_name", "unknown").lower() for panel in damaged_panels]


def extract_recommendation(analysis: Dict) -> str:
    """Extract final recommendation."""
    final_assessment = analysis.get("final_assessment", {})
    recommendation = final_assessment.get("recommendation", "review")
    return recommendation.lower()


def extract_reasoning(analysis: Dict) -> str:
    """Extract decision reasoning."""
    final_assessment = analysis.get("final_assessment", {})
    return final_assessment.get("decision_reasoning", "No reasoning provided")


def extract_cost_min(analysis: Dict) -> int:
    """Extract minimum cost estimate."""
    damage_assessment = analysis.get("damage_assessment", {})
    cost_data = damage_assessment.get("estimated_repair_cost", {})
    return cost_data.get("min_usd", 0)


def extract_cost_max(analysis: Dict) -> int:
    """Extract maximum cost estimate."""
    damage_assessment = analysis.get("damage_assessment", {})
    cost_data = damage_assessment.get("estimated_repair_cost", {})
    return cost_data.get("max_usd", 0)


# Initialize on module load
init_groq()
