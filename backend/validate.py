#!/usr/bin/env python3
"""
Backend validation script
اختبر endpoints الكشف والدردشة
"""

import requests
import json
import base64
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
API_KEY = ""  # اترك فارغ إذا ما عندك حماية

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def make_request(method, endpoint, data=None):
    """Make HTTP request to backend"""
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=5)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return resp.status_code, resp.json() if resp.text else {}
    except requests.exceptions.ConnectionError:
        log(f"❌ Failed to connect to {url}")
        return None, None
    except Exception as e:
        log(f"❌ Error: {e}")
        return None, None


def test_health():
    """Test /health endpoint"""
    log("Testing /health...")
    code, data = make_request("GET", "/health")
    
    if code == 200:
        log(f"✓ Health check passed: {data.get('status')}")
        return True
    else:
        log(f"✗ Health check failed: {code}")
        return False


def test_detection():
    """Test /detect endpoint"""
    log("\nTesting /detect endpoint...")
    
    # Create a simple 1x1 transparent PNG
    png_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89').decode()
    
    payload = {
        "frame_data": png_data,
        "timestamp": None
    }
    
    code, data = make_request("POST", "/detect", payload)
    
    if code == 200:
        log(f"✓ Detection request successful")
        log(f"  - Detection ID: {data.get('id')}")
        log(f"  - Objects detected: {len(data.get('objects', []))}")
        return True
    else:
        log(f"✗ Detection failed: {code}")
        if data:
            log(f"  Error: {data}")
        return False


def test_chat():
    """Test /chat endpoint"""
    log("\nTesting /chat endpoint...")
    
    payload = {
        "message": "What is the latest detection result?",
        "detection_result": None,
        "session_id": "test_session_001"
    }
    
    code, data = make_request("POST", "/chat", payload)
    
    if code == 200:
        log(f"✓ Chat request successful")
        log(f"  - Message ID: {data.get('id')}")
        log(f"  - Response: {data.get('assistant_response')[:50]}...")
        return True
    else:
        log(f"✗ Chat failed: {code}")
        if data:
            log(f"  Error: {data}")
        return False


def test_chat_with_detection():
    """Test /chat endpoint with detection context"""
    log("\nTesting /chat with detection context...")
    
    # First get last detection
    code, det = make_request("GET", "/detections/last")
    
    if code != 200 or not det:
        log("⚠ No previous detection found, creating one first...")
        test_detection()
        code, det = make_request("GET", "/detections/last")
    
    payload = {
        "message": "Tell me about the detection results",
        "detection_result": det if det else None,
        "session_id": "test_session_001"
    }
    
    code, data = make_request("POST", "/chat", payload)
    
    if code == 200:
        log(f"✓ Chat with detection successful")
        log(f"  - Detection attached: {data.get('detection_attached')}")
        log(f"  - Response: {data.get('assistant_response')[:50]}...")
        return True
    else:
        log(f"✗ Chat with detection failed: {code}")
        return False


def test_chat_history():
    """Test /chat/{session_id} endpoint"""
    log("\nTesting /chat history...")
    
    code, data = make_request("GET", "/chat/test_session_001")
    
    if code == 200:
        log(f"✓ Chat history retrieved: {len(data)} messages")
        return True
    else:
        log(f"✗ Chat history failed: {code}")
        return False


def test_clear_chat():
    """Test clearing chat session"""
    log("\nTesting /chat/{session_id} DELETE...")
    
    code, data = make_request("DELETE", "/chat/test_session_001")
    
    if code == 200:
        log(f"✓ Chat session cleared")
        return True
    else:
        log(f"✗ Clear failed: {code}")
        return False


def main():
    """Run all validation tests"""
    log("=" * 60)
    log("Hazm Tuwaiq Backend Validation")
    log("=" * 60)
    
    results = {
        "health": test_health(),
        "detection": test_detection(),
        "chat": test_chat(),
        "chat_with_detection": test_chat_with_detection(),
        "chat_history": test_chat_history(),
        "clear_chat": test_clear_chat(),
    }
    
    log("\n" + "=" * 60)
    log("Summary")
    log("=" * 60)
    for test, result in results.items():
        status = "✓" if result else "✗"
        log(f"{status} {test}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    log(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        log("\n✓ All tests passed!")
        return 0
    else:
        log(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
