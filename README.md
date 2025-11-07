# Fact-Checking Browser Extension

A Firefox browser extension that adds a "Check Fact" button to tweets, providing AI-powered fact-checking with confidence scores and supporting evidence.

## Project Overview

This project uses a retrieval-augmented verification approach (semantic search + NLI) to fact-check claims. It does NOT train models from scratch but leverages pre-trained open-source models for accurate, interpretable results.

### Architecture

- **Backend**: FastAPI (Python) with FAISS vector DB for semantic search
- **Embeddings**: sentence-transformers (all-mpnet-base-v2)
- **Verifier**: NLI models (roberta-large-mnli or bart-large-mnli)
- **Optional**: Quantized 7B LLM for explanation synthesis (uses 11GB GPU)
- **Frontend**: Firefox extension (Manifest V3) that extracts tweet text from DOM

### Current Status

✅ **Step 1 Complete**: Minimal API skeleton with placeholder responses  
✅ **Step 2 Complete**: Add semantic search (embeddings + FAISS)  
✅ **Step 3 Complete**: Add NLI verifier and scoring  
⏳ **Step 4**: Optional LLM synthesis  
⏳ **Step 5**: Firefox extension  
⏳ **Step 6**: Logging and feedback  
⏳ **Step 7**: Documentation and packaging

## Quick Start

### Prerequisites

- Python 3.12+
- 11GB GPU (NVIDIA) for optional LLM synthesis
- Firefox browser

### Setup

1. **Clone and navigate**:

```cmd
cd "c:\Users\youss\Important\Projects\Fact-Checking-Extension"
```

2. **Backend setup** (see `backend/README.md` for details):

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run backend**:

```cmd
uvicorn main:app --host 127.0.0.1 --port 8000
```

4. **Test**:

```cmd
python ..\tests\test_api.py
```

API docs: http://127.0.0.1:8000/docs

## Project Structure

```
Fact-Checking-Extension/
├── backend/          # FastAPI server
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── extension/        # Firefox extension (Step 5)
├── data/            # Seed corpus for FAISS (Step 2)
├── tests/           # Test scripts
│   └── test_api.py
├── docs/
│   └── CHANGELOG.md
└── README.md
```

## Technology Stack

- **Free/Open-Source Only**: No paid APIs or services
- **Local-First**: Runs on developer machine with GPU
- **Privacy-Friendly**: Extracts tweet text client-side, minimal storage
- **Demo Purpose**: Short-lived Firefox sideload for LinkedIn/GitHub portfolio

## Next Steps

Type "continue" to proceed to Step 2 (semantic search implementation).

## License

MIT (to be added in Step 7)
