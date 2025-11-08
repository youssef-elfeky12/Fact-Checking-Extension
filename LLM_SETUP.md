# LLM-Based Fact Checker Setup Guide

## What Changed?

We replaced the old NLI model (RoBERTa) with a **real LLM** that can:

- Actually read and understand sources
- Cite which sources it used
- Explain its reasoning in plain English
- Give accurate verdicts with confidence scores

## Manual Setup Steps

### 1. Get a Free Groq API Key

1. Go to https://console.groq.com
2. Sign up (it's free!)
3. Click on "API Keys" in the sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)

### 2. Create .env File

In the project root folder, create a file named `.env`:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

**Important**: Replace `gsk_your_actual_key_here` with your actual key!

### 3. Install Dependencies

The `groq` package should already be installed. If not:

```bash
.venv\Scripts\pip install groq python-dotenv
```

### 4. Start the Server

```bash
.\run_server.bat
```

Or manually:

```bash
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You should see:

```
✓ Web search engine ready (DuckDuckGo - 10 sources)
--- Loading LLM Verifier (Groq API) ---
✓ LLM verifier ready
```

### 5. Test It!

Go to Twitter/X and click the fact-check button on any tweet!

## How It Works Now

1. **User submits claim** → "The Eiffel Tower grows 15cm in summer"
2. **DuckDuckGo search** → Finds 10 relevant sources
3. **LLM reads all sources** → Groq's Llama 3.3 70B analyzes them
4. **LLM provides verdict** → SUPPORTS/REFUTES/NOT ENOUGH INFO
5. **LLM cites sources** → Shows which sources it actually used
6. **Explanation returned** → Shows the LLM's reasoning

## Models Available

In `backend/llm_verifier.py`, you can change the model:

- `llama-3.3-70b-versatile` ← **Recommended** (smart, fast)
- `mixtral-8x7b-32768` (good for long context)
- `llama-3.1-8b-instant` (fastest but less accurate)

## Troubleshooting

### "GROQ_API_KEY not found"

→ Make sure `.env` file exists in project root with your key

### "API rate limit exceeded"

→ Groq free tier has limits. Wait a few minutes or upgrade account

### "No sources found"

→ DuckDuckGo might be rate limiting. Wait 30 seconds and try again

### Sources still irrelevant

→ The relevance filter now requires only 1 keyword match, letting the LLM decide what's relevant

## What Was Removed

- ❌ Old NLI model (RoBERTa - 1.4GB)
- ❌ Sentence transformers
- ❌ FAISS index
- ❌ Torch, transformers, bitsandbytes (huge dependencies)
- ❌ Explainer.py (LLM handles explanations now)
- ❌ Verifier.py (replaced with llm_verifier.py)

The codebase is now **much cleaner and faster**!
