from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from embeddings import EmbeddingSearchEngine, extract_snippet
from verifier import get_verifier
from explainer import get_explainer, is_explainer_enabled

app = FastAPI(title="Fact Checker API", version="0.4.0")

# CORS configuration for Firefox extension and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine, verifier, and optional LLM explainer (load on startup)
search_engine = None
verifier = None
explainer = None
INDEX_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'index')


@app.on_event("startup")
async def startup_event():
    """Load FAISS index, NLI model, and optional LLM explainer on startup."""
    global search_engine, verifier, explainer
    
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
    
    # Load optional LLM explainer (only if enabled)
    if is_explainer_enabled():
        try:
            print("\n--- Loading LLM Explainer (Mistral 7B) ---")
            explainer = get_explainer(model_name="mistralai/Mistral-7B-Instruct-v0.2")
            if explainer:
                print("✓ LLM explainer ready\n")
            else:
                print("⚠ LLM explainer disabled\n")
        except Exception as e:
            print(f"❌ Error loading LLM explainer: {e}")
            explainer = None
    else:
        print("\n⚠ LLM explainer disabled (set ENABLE_LLM_EXPLAINER=true to enable)\n")


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
        "version": "0.4.0",
        "search_ready": search_engine is not None and search_engine.index is not None,
        "verifier_ready": verifier is not None,
        "explainer_ready": explainer is not None
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
    
    # Step 4: Generate enhanced explanation with LLM (if enabled)
    explanation = verification_result['explanation']
    if explainer is not None:
        try:
            print("Generating LLM explanation...")
            llm_explanation = explainer.generate_explanation(
                claim=claim,
                truth_score=verification_result['truth_score'],
                evidences=verification_result['evidences']
            )
            explanation = llm_explanation
            print(f"✓ LLM explanation generated")
        except Exception as e:
            print(f"⚠ LLM explanation failed, using fallback: {e}")
            # Keep the template-based explanation from verifier
    
    # Step 5: Format response
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
        explanation=explanation
    )
