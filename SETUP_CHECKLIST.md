# ✅ Setup Checklist

Follow these steps in order:

## □ Step 1: Get Groq API Key

1. [ ] Go to https://console.groq.com
2. [ ] Sign up (free account)
3. [ ] Navigate to "API Keys" section
4. [ ] Click "Create API Key"
5. [ ] Copy the key (starts with `gsk_`)

## □ Step 2: Create .env File

1. [ ] Open the project folder: `C:\Users\youss\Important\Projects\Fact-Checking-Extension`
2. [ ] Create a new file called `.env` (no extension, just `.env`)
3. [ ] Add this line: `GROQ_API_KEY=your_key_here`
4. [ ] Replace `your_key_here` with your actual key
5. [ ] Save the file

**Example .env file:**

```
GROQ_API_KEY=gsk_abc123xyz789
```

## □ Step 3: Test Backend

1. [ ] Open terminal in project folder
2. [ ] Run: `.\run_server.bat`
3. [ ] Look for these messages:
   - ✓ Web search engine ready
   - ✓ LLM verifier ready
4. [ ] If you see errors, check the `.env` file

## □ Step 4: Load Extension

1. [ ] Open Firefox
2. [ ] Go to `about:debugging#/runtime/this-firefox`
3. [ ] Click "Load Temporary Add-on"
4. [ ] Select `extension/manifest.json`
5. [ ] Extension should appear in the list

## □ Step 5: Test on Twitter

1. [ ] Go to twitter.com or x.com
2. [ ] Find a tweet with a factual claim
3. [ ] Click the 🔍 "Fact Check" button
4. [ ] Wait 3-5 seconds
5. [ ] See the LLM's verdict with reasoning!

---

## Troubleshooting

### "GROQ_API_KEY not found"

- ❌ Problem: `.env` file missing or wrong location
- ✅ Solution: Make sure `.env` is in the **project root folder** (same level as `run_server.bat`)

### "Backend not available"

- ❌ Problem: Server not running
- ✅ Solution: Start the server with `.\run_server.bat`

### "Rate limit exceeded"

- ❌ Problem: Too many requests
- ✅ Solution: Wait 1-2 minutes, Groq has free tier limits

### "No sources found"

- ❌ Problem: DuckDuckGo rate limiting
- ✅ Solution: Wait 30 seconds and try again

---

## Quick Test Commands

### Test without extension:

```bash
.venv\Scripts\python.exe test_llm.py
```

### Check if .env is loaded:

```bash
.venv\Scripts\python.exe -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'Found!' if os.getenv('GROQ_API_KEY') else 'NOT FOUND')"
```

### Test web search only:

```bash
.venv\Scripts\python.exe test_relevance.py
```

---

## What's Different?

### Before (NLI Model):

- ❌ Just compared text similarity
- ❌ Didn't understand context
- ❌ 4GB of dependencies
- ❌ Slow first run (model download)
- ❌ Often wrong verdicts

### Now (LLM):

- ✅ Actually reads sources
- ✅ Understands context and nuance
- ✅ Only 1MB of dependencies
- ✅ Fast every time (API)
- ✅ Much more accurate

---

## You're Ready!

Once all checkboxes are ticked, your fact-checker will:

1. Search the web for reliable sources
2. Have a 70B parameter LLM read them
3. Get an informed verdict with reasoning
4. Show you exactly which sources were used
5. Provide clickable links to verify yourself

**Total setup time: ~5 minutes**
**Result: Production-ready AI fact checker!** 🎉
