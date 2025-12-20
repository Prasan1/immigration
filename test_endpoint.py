#!/usr/bin/env python3
"""
Quick test to verify the form-guide endpoint is properly configured
"""

import requests
import sys

def test_endpoint():
    """Test the form-guide API endpoint"""
    base_url = "http://localhost:5000"

    print("Testing form-guide endpoint...")
    print("=" * 60)

    # Test with Form I-130 (should have guide)
    print("\n1. Testing Form ID 1 (I-130 - should have guide):")
    try:
        response = requests.get(f"{base_url}/api/form-guide/1", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Guide available: {data.get('available', False)}")
            if data.get('available'):
                print(f"   ✓ Form: {data.get('form_title', 'Unknown')}")
                print(f"   ✓ Has filling steps: {len(data.get('guide', {}).get('filling_steps', []))} steps")
        elif response.status_code == 401:
            print(f"   ✗ ERROR: Authentication required!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ ERROR: Could not connect to Flask app!")
        print("   Make sure the Flask app is running on localhost:5000")
        sys.exit(1)
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    # Test with a form that doesn't have a guide
    print("\n2. Testing Form ID 5 (should not have guide):")
    try:
        response = requests.get(f"{base_url}/api/form-guide/5", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Guide available: {data.get('available', False)}")
            print(f"   ✓ Message: {data.get('message', 'N/A')}")
        elif response.status_code == 401:
            print(f"   ✗ ERROR: Authentication required!")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    print("\n" + "=" * 60)
    print("\nIf you see authentication errors above, the endpoint has")
    print("the @login_required decorator which needs to be removed.")
    print("\nExpected behavior:")
    print("  - Both tests should return status 200")
    print("  - No authentication should be required")

if __name__ == "__main__":
    test_endpoint()
