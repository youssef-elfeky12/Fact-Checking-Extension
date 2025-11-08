# 🚀 Quick Start Guide - LLM Fact Checker

## Step 1: Get Groq API Key (2 minutes)

1. Go to **https://console.groq.com**
2. Click "Sign Up" (free!)
3. After signing in, click **"API Keys"** in the left sidebar
4. Click **"Create API Key"**
5. **Copy the key** (starts with `gsk_...`)

## Step 2: Create .env File

In the **project root folder** (where this file is), create a new file called `.env`:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

**⚠️ IMPORTANT**: Replace `gsk_your_actual_key_here` with the key you copied!

Example:

```
GROQ_API_KEY=gsk_abc123xyz789example
```

## Step 3: Start the Server

Double-click `run_server.bat` or run in terminal:

```bash
.\run_server.bat
```

You should see:

```
✓ Web search engine ready (DuckDuckGo - 10 sources)
--- Loading LLM Verifier (Groq API) ---
✓ LLM verifier ready
```

## Step 4: Load Extension in Firefox

1. Open Firefox
2. Go to `about:debugging#/runtime/this-firefox`
3. Click **"Load Temporary Add-on"**
4. Navigate to `extension/` folder
5. Select `manifest.json`

## Step 5: Test It!

1. Go to **Twitter/X** (twitter.com or x.com)
2. Find any tweet with a factual claim
3. Click the **🔍 Fact Check** button below the tweet
4. Wait 3-5 seconds for the LLM to analyze sources
5. See the verdict with reasoning and clickable sources!

---

## What's Different Now?

### ✅ BEFORE (Old NLI System):

- Just compared text similarity
- Didn't understand context
- Couldn't explain reasoning
- Sources weren't actually used by the AI

### ✅ NOW (LLM System):

- **Real AI reads the sources**
- **Understands context and nuance**
- **Cites which sources it used**
- **Explains reasoning in plain English**
- **More accurate verdicts**

---

## Example Output

**Claim**: "The Great Wall of China is visible from the Moon"

**Old System**:

- Truth: 45% ❌ (Wrong!)
- Sources: Random articles
- Explanation: Generic template

**New System**:

- Verdict: REFUTES ✅ (Correct!)
- Confidence: 95%
- Sources Used: [1, 2, 4] (NASA, Wikipedia, Space.com)
- Reasoning: "According to NASA (Source 1) and multiple astronauts, the Great Wall is not visible from the Moon with the naked eye. While it's a popular myth, the wall is too narrow and blends with the surrounding terrain. Source 2 (Wikipedia) confirms this is a common misconception."

---

## Troubleshooting

### "GROQ_API_KEY not found in environment"

→ You forgot to create the `.env` file or put it in the wrong folder
→ The `.env` file must be in the **project root** (same folder as this README)

### "Backend not available"

→ Make sure the server is running (`run_server.bat`)
→ Check server logs for errors

### "No sources found"

→ DuckDuckGo rate limit - wait 30 seconds and try again
→ Try rephrasing the claim

### Sources seem irrelevant

→ The LLM is smart enough to ignore irrelevant sources
→ It only cites the sources it actually used

---

## Testing Without Extension

Want to test the LLM without opening Twitter?

```bash
.venv\Scripts\python.exe test_llm.py
```

This will test 3 example claims and show the LLM's analysis!

---

## Cost & Rate Limits

**Groq Free Tier**:

- ✅ Completely FREE
- 30 requests per minute
- 14,400 requests per day
- Perfect for personal use!

If you hit the limit, just wait a minute or two.

---

## Need Help?

Check `LLM_SETUP.md` for detailed information about:

- How the system works
- Available models
- Architecture changes
- Advanced configuration
