"""
Test script to verify relevance filtering works correctly
"""
import sys
sys.path.insert(0, 'backend')

from web_search import WebSearchEngine

def test_great_wall():
    print("=" * 80)
    print("Testing: Great Wall of China visibility from Moon")
    print("=" * 80)
    
    engine = WebSearchEngine(max_results=10)
    results = engine.search("The Great Wall of China is visible from the Moon with the naked eye")
    
    print(f"\n📊 Total results: {len(results)}")
    print("\n📋 All sources:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['source']}")
        print(f"   URL: {result['url']}")
        print(f"   Score: {result['reliability_score']}")
        print(f"   Text: {result['text'][:150]}...")
    
    # Check if results are actually relevant
    relevant_count = 0
    keywords = ['great wall', 'china', 'moon', 'visible', 'space']
    
    print("\n🔍 Relevance check:")
    for i, result in enumerate(results, 1):
        text_lower = result['text'].lower()
        matches = [kw for kw in keywords if kw in text_lower]
        is_relevant = len(matches) >= 2
        relevant_count += is_relevant
        
        status = "✅ RELEVANT" if is_relevant else "❌ IRRELEVANT"
        print(f"  {i}. {status} - Matches: {matches}")
    
    print(f"\n📈 Summary: {relevant_count}/{len(results)} sources are relevant")
    
    return results

if __name__ == "__main__":
    test_great_wall()
