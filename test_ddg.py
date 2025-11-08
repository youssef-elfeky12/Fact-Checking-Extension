from duckduckgo_search import DDGS
import time

print("Testing DuckDuckGo search with English preference...")

try:
    ddgs = DDGS()
    print("✓ DDGS initialized")
    
    # Test queries
    queries = [
        "The Great Wall of China is visible from the Moon",
        "Eiffel Tower thermal expansion"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        
        # Add English hint
        english_query = f"{query} (in English)"
        print(f"Search: {english_query}")
        
        start = time.time()
        
        results = list(ddgs.text(
            keywords=english_query,
            region='us-en',  # US English region
            safesearch='moderate',
            max_results=10
        ))
        
        elapsed = time.time() - start
        
        print(f"✓ Found {len(results)} results in {elapsed:.2f}s\n")
        
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result.get('title', 'No title')[:60]}")
            print(f"   {result.get('href', 'No URL')[:80]}")
        
        # Small delay between queries to avoid rate limiting
        time.sleep(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
