#!/usr/bin/env python3
"""
Test cv2 import to verify OpenCV is working correctly
"""

import sys

def test_cv2_import():
    """Test basic cv2 import"""
    print("Testing cv2 import...")
    try:
        import cv2
        print(f"✅ cv2 imported successfully!")
        print(f"   Version: {cv2.__version__}")
        print(f"   Build info: {cv2.getBuildInformation()[:200]}...")
        return True
    except ImportError as e:
        print(f"❌ Failed to import cv2: {e}")
        return False
    except Exception as e:
        print(f"⚠️  cv2 imported but error getting info: {e}")
        return True

def test_lazy_imports():
    """Test lazy imports from our modules"""
    print("\nTesting lazy imports from modules...")
    
    modules_to_test = [
        'backend.cctv.rtsp_handler',
        'backend.ai_core.yolo_engine',
        'backend.ai_core.pose_estimation',
        'backend.ai_core.fatigue_detection',
        'backend.cctv.frame_processor',
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported without crash")
        except Exception as e:
            print(f"❌ {module_name} failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("OpenCV Import Test")
    print("=" * 60)
    
    cv2_ok = test_cv2_import()
    lazy_ok = test_lazy_imports()
    
    print("\n" + "=" * 60)
    if cv2_ok and lazy_ok:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
