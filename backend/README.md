# Fact Checker Backend

FastAPI backend for the fact-checking extension.

## Setup Instructions

### 1. Create and activate virtual environment

```cmd
cd "c:\Users\youss\Important\Projects\Fact Checking Project\backend"
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```cmd
pip install -r requirements.txt
```

### 3. Run the server

**PowerShell (from project root):**

```powershell
cd "c:\Users\youss\Important\Projects\Fact Checking Project"
$env:PYTHONPATH = "c:\Users\youss\Important\Projects\Fact Checking Project\backend"; & ".venv\Scripts\uvicorn.exe" backend.main:app --host 127.0.0.1 --port 8000
```

**CMD (from project root):**

```cmd
cd "c:\Users\youss\Important\Projects\Fact Checking Project"
set PYTHONPATH=c:\Users\youss\Important\Projects\Fact Checking Project\backend
.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000
```

The API will be available at: http://127.0.0.1:8000

API docs (Swagger UI): http://127.0.0.1:8000/docs

## Testing

### Using curl (from cmd)

```cmd
curl -X POST http://127.0.0.1:8000/check -H "Content-Type: application/json" -d "{\"tweet_text\":\"The Earth is round.\"}"
```

### Using the test script

Make sure the backend is running, then:

```cmd
cd "c:\Users\youss\Important\Projects\Fact Checking Project\tests"
python test_api.py
```

Or with pytest:

```cmd
pip install pytest requests
pytest test_api.py -v
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

Before running the server, you need to build the FAISS search index:

```cmd
cd "c:\Users\youss\Important\Projects\Fact Checking Project"
& ".venv\Scripts\python.exe" backend\build_index.py
```

This will:

- Load seed data from `data/seed_data.json`
- Generate embeddings using `all-mpnet-base-v2`
- Create FAISS index in `data/index/`
- Run test queries to verify

## Current Status

**Step 2 Complete:** Semantic search with embeddings + FAISS. NLI verification pending.
