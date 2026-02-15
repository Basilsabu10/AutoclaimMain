"""
Test script to verify YOLOv8 + Groq implementation.
Run this to check if everything is working correctly.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("AutoClaim YOLOv8 + Groq Test")
print("=" * 60)

# Test 1: Check YOLOv8 availability
print("\n[Test 1] Checking YOLOv8 availability...")
try:
    from app.services.yolov8_damage_service import (
        YOLO_AVAILABLE,
        check_gpu_available,
        init_yolo_model,
        get_model_info
    )
    
    print(f"✅ YOLOv8 available: {YOLO_AVAILABLE}")
    
    if YOLO_AVAILABLE:
        # Check GPU
        gpu_info = check_gpu_available()
        print(f"   GPU Status: {gpu_info}")
        
        # Initialize model
        print("\n[Test 2] Initializing YOLOv8 model...")
        success = init_yolo_model()
        print(f"   Model initialized: {success}")
        
        if success:
            info = get_model_info()
            print(f"   Model info: {info}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check Groq availability
print("\n[Test 3] Checking Groq availability...")
try:
    from app.services.groq_service import GROQ_AVAILABLE, init_groq
    print(f"✅ Groq available: {GROQ_AVAILABLE}")
    
    if GROQ_AVAILABLE:
        success = init_groq()
        print(f"   Groq initialized: {success}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Check Gemini removal
print("\n[Test 4] Verifying Gemini removal...")
try:
    from app.services import gemini_service
    print("❌ WARNING: Gemini service still exists!")
except ImportError:
    print("✅ Gemini service successfully removed")

# Test 4: Check AI orchestrator
print("\n[Test 5] Checking AI orchestrator...")
try:
    from app.services import ai_orchestrator
    status = ai_orchestrator.initialize_services()
    print(f"✅ AI Services status: {status}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
