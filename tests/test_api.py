"""
Simple test script for the /check endpoint.
Run with: pytest test_api.py
Or directly: python test_api.py
"""
import requests
import json


def test_check_endpoint():
    """Test the /check endpoint returns expected schema and HTTP 200."""
    url = "http://127.0.0.1:8000/check"
    payload = {"tweet_text": "The Earth is round."}
    
    response = requests.post(url, json=payload)
    
    # Assert HTTP 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Parse JSON
    data = response.json()
    
    # Assert schema
    assert "percent_true" in data, "Missing percent_true"
    assert "evidences" in data, "Missing evidences"
    assert "explanation" in data, "Missing explanation"
    assert isinstance(data["percent_true"], (int, float)), "percent_true must be numeric"
    assert isinstance(data["evidences"], list), "evidences must be a list"
    assert isinstance(data["explanation"], str), "explanation must be a string"
    
    # Check evidence structure
    if len(data["evidences"]) > 0:
        ev = data["evidences"][0]
        assert "source" in ev, "Evidence missing source"
        assert "snippet" in ev, "Evidence missing snippet"
        assert "stance" in ev, "Evidence missing stance"
        assert "score" in ev, "Evidence missing score"
    
    print("✓ All tests passed!")
    print(f"Response: {json.dumps(data, indent=2)}")


if __name__ == "__main__":
    try:
        test_check_endpoint()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to http://127.0.0.1:8000")
        print("Make sure the backend is running: uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
