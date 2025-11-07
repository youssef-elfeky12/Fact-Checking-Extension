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
✅ **Step 4 Complete**: Optional LLM synthesis (Mistral 7B - toggleable)  
⏳ **Step 5**: Firefox extension  
⏳ **Step 6**: Logging and feedback  
⏳ **Step 7**: Documentation and packaging

## Quick Start

### Prerequisites

- Python 3.9+ (tested on 3.9, 3.11, 3.12)
- 11GB GPU (NVIDIA) for optional LLM synthesis (Step 4)
- Firefox browser (for Step 5)
- ~5GB disk space for models and dependencies

### Setup

1. **Clone and navigate to project root**:

```cmd
cd "c:\Users\youss\Important\Projects\Fact-Checking-Extension"
```

2. **Create and activate virtual environment**:

**CMD:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**PowerShell** (may require execution policy change):

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

3. **Install dependencies**:

```cmd
python -m pip install -r backend\requirements.txt
```

4. **Build FAISS search index** (one-time, or when seed data changes):

```cmd
python backend\build_index.py
```

This creates `data/index/faiss.index` from `data/seed_data.json`.

5. **Start the backend server**:

**Option A: Use the provided batch script** (recommended):

```cmd
run_server.bat
```

**Option B: Manual start**:

```cmd
set PYTHONPATH=%CD%\backend
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Option C: With LLM explainer enabled** (requires GPU, downloads ~4GB model):

```cmd
run_server_with_llm.bat
```

The server will download NLI models (~1.4GB) on first startup. This is cached in `%USERPROFILE%\.cache\huggingface\` and won't re-download on subsequent runs.

6. **Test the API**:

```cmd
curl -X POST http://127.0.0.1:8000/check -H "Content-Type: application/json" -d "{\"tweet_text\":\"Water boils at 100 degrees Celsius.\"}"
```

Or run the test suite:

```cmd
python -m pytest tests/ -v
```

API docs: http://127.0.0.1:8000/docs

### Optional: Pre-download Models

To avoid live downloads during demos, pre-download models after installing requirements:

**NLI Model (roberta-large-mnli, ~1.4GB)**:

```cmd
.venv\Scripts\python.exe -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('roberta-large-mnli'); AutoModelForSequenceClassification.from_pretrained('roberta-large-mnli')"
```

**LLM Model (Mistral 7B, ~3.5GB)** - only if using `run_server_with_llm.bat`:

```cmd
set ENABLE_LLM_EXPLAINER=true
.venv\Scripts\python.exe -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('mistralai/Mistral-7B-Instruct-v0.2'); print('Mistral 7B downloaded')"
```

Models are cached in `%USERPROFILE%\.cache\huggingface\` by default.

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
- **Local-First**: Runs on developer machine (GPU accelerated when available)
- **Privacy-Friendly**: Extracts tweet text client-side, minimal storage
- **Models Used**:
  - sentence-transformers/all-mpnet-base-v2 (~420MB) - embeddings
  - roberta-large-mnli (~1.4GB) - NLI verification
  - mistralai/Mistral-7B-Instruct-v0.2 (~3.5GB, optional) - explanations
- **Demo Purpose**: Short-lived Firefox sideload for LinkedIn/GitHub portfolio

## Environment Variables

- `HF_HOME` - Hugging Face cache directory (default: `%USERPROFILE%\.cache\huggingface`)
- `ENABLE_LLM_EXPLAINER` - Set to `true` to enable Mistral 7B explanations (default: `false`)
- `PYTHONPATH` - Set to `<repo_root>\backend` for imports to work

## Troubleshooting

### Model Re-downloads Every Time

- Models are cached in `%USERPROFILE%\.cache\huggingface\`. If this directory is cleared or the venv is recreated, models won't re-download as long as the cache remains.
- Set `HF_HOME` explicitly in your environment or run scripts to control cache location.

### PowerShell Execution Policy Error

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### CUDA Out of Memory (Step 4 LLM)

- Close other GPU applications
- Don't enable LLM explainer (use template explanations instead)
- The 4-bit quantized Mistral 7B needs ~4GB VRAM + ~2GB for NLI/embeddings

### Import Errors

- Ensure PYTHONPATH is set: `set PYTHONPATH=%CD%\backend`
- Or use the provided `run_server.bat` script

## Next Steps

✅ Steps 1–4 complete. Type **`continue`** to proceed to **Step 5: Firefox Extension** development.

For detailed step-by-step instructions, see:

- `copilot_prompt.md` - Full project prompt and workflow
- `STEP3_COMPLETE.md` - NLI verifier setup
- `STEP4_COMPLETE.md` - LLM explainer setup
- `backend/README.md` - Backend-specific instructions

## License

MIT (to be added in Step 7)
