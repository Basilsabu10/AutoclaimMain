"""
Optimized Groq Vision Service - Pure Data Extraction
Fast, low-cost, deterministic fact extraction for fraud detection.
AI extracts facts → Python code makes decisions.
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
    """Encode image to base64 with optimal compression."""
    try:
        from PIL import Image
        import io
        
        img = Image.open(image_path)
        
        # Convert to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Resize for speed (1280x720 is enough for fact extraction)
        max_size = (1280, 720)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Compress to JPEG quality 80 (good enough for extraction)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=80, optimize=True)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')
        
    except Exception as e:
        print(f"[ERROR] Failed to encode image: {e}")
        return None


def build_extraction_prompt(description: str, policy_data: Optional[Dict] = None) -> str:
    """
    Lean prompt for pure data extraction.
    No fluff, no judgment, just facts.
    """
    
    policy_info = ""
    if policy_data:
        policy_info = f"\nPolicy: {policy_data.get('vehicle_make')} {policy_data.get('vehicle_model')} {policy_data.get('vehicle_year')}, Color: {policy_data.get('vehicle_color')}, Plate: {policy_data.get('vehicle_registration')}"
    
    prompt = f"""You are an AI vision system. Your task is to extract ONLY factual observations from the provided image. 
Do not infer, speculate, or explain. 
Return data strictly in the JSON schema below. 
If a field cannot be determined, return null or false as appropriate. 
Do not add extra fields, comments, or text outside the JSON.


Claim: "{description}"{policy_info}

Return ONLY this JSON (no markdown, no explanation):

{{
  "identity": {{
    "detected_objects": ["car", "damage_area"],
    "vehicle_make": "detected make or null",
    "vehicle_model": "detected model or null",
    "vehicle_year": "YYYY or null",
    "vehicle_color": "primary color or null",
    "license_plate_text": "exact plate text or null",
    "license_plate_visible": true/false,
    "license_plate_obscured": true/false,
  }},
  "damage": {{
    "damage_detected": true/false,
    "damage_type": "dent | scratch | crack | shatter | crush | tear | missing | none",
    ""severity_score": 0.00-1.00,
    "damaged_panels": ["front_bumper", "hood", "door_fl", "fender_fr"],
    "impact_point": "front_center | front_left | front_right | side_left | side_right | rear_center | rear_left | rear_right | multiple | none",
    "paint_damage": true/false,
    "glass_damage": true/false,
    "is_rust_present": true/false,
    "rust_locations": [],
    "is_dirt_in_damage": true/false,
    "is_paint_faded_around_damage": true/false,
    "airbags_deployed": true/false,
    "fluid_leaks_visible": true/false,
    "parts_missing": true/false,
    "estimated_cost_range_INR": {{"min": 0, "max": 0}}
  }},
  "forensics": {{
    "is_screen_recapture": true/false,
    "has_ui_elements": true/false,
    "has_watermarks": true/false,
    "image_quality": "high | medium | low",
    "is_blurry": true/false,
    "lighting_quality": "good | poor",
    "multiple_light_sources": true/false,
    "shadows_inconsistent": true/false
  }},
  "scene": {{
    "location_type": "street | parking_lot | garage | highway | residential | unknown",
    "time_of_day": "day | night | dusk | unknown",
    "weather_visible": "clear | rain | snow | fog | unknown",
    "debris_visible": true/false,
    "other_vehicles_visible": true/false,
    "is_moving_traffic": true/false
  }}
}}

RITICAL RULES:
- Respond with ONLY valid JSON
- Use null for unknown values
- Be specific and evidence-based
- All confidence scores calibrated: 90%+ only when certainty is high"""
    
    return prompt


def extract_vehicle_data(
    image_paths: List[str], 
    description: str = "",
    policy_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Fast data extraction from vehicle damage images.
    Returns facts only - no decisions.
    """
    if not groq_client:
        init_groq()
    
    if not groq_client:
        return {
            "error": "Groq client not initialized",
            "success": False
        }
    
    # Build lean prompt
    prompt = build_extraction_prompt(description, policy_data)
    
    # Prepare images (limit to 2 for speed)
    image_contents = []
    for path in image_paths[:2]:
        if not os.path.exists(path):
            continue
        
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
    
    # Build message
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            *image_contents
        ]
    }]
    
    try:
        print(f"[INFO] Extracting data with Groq ({len(image_contents)} images)...")
        
        # Call Groq API with smaller, faster model if available
        # Try llama-3.2-11b-vision-preview first, fallback to configured model
        model = "llama-3.2-11b-vision-preview"  # Smaller, faster
        
        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,  # Zero temperature for deterministic facts
            max_tokens=1500,   # Much less than before
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        
        # Parse JSON
        try:
            data = json.loads(response_text)
            data["success"] = True
            data["provider"] = "groq"
            data["model"] = model
            
            print(f"[OK] Data extracted successfully")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}")
            print(f"Response: {response_text[:500]}")
            return {
                "error": "Invalid JSON response",
                "raw_response": response_text,
                "success": False
            }
    
    except Exception as e:
        print(f"[ERROR] Groq API call failed: {e}")
        # Fallback to configured model
        if "llama-3.2-11b-vision-preview" in str(e):
            print("[INFO] Falling back to configured model...")
            try:
                response = groq_client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)
                data["success"] = True
                data["provider"] = "groq"
                data["model"] = settings.GROQ_MODEL
                return data
            except Exception as e2:
                print(f"[ERROR] Fallback also failed: {e2}")
                return {"error": str(e2), "success": False}
        
        return {
            "error": str(e),
            "success": False
        }


# Alias for backward compatibility
analyze_damage = extract_vehicle_data

# Initialize on module load
init_groq()