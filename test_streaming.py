# ══════════════════════════════════════════════════════════════
# TEST SCRIPT - Streaming Service
# ══════════════════════════════════════════════════════════════
#
# Tests the Streaming Service API endpoints.
# Requires: RabbitMQ and PostgreSQL running
#
# Run: python test_streaming.py
#
# ══════════════════════════════════════════════════════════════

import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 50)
    print("TEST: Health Check")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to streaming service")
        print("   Make sure to start it first: python services/streaming/main.py")
        return False


def test_root():
    """Test root endpoint."""
    print("\n" + "=" * 50)
    print("TEST: Root Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_videos():
    """Test videos endpoint."""
    print("\n" + "=" * 50)
    print("TEST: Videos Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/videos", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Video Count: {data.get('count', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_violations():
    """Test violations endpoint."""
    print("\n" + "=" * 50)
    print("TEST: Violations Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/violations", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Violation Count: {data.get('count', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_violations_current():
    """Test current violations endpoint."""
    print("\n" + "=" * 50)
    print("TEST: Current Violations Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/violations/current", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_roi():
    """Test ROI endpoint."""
    print("\n" + "=" * 50)
    print("TEST: ROI Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/roi", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"ROI Count: {data.get('count', 0)}")
        if data.get('rois'):
            print(f"First ROI: {data['rois'][0]}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_docs():
    """Test OpenAPI docs endpoint."""
    print("\n" + "=" * 50)
    print("TEST: API Docs")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Docs available at: {BASE_URL}/docs")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STREAMING SERVICE - API TESTS")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Videos", test_videos),
        ("Violations", test_violations),
        ("Current Violations", test_violations_current),
        ("ROI", test_roi),
        ("API Docs", test_docs),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"  Total: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
