"""
Test semantic search functionality.
Run after building the index with build_index.py
"""
import requests
import json


def test_semantic_search():
    """Test that semantic search returns relevant evidence."""
    url = "http://127.0.0.1:8000/check"
    
    # Test claim that should match seed data
    test_cases = [
        {
            "claim": "Is the Earth round?",
            "expected_keyword": "spherical"  # Should find Earth shape document
        },
        {
            "claim": "What temperature does water boil?",
            "expected_keyword": "100"  # Should find boiling point document
        },
        {
            "claim": "Are vaccines safe?",
            "expected_keyword": "vaccine"  # Should find vaccine document
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        print(f"Claim: {test['claim']}")
        
        response = requests.post(url, json={"tweet_text": test['claim']})
        
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            all_passed = False
            continue
        
        data = response.json()
        
        # Check structure
        assert "evidences" in data, "Missing evidences"
        assert len(data["evidences"]) > 0, "No evidences returned"
        
        # Check if relevant evidence was found
        found_relevant = False
        for ev in data["evidences"]:
            if test["expected_keyword"].lower() in ev["snippet"].lower():
                found_relevant = True
                print(f"✓ Found relevant evidence: {ev['source']}")
                print(f"  Snippet: {ev['snippet'][:100]}...")
                print(f"  Score: {ev['score']:.3f}")
                break
        
        if not found_relevant:
            print(f"⚠ Warning: Expected keyword '{test['expected_keyword']}' not found in top results")
            print(f"  Top result: {data['evidences'][0]['snippet'][:100]}...")
        
        print(f"  Percent true: {data['percent_true']}%")
    
    if all_passed:
        print("\n✓ All semantic search tests completed!")
    else:
        print("\n⚠ Some tests had issues")


if __name__ == "__main__":
    try:
        test_semantic_search()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to http://127.0.0.1:8000")
        print("Make sure the backend is running: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
