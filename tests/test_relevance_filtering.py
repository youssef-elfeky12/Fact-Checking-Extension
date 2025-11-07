"""
Quick test to verify the NLI verifier fix.
Tests that relevant evidence is weighted properly.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_water_boiling():
    """Test a clearly true claim about water boiling."""
    print("="*60)
    print("Testing: Water boils at 100 degrees Celsius")
    print("="*60)
    
    claim = "Water boils at 100 degrees Celsius."
    
    response = requests.post(
        f"{BASE_URL}/check",
        json={"tweet_text": claim}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Truth Score: {result['percent_true']}%")
        print(f"\nExplanation: {result['explanation']}")
        print(f"\nEvidence breakdown:")
        
        for i, ev in enumerate(result['evidences'], 1):
            print(f"\n{i}. {ev['source']}")
            print(f"   Stance: {ev['stance']}")
            print(f"   Confidence: {ev['score']:.3f}")
            print(f"   Snippet: {ev['snippet'][:100]}...")
        
        # Check if result makes sense
        if result['percent_true'] >= 70:
            print(f"\n✅ PASS: Truth score is appropriately high ({result['percent_true']}%)")
        else:
            print(f"\n❌ FAIL: Truth score is too low ({result['percent_true']}%) for a true claim")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_false_claim():
    """Test a clearly false claim."""
    print("\n" + "="*60)
    print("Testing: The Earth is flat")
    print("="*60)
    
    claim = "The Earth is flat."
    
    response = requests.post(
        f"{BASE_URL}/check",
        json={"tweet_text": claim}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Truth Score: {result['percent_true']}%")
        print(f"\nExplanation: {result['explanation']}")
        
        # Check if result makes sense
        if result['percent_true'] <= 30:
            print(f"\n✅ PASS: Truth score is appropriately low ({result['percent_true']}%)")
        else:
            print(f"\n❌ FAIL: Truth score is too high ({result['percent_true']}%) for a false claim")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    try:
        test_water_boiling()
        test_false_claim()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Make sure the backend server is running!")
        print("   Run: run_server.bat")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
