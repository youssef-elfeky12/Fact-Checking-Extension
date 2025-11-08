"""
Simple test for keyword extraction and relevance checking
"""
import sys
sys.path.insert(0, 'backend')

from web_search import WebSearchEngine

def test_keywords():
    print("Testing keyword extraction:")
    print("=" * 80)
    
    engine = WebSearchEngine(max_results=10)
    
    test_queries = [
        "The Great Wall of China is visible from the Moon",
        "The Eiffel Tower grows taller in summer",
        "Climate change causes sea level rise"
    ]
    
    for query in test_queries:
        keywords = engine._extract_keywords(query)
        print(f"\nQuery: {query}")
        print(f"Keywords: {keywords}")
    
    print("\n" + "=" * 80)
    print("Testing relevance check:")
    print("=" * 80)
    
    # Test relevance with sample texts
    keywords = ['great wall of china', 'great wall', 'visible', 'moon']
    
    test_cases = [
        ("The Great Wall of China from space and moon visibility", True),
        ("Great Barrier Reef coral decline", False),
        ("Gmail help for signing up", False),
        ("Astronauts discuss what can be seen from the Moon, including the Great Wall", True),
        ("World Economic Forum news about climate change", False),
        ("The wall is great but you can't see it from the moon", True)
    ]
    
    for text, expected in test_cases:
        result = engine._is_relevant(text, keywords)
        status = "✅" if result == expected else "❌"
        print(f"{status} Expected: {expected}, Got: {result}")
        print(f"   Text: {text}")
        
        # Show which keywords matched
        matches = [kw for kw in keywords if kw in text.lower()]
        print(f"   Matches: {matches}\n")

if __name__ == "__main__":
    test_keywords()
