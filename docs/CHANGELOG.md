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

---

## Step 4 - Optional LLM Synthesis (Mistral 7B) (2025-11-07)

### Added

- **New module**: `backend/explainer.py` (245 lines)

  - Implemented `LLMExplainer` class using `mistralai/Mistral-7B-Instruct-v0.2`
  - Uses 4-bit quantization via bitsandbytes (fits in 11GB GPU)
  - `generate_explanation()` - generates natural language explanations from claim + evidence
  - Template-based fallback if LLM generation fails
  - Toggleable via `ENABLE_LLM_EXPLAINER` environment variable
  - Auto-detects GPU/CPU and adjusts accordingly

- **Updated**: `backend/main.py` (v0.4.0)

  - Integrated optional LLM explainer into startup
  - Modified `/check` endpoint to use LLM explanations when enabled
  - Falls back to template-based explanations if LLM disabled or fails
  - Enhanced health check with explainer status

- **Dependencies**: Added to `requirements.txt`

  - `bitsandbytes==0.41.0` (4-bit quantization)
  - `accelerate==0.24.0` (efficient model loading)

- **Tests**: `tests/test_explainer.py`

  - Tests for LLM loading
  - Tests for explanation generation (true/false claims)
  - Tests for fallback mechanism
  - Requires `ENABLE_LLM_EXPLAINER=true` to run

- **Documentation**: `STEP4_COMPLETE.md`
  - Installation guide
  - How to enable/disable LLM
  - Performance benchmarks
  - Troubleshooting guide

### Technical Details

**Model**: Mistral 7B Instruct v0.2

- Parameters: 7 billion
- Quantization: 4-bit NF4 (bitsandbytes)
- Size: ~3.5-4GB on disk/memory
- Context window: 8192 tokens
- Inference: ~1-2 seconds per explanation (GPU)

**Prompt Format**: Mistral Instruct format

```
[INST] {system_prompt}
Claim: "{claim}"
Truth Score: {score}%
Evidence: {evidence_list}
{task_instruction} [/INST]
```

**Generated Explanations**:

- 2-3 sentences
- Cites evidence sources
- Explains verdict reasoning
- More natural than template-based

**Toggle Control**:

- **Disabled by default** (template explanations only)
- Enable: Set `ENABLE_LLM_EXPLAINER=true` environment variable
- Check status: GET `/` returns `explainer_ready: true/false`

**Memory Usage**:
| Configuration | Memory | Startup Time | Per-request |
|---------------|--------|--------------|-------------|
| LLM Disabled | ~2GB | ~5s | ~1s |
| LLM Enabled | ~6-7GB | ~15s | ~2-3s |

**GPU Requirements**:

- NVIDIA GPU with 11GB+ VRAM (recommended)
- CUDA 11.8+ and compatible drivers
- Falls back to CPU if no GPU (slower, ~10-20s per explanation)

### Workflow Integration

1. User submits claim via POST /check
2. Semantic search retrieves evidence (Step 2)
3. NLI computes truth score (Step 3)
4. **NEW**: If `explainer` enabled, generate LLM explanation
   - Mistral 7B synthesizes 2-3 sentence explanation
   - Cites evidence and explains reasoning
5. If LLM disabled/fails, use template explanation (Step 3)
6. Return response with explanation

### Example Outputs

**Template Explanation (Step 3)**:

```
This claim appears likely true based on 3 evidence source(s).
2 source(s) support the claim. 1 source(s) are neutral or inconclusive.
```

**LLM Explanation (Step 4)**:

```
The claim is likely true. Scientific evidence confirms that water boils
at 100°C at sea level under standard atmospheric pressure. Two reliable
sources directly support this well-established physical fact.
```

### Files Added/Modified

- `backend/explainer.py` (new - 245 lines)
- `backend/main.py` (modified - integrated LLM)
- `backend/requirements.txt` (modified - added bitsandbytes, accelerate)
- `tests/test_explainer.py` (new - 222 lines)
- `STEP4_COMPLETE.md` (new - setup guide)
- `README.md` (updated status: Step 4 ✅)

### Optional Feature

**This step is completely optional**:

- API works fine without it (uses template explanations)
- Requires significant GPU resources (~4GB extra)
- Better for production, but template is fine for demos
- Can be enabled/disabled anytime via environment variable

### Next Step

Waiting for user to type "continue" to proceed to Step 5 (Firefox extension UI).
