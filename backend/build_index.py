"""
Build FAISS index from seed data.
Run this script to create or rebuild the search index.
"""
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from embeddings import EmbeddingSearchEngine


def build_index():
    """Build FAISS index from seed data."""
    # Paths
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'seed_data.json')
    index_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'index')
    
    # Load seed data
    print(f"Loading seed data from {data_file}...")
    with open(data_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Loaded {len(documents)} documents")
    
    # Initialize search engine
    # Use all-mpnet-base-v2 for best quality
    # Alternative: all-MiniLM-L6-v2 for lower memory/faster inference
    search_engine = EmbeddingSearchEngine(model_name="all-mpnet-base-v2")
    
    # Add documents to index
    search_engine.add_documents(documents)
    
    # Save index
    search_engine.save_index(index_dir)
    
    print("\n✓ Index built successfully!")
    print(f"  Total documents: {len(documents)}")
    print(f"  Index saved to: {index_dir}")
    
    # Test search
    print("\n--- Testing search ---")
    test_query = "Is the Earth round?"
    print(f"Query: {test_query}")
    results = search_engine.search(test_query, top_k=3)
    
    for i, (doc, distance) in enumerate(results, 1):
        print(f"\n{i}. Distance: {distance:.4f}")
        print(f"   Source: {doc['source']}")
        print(f"   URL: {doc['url']}")
        print(f"   Text: {doc['text'][:100]}...")


if __name__ == "__main__":
    build_index()
