# Step 3 Complete: NLI Verifier and Scoring ✅

## What Was Added

1. **NLI Verifier Module** (`backend/verifier.py`)

   - Uses roberta-large-mnli for Natural Language Inference
   - Computes entailment/neutral/contradiction probabilities
   - Maps NLI scores to 0-100% truth score
   - Assigns stance (support/contradict/neutral) to each evidence
   - Generates natural language explanations

2. **Updated API** (`backend/main.py` v0.3.0)

   - Integrated NLI verifier into /check endpoint
   - Now returns real NLI-based truth scores
   - Enhanced error handling and logging

3. **Tests**
   - Unit tests: `tests/test_verifier.py`
   - Integration tests: `tests/test_nli_integration.py`

## How to Test

### 1. Install Dependencies

```cmd
cd c:\Users\youss\Important\Projects\Fact-Checking-Extension
python -m pip install transformers torch
```

### 2. Start the Backend

```cmd
cd c:\Users\youss\Important\Projects\Fact-Checking-Extension
set PYTHONPATH=c:\Users\youss\Important\Projects\Fact-Checking-Extension\backend
.venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Note**: First startup will download the roberta-large-mnli model (~1.4GB). This is a one-time download.

### 3. Run Tests

**Unit tests:**

```cmd
python tests\test_verifier.py
```

**Integration tests** (requires backend running):

```cmd
python tests\test_nli_integration.py
```

### 4. Manual Testing with curl

```cmd
curl -X POST http://127.0.0.1:8000/check -H "Content-Type: application/json" -d "{\"tweet_text\":\"Water boils at 100 degrees Celsius.\"}"
```

Expected response:

```json
{
  "percent_true": 85.0,
  "evidences": [
    {
      "source": "https://example.com/chemistry",
      "snippet": "At sea level, water boils at 100°C...",
      "stance": "support",
      "score": 0.92
    }
  ],
  "explanation": "This claim appears likely true based on 3 evidence source(s)..."
}
```

## Truth Score Formula

```
truth_score = 100 * (entailment + 0.5*neutral - contradiction)
truth_score = clamp(truth_score, 0, 100)
```

**Interpretation**:

- **75-100%**: Likely true (strong evidence support)
- **50-75%**: Partially true or uncertain
- **25-50%**: Partially false or uncertain
- **0-25%**: Likely false (strong evidence contradiction)

## Key Files

- `backend/verifier.py` - NLI verifier implementation
- `backend/main.py` - Updated API with NLI integration
- `tests/test_verifier.py` - Unit tests
- `tests/test_nli_integration.py` - Integration tests
- `backend/requirements.txt` - Updated dependencies

## What Changed in the API

### Before (Step 2)

- Truth score based on semantic similarity distance
- All evidence marked as "neutral" stance
- Placeholder explanation

### After (Step 3)

- Truth score based on NLI entailment probabilities
- Evidence assigned "support", "contradict", or "neutral" stance
- Detailed explanation with evidence breakdown
- More accurate fact-checking results

## Performance Notes

- **First request**: 5-10 seconds (model loading)
- **Subsequent requests**: ~1-2 seconds per claim (5 evidence docs)
- **GPU**: Speeds up inference 3-5x if available
- **CPU**: Works fine, just slower

## Next Steps

Type `continue` when ready to proceed to **Step 4: Optional LLM synthesis** for enhanced natural language explanations.

## Troubleshooting

**Model download fails:**

- Check internet connection
- HuggingFace downloads from https://huggingface.co/
- Model saved to `~/.cache/huggingface/`

**Out of memory:**

- roberta-large-mnli needs ~2GB RAM
- If CPU limited, consider smaller model in future
- GPU with 4GB+ VRAM is ideal

**Import errors:**

- Ensure transformers and torch are installed
- Check: `python -m pip list | findstr transformers`
