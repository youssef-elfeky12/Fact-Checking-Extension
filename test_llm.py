"""
Test the Tavily AI fact checker
"""
import sys
sys.path.insert(0, 'backend')

from llm_verifier import LLMVerifier

def test_claim(claim: str):
    print("=" * 80)
    print(f"CLAIM: {claim}")
    print("=" * 80)
    
    # Tavily searches and verifies
    verifier = LLMVerifier()
    result = verifier.verify_claim(claim)
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']:.0%}")
    
    print(f"\nSources:")
    for i, source in enumerate(result['sources'], 1):
        print(f"\n{i}. {source['title']}")
        print(f"   {source['url']}")
        print(f"   Reliability: {source['reliability_score']}/100")
    
    print(f"\nReasoning:\n{result['reasoning']}")


if __name__ == "__main__":
    test_claims = [
        "The Great Wall of China is visible from the Moon with the naked eye",
        "The Eiffel Tower can grow by up to 15 centimeters during summer",
        "Water boils at 100 degrees Celsius at sea level"
    ]
    
    for claim in test_claims:
        try:
            test_claim(claim)
            print("\n\n")
        except Exception as e:
            print(f"❌ Error: {e}\n\n")


