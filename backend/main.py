from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from embeddings import EmbeddingSearchEngine, extract_snippet

app = FastAPI(title="Fact Checker API", version="0.2.0")

# CORS configuration for Firefox extension and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine (load on startup)
search_engine = None
INDEX_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'index')


@app.on_event("startup")
async def startup_event():
    """Load FAISS index on startup."""
    global search_engine
    try:
        search_engine = EmbeddingSearchEngine(model_name="all-mpnet-base-v2")
        if os.path.exists(INDEX_DIR):
            search_engine.load_index(INDEX_DIR)
            print(f"✓ Loaded search index with {search_engine.index.ntotal} documents")
        else:
            print("⚠ Warning: No index found. Run build_index.py to create one.")
    except Exception as e:
        print(f"❌ Error loading search engine: {e}")
        search_engine = None


class CheckRequest(BaseModel):
    tweet_text: str


class Evidence(BaseModel):
    source: str
    snippet: str
    stance: str  # "support" | "contradict" | "neutral"
    score: float


class CheckResponse(BaseModel):
    percent_true: float
    evidences: list[Evidence]
    explanation: str


@app.get("/")
def root():
    return {"message": "Fact Checker API is running", "version": "0.1.0"}


@app.post("/check", response_model=CheckResponse)
def check_claim(req: CheckRequest):
    """
    Check a claim and return percent_true estimate with evidence.
    Uses semantic search to find relevant evidence.
    """
    if search_engine is None or search_engine.index is None:
        raise HTTPException(
            status_code=503,
            detail="Search index not available. Please run build_index.py first."
        )
    
    # Extract claim text
    claim = req.tweet_text.strip()
    
    if not claim:
        raise HTTPException(status_code=400, detail="tweet_text cannot be empty")
    
    # Search for relevant evidence (top 5)
    results = search_engine.search(claim, top_k=5)
    
    if not results:
        return CheckResponse(
            percent_true=50.0,
            evidences=[],
            explanation="No relevant evidence found in the database."
        )
    
    # Build evidence list with snippets
    evidences = []
    for doc, distance in results:
        snippet = extract_snippet(doc['text'], max_length=200)
        # Convert distance to a similarity score (lower distance = higher similarity)
        # Simple inverse mapping for now
        score = max(0.0, 1.0 - (distance / 10.0))
        
        evidences.append(Evidence(
            source=doc['source'],
            snippet=snippet,
            stance="neutral",  # Will be replaced with NLI in Step 3
            score=score
        ))
    
    # Simple placeholder aggregation (will be replaced with NLI in Step 3)
    avg_score = sum(e.score for e in evidences) / len(evidences)
    percent_true = avg_score * 100
    
    return CheckResponse(
        percent_true=round(percent_true, 1),
        evidences=evidences,
        explanation=f"Found {len(evidences)} relevant evidence sources. NLI verification pending (Step 3)."
    )
