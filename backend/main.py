from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from web_search import get_web_search_engine
from verifier import get_verifier
from explainer import get_explainer, is_explainer_enabled

app = FastAPI(title="Fact Checker API", version="0.5.0")

# CORS configuration for Firefox extension and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize web search engine, verifier, and optional LLM explainer (load on startup)
web_search = None
verifier = None
explainer = None


@app.on_event("startup")
async def startup_event():
    """Load web search engine, NLI model, and optional LLM explainer on startup."""
    global web_search, verifier, explainer
    
    # Initialize web search engine (no pre-loading needed)
    try:
        web_search = get_web_search_engine(max_results=5)
        print("✓ Web search engine ready (DuckDuckGo)\n")
    except Exception as e:
        print(f"❌ Error initializing web search: {e}")
        web_search = None
    
    # Load NLI verifier
    try:
        print("--- Loading NLI Verifier ---")
        verifier = get_verifier(model_name="roberta-large-mnli")
        print("✓ NLI verifier ready\n")
    except Exception as e:
        print(f"❌ Error loading NLI verifier: {e}")
        verifier = None
    
    # Load optional LLM explainer (only if enabled)
    if is_explainer_enabled():
        try:
            print("--- Loading LLM Explainer (Mistral 7B) ---")
            explainer = get_explainer(model_name="mistralai/Mistral-7B-Instruct-v0.2")
            if explainer:
                print("✓ LLM explainer ready\n")
            else:
                print("⚠ LLM explainer disabled\n")
        except Exception as e:
            print(f"❌ Error loading LLM explainer: {e}")
            explainer = None
    else:
        print("⚠ LLM explainer disabled (set ENABLE_LLM_EXPLAINER=true to enable)\n")


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
        "version": "0.5.0",
        "search_ready": web_search is not None,
        "verifier_ready": verifier is not None,
        "explainer_ready": explainer is not None
    }


@app.get("/health")
def health_check():
    """Health check endpoint for extension popup status monitoring."""
    return {
        "status": "ok",
        "search_ready": web_search is not None,
        "verifier_ready": verifier is not None
    }


@app.post("/check", response_model=CheckResponse)
def check_claim(req: CheckRequest):
    """
    Check a claim and return percent_true estimate with evidence.
    Uses real-time web search + NLI verification.
    """
    if web_search is None:
        raise HTTPException(
            status_code=503,
            detail="Web search engine not available."
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
    
    # Step 1: Search the web for relevant evidence
    print(f"\n--- Checking claim: {claim[:100]}... ---")
    evidence_docs = web_search.search(claim)
    
    if not evidence_docs:
        return CheckResponse(
            percent_true=50.0,
            evidences=[],
            explanation="No web results found for this claim."
        )
    
    # Step 2: Verify claim with NLI (evidence_docs already have distance key)
    verification_result = verifier.verify_claim(
        claim, 
        evidence_docs,
        relevance_threshold=0.3  # Lower threshold for better web results
    )
    
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
