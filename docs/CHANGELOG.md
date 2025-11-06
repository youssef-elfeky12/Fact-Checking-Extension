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
