#!/usr/bin/env python3
"""
Validation script for Hazm Tuwaiq Backend
Tests critical endpoints to ensure deployment is working.
"""
import sys
import requests
import time


def main():
    BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    
    print(f"🧪 Testing backend at: {BASE}")
    print("=" * 60)
    
    def check(path, method="GET", expected_status=200, json_required=True):
        url = BASE + path
        print(f"\n📍 {method} {path}")
        
        try:
            if method == "GET":
                r = requests.get(url, timeout=20)
            else:
                r = requests.request(method, url, timeout=20)
            
            print(f"   Status: {r.status_code}")
            
            # Check status
            if r.status_code != expected_status:
                print(f"   ❌ Expected {expected_status}, got {r.status_code}")
                print(f"   Response: {r.text[:200]}")
                return False
            
            # Check JSON if required
            if json_required:
                try:
                    data = r.json()
                    print(f"   ✅ Valid JSON response")
                    print(f"   Data: {data}")
                except Exception as e:
                    print(f"   ❌ Invalid JSON: {e}")
                    print(f"   Raw: {r.text[:200]}")
                    return False
            
            return True
            
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout after 20s")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    # Run tests
    results = []
    
    # Test 1: Health endpoint
    results.append(("Health Check", check("/health")))
    
    # Test 2: Root endpoint
    results.append(("Root Endpoint", check("/")))
    
    # Test 3: Docs (Swagger UI)
    results.append(("API Docs", check("/docs", json_required=False)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Backend is healthy.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

    
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
