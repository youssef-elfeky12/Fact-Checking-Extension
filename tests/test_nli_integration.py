"""
Quick integration test for Step 3 - NLI Verifier
Tests the /check endpoint with NLI-based verification.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_check_endpoint():
    """Test the /check endpoint with real claims."""
    
    print("=== Testing /check endpoint with NLI ===\n")
    
    # Test claim 1: Likely true
    claim1 = "Water boils at 100 degrees Celsius at sea level."
    print(f"Test 1: {claim1}")
    response = requests.post(
        f"{BASE_URL}/check",
        json={"tweet_text": claim1}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Truth Score: {result['percent_true']}%")
        print(f"  Explanation: {result['explanation']}")
        print(f"  Evidence count: {len(result['evidences'])}")
        if result['evidences']:
            print(f"  Top evidence stance: {result['evidences'][0]['stance']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    print("\n" + "-"*60 + "\n")
    
    # Test claim 2: Likely false
    claim2 = "The Earth is flat and sits on a turtle."
    print(f"Test 2: {claim2}")
    response = requests.post(
        f"{BASE_URL}/check",
        json={"tweet_text": claim2}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Truth Score: {result['percent_true']}%")
        print(f"  Explanation: {result['explanation']}")
        print(f"  Evidence count: {len(result['evidences'])}")
        if result['evidences']:
            print(f"  Top evidence stance: {result['evidences'][0]['stance']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    print("\n" + "-"*60 + "\n")
    
    # Test claim 3: Neutral/ambiguous
    claim3 = "Technology is advancing rapidly."
    print(f"Test 3: {claim3}")
    response = requests.post(
        f"{BASE_URL}/check",
        json={"tweet_text": claim3}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Truth Score: {result['percent_true']}%")
        print(f"  Explanation: {result['explanation']}")
        print(f"  Evidence count: {len(result['evidences'])}")
        if result['evidences']:
            print(f"  Top evidence stance: {result['evidences'][0]['stance']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    print("\n=== Tests Complete ===\n")


def test_health():
    """Test the health endpoint."""
    print("=== Testing Health Endpoint ===\n")
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Message: {result['message']}")
        print(f"  Version: {result['version']}")
        print(f"  Search Ready: {result['search_ready']}")
        print(f"  Verifier Ready: {result['verifier_ready']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    try:
        test_health()
        test_check_endpoint()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Make sure the backend server is running!")
        print("   Run: uvicorn backend.main:app --host 127.0.0.1 --port 8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
