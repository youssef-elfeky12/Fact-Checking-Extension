from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from embeddings import EmbeddingSearchEngine, extract_snippet
from verifier import get_verifier

app = FastAPI(title="Fact Checker API", version="0.3.0")

# CORS configuration for Firefox extension and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine and verifier (load on startup)
search_engine = None
verifier = None
INDEX_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'index')


@app.on_event("startup")
async def startup_event():
    """Load FAISS index and NLI model on startup."""
    global search_engine, verifier
    
    # Load search engine
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
    
    # Load NLI verifier
    try:
        print("\n--- Loading NLI Verifier ---")
        verifier = get_verifier(model_name="roberta-large-mnli")
        print("✓ NLI verifier ready\n")
    except Exception as e:
        print(f"❌ Error loading NLI verifier: {e}")
        verifier = None


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
    return {
        "message": "Fact Checker API is running",
        "version": "0.3.0",
        "search_ready": search_engine is not None and search_engine.index is not None,
        "verifier_ready": verifier is not None
    }


@app.post("/check", response_model=CheckResponse)
def check_claim(req: CheckRequest):
    """
    Check a claim and return percent_true estimate with evidence.
    Uses semantic search + NLI verification.
    """
    if search_engine is None or search_engine.index is None:
        raise HTTPException(
            status_code=503,
            detail="Search index not available. Please run build_index.py first."
        )
    
    if verifier is None:
        raise HTTPException(
            status_code=503,
            detail="NLI verifier not available. Please check server logs."
        )
    
    # Extract claim text
    claim = req.tweet_text.strip()
    
    if not claim:
        raise HTTPException(status_code=400, detail="tweet_text cannot be empty")
    
    # Step 1: Search for relevant evidence (top 5)
    print(f"\n--- Checking claim: {claim[:100]}... ---")
    results = search_engine.search(claim, top_k=5)
    
    if not results:
        return CheckResponse(
            percent_true=50.0,
            evidences=[],
            explanation="No relevant evidence found in the database."
        )
    
    # Step 2: Prepare documents for NLI verification
    evidence_docs = []
    for doc, distance in results:
        evidence_docs.append({
            'text': doc['text'],
            'source': doc['source'],
            'distance': distance
        })
    
    # Step 3: Verify claim with NLI
    verification_result = verifier.verify_claim(claim, evidence_docs)
    
    # Step 4: Format response
    evidences = [
        Evidence(
            source=e['source'],
            snippet=e['snippet'],
            stance=e['stance'],
            score=e['score']
        )
        for e in verification_result['evidences']
    ]
    
    print(f"Truth score: {verification_result['truth_score']}%")
    print(f"NLI scores: {verification_result['avg_nli_scores']}")
    
    return CheckResponse(
        percent_true=verification_result['truth_score'],
        evidences=evidences,
        explanation=verification_result['explanation']
    )
