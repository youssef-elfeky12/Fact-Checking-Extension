# Fact Checker Backend

FastAPI backend for the fact-checking extension.

## Setup Instructions

### 1. Create and activate virtual environment

**From project root** (recommended):

```cmd
cd "c:\Users\youss\Important\Projects\Fact-Checking-Extension"
python -m venv .venv
.venv\Scripts\activate
```

**PowerShell** (if you get execution policy errors):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```cmd
python -m pip install -r backend\requirements.txt
```

This installs:

- FastAPI + uvicorn (API server)
- sentence-transformers (embeddings)
- transformers + torch (NLI and optional LLM)
- faiss-cpu (vector search)
- bitsandbytes + accelerate (4-bit quantization for LLM)

### 3. Build FAISS index (one-time)

```cmd
python backend\build_index.py
```

This creates `data/index/faiss.index` from `data/seed_data.json`.

### 4. Pre-download models (optional, recommended)

To avoid live downloads during demos:

```cmd
scripts\preload_models.bat
```

Or manually:

```cmd
set HF_HOME=%USERPROFILE%\.cache\huggingface
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('roberta-large-mnli'); AutoModelForSequenceClassification.from_pretrained('roberta-large-mnli')"
```

### 5. Run the server

**Option A: Use batch script** (easiest):

```cmd
run_server.bat
```

**Option B: With LLM explainer**:

```cmd
run_server_with_llm.bat
```

**Option C: Manual**:

```cmd
set PYTHONPATH=%CD%\backend
set HF_HOME=%USERPROFILE%\.cache\huggingface
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

The API will be available at: http://127.0.0.1:8000  
API docs (Swagger UI): http://127.0.0.1:8000/docs

## Developer Notes

### Environment Variables

- `PYTHONPATH` - Must include `<repo_root>\backend` for imports
- `HF_HOME` - Hugging Face cache location (default: `%USERPROFILE%\.cache\huggingface`)
- `ENABLE_LLM_EXPLAINER` - Set to `true` to load Mistral 7B (Step 4)

### Model Downloads

On first startup, the backend downloads:

1. **sentence-transformers/all-mpnet-base-v2** (~420MB) - for embeddings
2. **roberta-large-mnli** (~1.4GB) - for NLI verification

If `ENABLE_LLM_EXPLAINER=true`: 3. **mistralai/Mistral-7B-Instruct-v0.2** (~3.5GB, quantized to 4-bit)

Models are cached in `HF_HOME` and won't re-download unless the cache is cleared.

### Hardware Requirements

- **Minimum**: CPU only, 8GB RAM
- **Recommended**: NVIDIA GPU with 6GB+ VRAM (for NLI + embeddings)
- **For LLM Step 4**: NVIDIA GPU with 11GB+ VRAM (RTX 2080 Ti, RTX 3060, RTX 4070+)

### Troubleshooting

**CUDA out of memory:**

- Close other GPU applications
- Don't enable LLM explainer (template explanations work fine)

**Import errors:**

- Ensure `PYTHONPATH` is set correctly
- Use the provided `run_server.bat` script

**PowerShell script execution blocked:**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Models re-downloading:**

- Check that `HF_HOME` is set and points to a persistent location
- Models are cached per-user, not per-venv

## Testing

### Using curl

```cmd
curl -X POST http://127.0.0.1:8000/check -H "Content-Type: application/json" -d "{\"tweet_text\":\"Water boils at 100 degrees Celsius.\"}"
```

### Using Python test scripts

```cmd
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_api.py -v
python -m pytest tests/test_verifier.py -v

# Run integration test (requires backend running)
python tests\test_nli_integration.py
```

## API Endpoints

### POST /check

Check a claim and return fact-check results.

**Request:**

```json
{
  "tweet_text": "Some claim to fact-check"
}
```

**Response:**

```json
{
  "percent_true": 50.0,
  "evidences": [
    {
      "source": "https://example.com",
      "snippet": "Evidence text snippet",
      "stance": "neutral",
      "score": 0.5
    }
  ],
  "explanation": "Brief explanation of the result"
}
```

## Building the Index

The FAISS index must be built before starting the server:

```cmd
python backend\build_index.py
```

This will:

- Load seed data from `data/seed_data.json`
- Generate embeddings using `all-mpnet-base-v2`
- Create FAISS index saved to `data/index/`
- Run test queries to verify functionality

The index is saved to disk and loaded on server startup.

## Current Status

✅ **Step 1**: API skeleton  
✅ **Step 2**: Semantic search (embeddings + FAISS)  
✅ **Step 3**: NLI verifier (roberta-large-mnli)  
✅ **Step 4**: Optional LLM synthesis (Mistral 7B)  
⏳ **Step 5**: Firefox extension (next)
