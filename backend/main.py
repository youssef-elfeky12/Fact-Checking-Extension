"""
Fact Checker API - Backend Service
FastAPI-based backend that fact-checks claims using Tavily AI search.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .llm_verifier import get_llm_verifier

app = FastAPI(
    title="Fact Checker API",
    version="1.0.0",
    description="AI-powered fact-checking API using Tavily search"
)

# CORS configuration for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_verifier = None


@app.on_event("startup")
async def startup_event():
    """Load Tavily AI verifier on startup."""
    global llm_verifier
    
    # Initialize Tavily verifier
    try:
        print("--- Loading Tavily AI Verifier ---")
        llm_verifier = get_llm_verifier()
        print("✓ Tavily verifier ready\n")
    except Exception as e:
        print(f"❌ Error loading Tavily verifier: {e}")
        print(f"   Make sure TAVILY_API_KEY is set in .env file")
        print(f"   Get free key from: https://tavily.com\n")
        llm_verifier = None


class CheckRequest(BaseModel):
    tweet_text: str


class Evidence(BaseModel):
    source: str
    snippet: str
    stance: str  # "support" | "contradict" | "neutral"
    score: float
    url: str  # URL to the source website


class CheckResponse(BaseModel):
    percent_true: float
    evidences: list[Evidence]
    explanation: str
    verdict: str  # "SUPPORTS" | "REFUTES" | "NOT ENOUGH INFO"
    certainty: float  # 0.0 to 1.0 (the AI's actual certainty)


@app.get("/")
def root():
    return {
        "message": "Fact Checker API is running",
        "version": "0.7.0",
        "llm_verifier_ready": llm_verifier is not None
    }


@app.get("/health")
def health_check():
    """Health check endpoint for extension popup status monitoring."""
    return {
        "status": "ok",
        "llm_verifier_ready": llm_verifier is not None
    }


@app.post("/check", response_model=CheckResponse)
def check_claim(req: CheckRequest):
    """
    Fact-check a claim using Tavily AI.
    
    Args:
        req: CheckRequest containing the claim text
        
    Returns:
        CheckResponse with verdict, certainty, explanation, and sources
        
    Raises:
        HTTPException: If verifier is unavailable or claim is empty
    """
    if llm_verifier is None:
        raise HTTPException(
            status_code=503,
            detail="Tavily AI verifier not available. Check TAVILY_API_KEY in .env file."
        )
    
    # Extract claim text
    claim = req.tweet_text.strip()
    
    if not claim:
        raise HTTPException(status_code=400, detail="Claim text cannot be empty")
    
    # Verify the claim using Tavily AI
    verification_result = llm_verifier.verify_claim(claim)
    
    # Convert verdict to percentage scale for UI
    verdict = verification_result['verdict']
    confidence = verification_result['confidence']
    
    if verdict == "SUPPORTS":
        percent_true = 50 + (confidence * 50)
    elif verdict == "REFUTES":
        percent_true = 50 - (confidence * 50)
    else:
        percent_true = 50.0
    
    # Format sources for display
    evidences = []
    for source in verification_result['sources'][:3]:
        # Determine stance from verdict
        if verdict == "SUPPORTS":
            stance = "support"
        elif verdict == "REFUTES":
            stance = "contradict"
        else:
            stance = "neutral"
        
        evidences.append(Evidence(
            source=source['title'],
            snippet=f"Source: {source['title']}",
            stance=stance,
            score=confidence,
            url=source['url']
        ))
    
    return CheckResponse(
        percent_true=percent_true,
        evidences=evidences,
        explanation=verification_result['reasoning'],
        verdict=verdict,
        certainty=confidence
    )
