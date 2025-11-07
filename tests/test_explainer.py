"""
Test the optional LLM explainer (Mistral 7B).
Run this only if you have enabled the explainer with ENABLE_LLM_EXPLAINER=true.
"""
import sys
import os

# Set environment variable to enable explainer for testing
os.environ["ENABLE_LLM_EXPLAINER"] = "true"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from explainer import get_explainer, is_explainer_enabled


def test_explainer_enabled():
    """Test that explainer can be enabled."""
    print("=== Testing Explainer Enabled Status ===\n")
    
    enabled = is_explainer_enabled()
    print(f"Explainer enabled: {enabled}")
    assert enabled, "Explainer should be enabled when ENABLE_LLM_EXPLAINER=true"
    print("✓ Test passed\n")


def test_load_explainer():
    """Test loading the LLM explainer."""
    print("=== Testing LLM Explainer Loading ===\n")
    print("Note: This will download Mistral 7B (~3.5-4GB) on first run.")
    print("This may take 2-5 minutes...\n")
    
    explainer = get_explainer()
    
    assert explainer is not None, "Explainer should load successfully"
    print("✓ LLM explainer loaded successfully\n")
    
    return explainer


def test_generate_explanation():
    """Test generating an explanation."""
    print("=== Testing Explanation Generation ===\n")
    
    explainer = get_explainer()
    if explainer is None:
        print("⚠ Explainer not loaded, skipping test")
        return
    
    # Test case: True claim with supporting evidence
    claim = "Water boils at 100 degrees Celsius at sea level."
    truth_score = 92.5
    evidences = [
        {
            "source": "https://example.com/chemistry",
            "snippet": "At sea level, water boils at 100°C (212°F) under standard atmospheric pressure.",
            "stance": "support",
            "score": 0.95
        },
        {
            "source": "https://example.com/physics",
            "snippet": "The boiling point of water is 100 degrees Celsius at 1 atmosphere of pressure.",
            "stance": "support",
            "score": 0.90
        }
    ]
    
    print(f"Claim: {claim}")
    print(f"Truth Score: {truth_score}%")
    print(f"Evidence count: {len(evidences)}")
    print("\nGenerating explanation...\n")
    
    explanation = explainer.generate_explanation(
        claim=claim,
        truth_score=truth_score,
        evidences=evidences,
        max_length=100
    )
    
    print(f"Generated Explanation:\n{explanation}\n")
    
    assert len(explanation) > 0, "Explanation should not be empty"
    assert len(explanation) < 1000, "Explanation should be concise"
    
    print("✓ Explanation generated successfully\n")


def test_generate_false_claim_explanation():
    """Test generating explanation for a false claim."""
    print("=== Testing False Claim Explanation ===\n")
    
    explainer = get_explainer()
    if explainer is None:
        print("⚠ Explainer not loaded, skipping test")
        return
    
    # Test case: False claim with contradicting evidence
    claim = "The Earth is flat."
    truth_score = 5.0
    evidences = [
        {
            "source": "https://example.com/astronomy",
            "snippet": "The Earth is an oblate spheroid, approximately spherical in shape.",
            "stance": "contradict",
            "score": 0.95
        },
        {
            "source": "https://example.com/science",
            "snippet": "Scientific evidence overwhelmingly confirms the Earth is round.",
            "stance": "contradict",
            "score": 0.92
        }
    ]
    
    print(f"Claim: {claim}")
    print(f"Truth Score: {truth_score}%")
    print("\nGenerating explanation...\n")
    
    explanation = explainer.generate_explanation(
        claim=claim,
        truth_score=truth_score,
        evidences=evidences,
        max_length=100
    )
    
    print(f"Generated Explanation:\n{explanation}\n")
    
    assert len(explanation) > 0, "Explanation should not be empty"
    print("✓ False claim explanation generated successfully\n")


def test_fallback_explanation():
    """Test fallback explanation when LLM fails."""
    print("=== Testing Fallback Explanation ===\n")
    
    explainer = get_explainer()
    if explainer is None:
        print("⚠ Explainer not loaded, skipping test")
        return
    
    claim = "Test claim"
    truth_score = 50.0
    evidences = [
        {
            "source": "https://example.com",
            "snippet": "Test evidence",
            "stance": "neutral",
            "score": 0.5
        }
    ]
    
    # Test the fallback method directly
    explanation = explainer._fallback_explanation(claim, truth_score, evidences)
    
    print(f"Fallback Explanation:\n{explanation}\n")
    
    assert len(explanation) > 0, "Fallback explanation should not be empty"
    assert "evidence source" in explanation.lower(), "Should mention evidence sources"
    
    print("✓ Fallback explanation test passed\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LLM EXPLAINER TESTS (Step 4)")
    print("="*60 + "\n")
    
    print("⚠ WARNING: This will download Mistral 7B (~3.5-4GB) on first run!")
    print("⚠ Requires: 11GB GPU or will run slowly on CPU\n")
    
    try:
        test_explainer_enabled()
        
        print("Loading LLM (this may take 2-5 minutes)...\n")
        explainer = test_load_explainer()
        
        if explainer:
            test_generate_explanation()
            test_generate_false_claim_explanation()
            test_fallback_explanation()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
