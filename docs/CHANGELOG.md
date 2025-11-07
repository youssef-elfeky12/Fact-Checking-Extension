# Changelog

## Step 1 - Project skeleton and minimal API (2025-11-06)

### Added

- Created project folder structure: /backend, /extension, /data, /docs, /tests
- Implemented minimal FastAPI app with POST /check endpoint
- Added CORS middleware for Firefox extension compatibility
- Created requirements.txt with FastAPI, uvicorn, pydantic dependencies
- Added test_api.py script with basic endpoint validation
- Created backend README.md with setup and usage instructions
- Added .gitignore for Python and project artifacts

### Features

- POST /check endpoint returns structured JSON with percent_true, evidences, explanation
- Placeholder response (50% confidence) for testing
- CORS enabled for localhost development
- HTTP 200 response validation in tests

### Files Added

- backend/main.py
- backend/requirements.txt
- backend/README.md
- tests/test_api.py
- docs/CHANGELOG.md
- .gitignore

### Next Step

Completed. User typed "continue".

---

## Step 2 - Semantic search (embeddings + FAISS) and seed data (2025-11-06)

### Added

- Created embeddings.py with EmbeddingSearchEngine class
- Added sentence-transformers (all-mpnet-base-v2) for semantic embeddings
- Integrated FAISS for vector similarity search
- Created seed_data.json with 10 fact-check documents
- Implemented build_index.py script to create/rebuild FAISS index
- Updated main.py to load index on startup and use semantic search
- Added test_search.py for semantic search validation

### Changed

- Updated requirements.txt: added sentence-transformers==2.7.0, faiss-cpu==1.12.0, numpy
- Modified /check endpoint to use semantic search instead of placeholder
- API now returns real evidence from indexed documents with similarity scores

### Features

- Semantic search using 768-dimensional embeddings (all-mpnet-base-v2)
- FAISS index with 10 seed documents covering scientific facts
- Evidence retrieval returns top 5 most similar documents
- Snippet extraction (200 chars max) from evidence text
- Distance-to-score conversion for ranking
- Index persistence (save/load from disk)

### Test Results

- Index built successfully with 10 documents
- Query "Is the Earth round?" correctly retrieves Earth shape document (distance: 0.63)
- Query "What temperature does water boil?" retrieves boiling point doc (85.0% confidence)
- Query "Are vaccines safe?" retrieves vaccine safety doc (85.7% confidence)
- Query "How fast is light?" retrieves speed of light doc (83.9% confidence)
- All semantic search tests: PASS

### Files Added/Modified

- backend/embeddings.py (new)
- backend/build_index.py (new)
- backend/main.py (modified - added search engine integration)
- data/seed_data.json (new)
- data/index/ (generated - faiss.index, documents.pkl)
- tests/test_search.py (new)
- backend/requirements.txt (modified)

### Next Step

Waiting for user to type "continue" to proceed to Step 3 (NLI verifier + scoring aggregation).

---

## Step 3 - NLI Verifier and Scoring (2025-11-07)

### Added

- **New module**: `backend/verifier.py`

  - Implemented `NLIVerifier` class using `roberta-large-mnli` model
  - `compute_nli_scores()` - computes entailment/neutral/contradiction probabilities for premise-hypothesis pairs
  - `verify_claim()` - verifies claims against multiple evidence documents
  - Truth score formula: `100 * (entailment + 0.5*neutral - contradiction)` clamped to [0, 100]
  - Automatic stance detection (support/contradict/neutral) for each evidence
  - Natural language explanation generation based on aggregated NLI scores

- **Updated**: `backend/main.py` (v0.3.0)

  - Integrated NLI verifier into startup event
  - Modified `/check` endpoint to use NLI-based verification
  - Loads `roberta-large-mnli` model on startup (GPU/CPU auto-detection)
  - Now returns real NLI-based truth scores instead of distance-based placeholders
  - Enhanced health check endpoint with verifier status

- **Dependencies**: Added to `requirements.txt`

  - `transformers==4.35.0`
  - `torch==2.1.0`

- **Tests**: `tests/test_verifier.py`

  - Unit tests for NLI score computation
  - Tests for claim verification with supporting evidence (expects truth_score > 50)
  - Tests for claim verification with contradicting evidence (expects truth_score < 50)
  - Tests for no-evidence handling (returns 50.0)
  - Tests for truth score formula with edge cases and clamping

- **Integration test**: `tests/test_nli_integration.py`
  - End-to-end tests for `/check` endpoint with NLI
  - Tests multiple claim types (likely true/likely false/neutral)
  - Validates stance assignment and explanation generation

### Technical Details

**NLI Model**: roberta-large-mnli (facebook)

- Pre-trained on MNLI (Multi-Genre Natural Language Inference) dataset
- Returns [contradiction, neutral, entailment] logits
- Model size: ~1.4GB
- GPU-accelerated when available (auto-falls back to CPU)
- First request loads model (5-10s delay)

**Truth Score Mapping**:

- 75-100%: Likely true (strong entailment from evidence)
- 50-75%: Partially true or uncertain
- 25-50%: Partially false or uncertain
- 0-25%: Likely false (strong contradiction from evidence)

**Workflow**:

1. User submits claim via POST /check
2. Semantic search retrieves top 5 relevant documents (Step 2)
3. NLI model computes entailment scores for each (claim, evidence) pair
4. Average NLI probabilities calculated across all evidence
5. Truth score computed using deterministic formula
6. Stance assigned to each evidence (support/contradict/neutral)
7. Explanation generated describing verdict and evidence breakdown

**API Response Format** (updated):

```json
{
  "percent_true": 85.5,
  "evidences": [
    {
      "source": "https://example.com/science",
      "snippet": "Water boils at 100°C at sea level...",
      "stance": "support",
      "score": 0.92
    }
  ],
  "explanation": "This claim appears likely true based on 3 evidence source(s). 2 source(s) support the claim. 1 source(s) are neutral or inconclusive."
}
```

### Files Added/Modified

- `backend/verifier.py` (new - 247 lines)
- `backend/main.py` (modified - integrated NLI verifier)
- `backend/requirements.txt` (modified - added transformers, torch)
- `tests/test_verifier.py` (new - 214 lines)
- `tests/test_nli_integration.py` (new - integration test)
- `README.md` (updated status: Step 3 ✅)

### Next Step

Waiting for user to type "continue" to proceed to Step 4 (Optional LLM synthesis for enhanced explanations).
