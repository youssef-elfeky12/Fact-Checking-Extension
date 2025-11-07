"""
Unit tests for NLI verifier module.
Tests the fact verification logic using NLI models.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from verifier import NLIVerifier


def test_nli_scores():
    """Test that NLI scores are computed correctly."""
    verifier = NLIVerifier(model_name="roberta-large-mnli")
    
    # Test with a clear entailment
    premise = "The sky is blue on a clear day."
    hypothesis = "The sky has a blue color."
    
    scores = verifier.compute_nli_scores(premise, hypothesis)
    
    # Check that we get valid probabilities
    assert 'entailment' in scores
    assert 'neutral' in scores
    assert 'contradiction' in scores
    
    # Probabilities should sum to ~1.0
    total = scores['entailment'] + scores['neutral'] + scores['contradiction']
    assert 0.99 <= total <= 1.01, f"Probabilities should sum to 1, got {total}"
    
    # For this example, entailment should be highest
    assert scores['entailment'] > scores['neutral']
    assert scores['entailment'] > scores['contradiction']
    
    print("✓ NLI scores test passed")
    print(f"  Scores: {scores}")


def test_verify_claim_with_support():
    """Test claim verification with supporting evidence."""
    verifier = NLIVerifier(model_name="roberta-large-mnli")
    
    claim = "Water boils at 100 degrees Celsius."
    evidence = [
        {
            "text": "At sea level, water boils at 100°C (212°F).",
            "source": "https://example.com/chemistry"
        },
        {
            "text": "The boiling point of water is 100 degrees Celsius at standard atmospheric pressure.",
            "source": "https://example.com/physics"
        }
    ]
    
    result = verifier.verify_claim(claim, evidence)
    
    # Check result structure
    assert 'truth_score' in result
    assert 'evidences' in result
    assert 'avg_nli_scores' in result
    assert 'explanation' in result
    
    # Check truth score is in valid range
    assert 0 <= result['truth_score'] <= 100
    
    # For supporting evidence, truth score should be high
    assert result['truth_score'] > 50, f"Expected high truth score for supporting evidence, got {result['truth_score']}"
    
    # Check evidence stances
    assert len(result['evidences']) == 2
    support_count = sum(1 for e in result['evidences'] if e['stance'] == 'support')
    assert support_count > 0, "Expected at least one supporting evidence"
    
    print("✓ Verify claim with support test passed")
    print(f"  Truth score: {result['truth_score']}%")
    print(f"  Evidence stances: {[e['stance'] for e in result['evidences']]}")


def test_verify_claim_with_contradiction():
    """Test claim verification with contradicting evidence."""
    verifier = NLIVerifier(model_name="roberta-large-mnli")
    
    claim = "The Earth is flat."
    evidence = [
        {
            "text": "The Earth is a sphere, approximately an oblate spheroid.",
            "source": "https://example.com/astronomy"
        },
        {
            "text": "Scientific evidence overwhelmingly confirms the Earth is round.",
            "source": "https://example.com/science"
        }
    ]
    
    result = verifier.verify_claim(claim, evidence)
    
    # Truth score should be low for contradicting evidence
    assert result['truth_score'] < 50, f"Expected low truth score for contradicting evidence, got {result['truth_score']}"
    
    # Check for contradicting stances
    contradict_count = sum(1 for e in result['evidences'] if e['stance'] == 'contradict')
    assert contradict_count > 0, "Expected at least one contradicting evidence"
    
    print("✓ Verify claim with contradiction test passed")
    print(f"  Truth score: {result['truth_score']}%")
    print(f"  Evidence stances: {[e['stance'] for e in result['evidences']]}")


def test_verify_claim_no_evidence():
    """Test claim verification with no evidence."""
    verifier = NLIVerifier(model_name="roberta-large-mnli")
    
    claim = "Some random claim with no evidence."
    evidence = []
    
    result = verifier.verify_claim(claim, evidence)
    
    # Should return neutral score
    assert result['truth_score'] == 50.0
    assert len(result['evidences']) == 0
    assert "No evidence" in result['explanation']
    
    print("✓ Verify claim with no evidence test passed")


def test_truth_score_formula():
    """Test the truth score calculation formula."""
    verifier = NLIVerifier(model_name="roberta-large-mnli")
    
    # Test case 1: Strong entailment
    nli_scores = {"entailment": 0.9, "neutral": 0.05, "contradiction": 0.05}
    score = verifier._calculate_truth_score(nli_scores)
    assert score > 75, f"Expected high score for strong entailment, got {score}"
    
    # Test case 2: Strong contradiction
    nli_scores = {"entailment": 0.05, "neutral": 0.05, "contradiction": 0.9}
    score = verifier._calculate_truth_score(nli_scores)
    assert score < 25, f"Expected low score for strong contradiction, got {score}"
    
    # Test case 3: Neutral
    nli_scores = {"entailment": 0.33, "neutral": 0.34, "contradiction": 0.33}
    score = verifier._calculate_truth_score(nli_scores)
    assert 40 <= score <= 60, f"Expected moderate score for neutral, got {score}"
    
    # Test case 4: Clamping at 0
    nli_scores = {"entailment": 0.0, "neutral": 0.0, "contradiction": 1.0}
    score = verifier._calculate_truth_score(nli_scores)
    assert score == 0.0, f"Expected 0 for max contradiction, got {score}"
    
    # Test case 5: Clamping at 100
    nli_scores = {"entailment": 1.0, "neutral": 0.0, "contradiction": 0.0}
    score = verifier._calculate_truth_score(nli_scores)
    assert score == 100.0, f"Expected 100 for max entailment, got {score}"
    
    print("✓ Truth score formula test passed")


if __name__ == "__main__":
    print("\n=== Running NLI Verifier Tests ===\n")
    
    try:
        test_nli_scores()
        print()
        
        test_verify_claim_with_support()
        print()
        
        test_verify_claim_with_contradiction()
        print()
        
        test_verify_claim_no_evidence()
        print()
        
        test_truth_score_formula()
        print()
        
        print("=== All tests passed! ✓ ===\n")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
