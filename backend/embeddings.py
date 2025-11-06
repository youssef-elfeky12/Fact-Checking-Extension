"""
Embedding and semantic search utilities using sentence-transformers and FAISS.
"""
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple


class EmbeddingSearchEngine:
    """Manages document embeddings and FAISS-based semantic search."""
    
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Sentence-transformers model name.
                       Default: all-mpnet-base-v2 (best quality)
                       Fallback: all-MiniLM-L6-v2 (faster, lower memory)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def add_documents(self, documents: List[dict]):
        """
        Add documents to the search index.
        
        Args:
            documents: List of dicts with keys: 'text', 'source', 'url'
        """
        if not documents:
            print("Warning: No documents to add")
            return
        
        print(f"Adding {len(documents)} documents to index...")
        self.documents.extend(documents)
        
        # Extract text for embedding
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create or update FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(embeddings)
        print(f"Index now contains {self.index.ntotal} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
        
        Returns:
            List of (document, distance) tuples
        """
        if self.index is None or self.index.ntotal == 0:
            print("Warning: Index is empty")
            return []
        
        # Embed query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Return documents with distances
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        
        return results
    
    def save_index(self, directory: str):
        """Save FAISS index and documents to disk."""
        os.makedirs(directory, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(directory, "faiss.index")
        faiss.write_index(self.index, index_path)
        
        # Save documents
        docs_path = os.path.join(directory, "documents.pkl")
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"Index saved to {directory}")
    
    def load_index(self, directory: str):
        """Load FAISS index and documents from disk."""
        index_path = os.path.join(directory, "faiss.index")
        docs_path = os.path.join(directory, "documents.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            raise FileNotFoundError(f"Index not found in {directory}")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load documents
        with open(docs_path, 'rb') as f:
            self.documents = pickle.load(f)
        
        print(f"Loaded index with {self.index.ntotal} documents from {directory}")


def extract_snippet(text: str, max_length: int = 200) -> str:
    """Extract a snippet from text, trying to get complete sentences."""
    if len(text) <= max_length:
        return text
    
    # Try to cut at sentence boundary
    snippet = text[:max_length]
    last_period = snippet.rfind('.')
    last_question = snippet.rfind('?')
    last_exclamation = snippet.rfind('!')
    
    boundary = max(last_period, last_question, last_exclamation)
    
    if boundary > max_length * 0.5:  # If we found a sentence end in the latter half
        return text[:boundary + 1]
    else:
        return snippet + "..."
