"""
OCR Service for Number Plate Extraction.
Uses EasyOCR to extract vehicle registration numbers.
"""

from typing import Dict, Any

# Try to import EasyOCR
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: EasyOCR not installed")

# OCR Reader instance
ocr_reader = None


def init_ocr():
    """Initialize EasyOCR reader (downloads model on first run)."""
    global ocr_reader
    if OCR_AVAILABLE and ocr_reader is None:
        try:
            print("Initializing EasyOCR (may download model on first run)...")
            ocr_reader = easyocr.Reader(['en'], gpu=False)
            print("[OK] EasyOCR initialized")
        except Exception as e:
            print(f"[ERROR] EasyOCR init failed: {e}")


def extract_number_plate(image_path: str) -> Dict[str, Any]:
    """
    Extract vehicle number plate text from an image.
    
    Args:
        image_path: Path to front view image of vehicle
        
    Returns:
        dict with keys: plate_text, confidence
    """
    init_ocr()
    
    result = {
        "plate_text": None,
        "confidence": None
    }
    
    if not OCR_AVAILABLE or ocr_reader is None:
        return result
    
    try:
        detections = ocr_reader.readtext(image_path)
        
        if not detections:
            return result
        
        best_match = None
        best_confidence = 0
        
        for (bbox, text, confidence) in detections:
            # Clean text - remove spaces, keep alphanumeric
            clean_text = ''.join(c for c in text if c.isalnum()).upper()
            
            # Number plates: 4-15 chars, mix of letters and numbers
            if 4 <= len(clean_text) <= 15 and confidence > best_confidence:
                has_letters = any(c.isalpha() for c in clean_text)
                has_numbers = any(c.isdigit() for c in clean_text)
                
                if has_letters and has_numbers:
                    best_match = clean_text
                    best_confidence = confidence
        
        if best_match:
            result["plate_text"] = best_match
            result["confidence"] = round(best_confidence, 3)
            
    except Exception as e:
        print(f"OCR failed for {image_path}: {e}")
    
    return result
