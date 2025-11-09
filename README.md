# AI Fact-Checker Extension for Twitter/X

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Firefox](https://img.shields.io/badge/firefox-extension-orange)

> A browser extension that adds AI-powered fact-checking to Twitter/X. Click "Verify Claim" on any tweet to get instant verification with sources.

## ✨ Features

- 🔍 **One-Click Verification** - "Verify Claim" button on every tweet
- 🤖 **AI-Powered Analysis** - Tavily AI searches and verifies claims
- 🎯 **Certainty Scores** - Clear percentage-based confidence levels (e.g., "True - 95% Certainty")
- 📚 **Source Transparency** - Top 3 most reliable sources with stance analysis
- 🎨 **Twitter-Native UI** - Seamless integration matching Twitter's design
- 🔒 **Privacy-First** - Tweet text extracted client-side only

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌────────────────┐
│ Tweet Text  │───▶│   Content    │───▶│   FastAPI   │───▶│  Tavily AI API │
│  (browser)  │    │   Script     │    │   Backend   │    │  (web search)  │
└─────────────┘    └──────────────┘    └─────────────┘    └────────────────┘
                           │                    │                    │
                           │                    └────────────────────┘
                           │                      Verdict + Sources
                           │                             │
                           └─────────────────────────────┘
                                    Display Results
```

**Flow**:

1. User clicks "Verify Claim" on a tweet
2. Content script extracts tweet text and sends to backend API
3. Backend calls Tavily AI with structured format requirements
4. Tavily searches the web and returns verdict + sources
5. Extension displays results under the tweet with color-coded verdict

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (tested on 3.12)
- **Firefox browser**
- **Tavily AI API key** (free tier: 1000 searches/month)
- ~50MB disk space

### 1. Clone Repository

```bash
git clone https://github.com/youssef-elfeky12/Fact-Checking-Extension.git
cd Fact-Checking-Extension
```

### 2. Backend Setup

```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
python -m pip install -r backend\requirements.txt

# Create .env file
copy NUL .env

# Add your Tavily API key to .env:
# TAVILY_API_KEY=your_api_key_here
```

> 💡 **Get your free Tavily API key**: Visit [tavily.com](https://tavily.com) and sign up

### 3. Start Backend Server

**Option A: Use the batch script** (recommended):

```cmd
run_server.bat
```

**Option B: Manual start**:

```cmd
set PYTHONPATH=%CD%\backend
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

### 4. Install Firefox Extension

1. Open Firefox
2. Go to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Select `manifest.json` from the `extension/` folder
5. Navigate to Twitter/X

## 📋 Usage

1. **Navigate to Twitter/X**: Open [twitter.com](https://twitter.com) or [x.com](https://x.com)
2. **Find a Tweet**: Scroll through your feed
3. **Click "Verify Claim"**: Button appears next to like/retweet buttons
4. **View Results**: See verdict, certainty, explanation, and sources
5. **Hide Results**: Click "Hide Result" to collapse the fact-check box

## 📁 Project Structure

```
Fact-Checking-Extension/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── llm_verifier.py      # Tavily AI integration
│   └── requirements.txt     # Python dependencies
├── extension/
│   ├── manifest.json        # Extension configuration
│   ├── background.js        # Background service worker
│   ├── content_script.js    # Tweet injection logic
│   ├── popup.html           # Extension popup
│   ├── popup.js             # Popup logic
│   ├── styles.css           # UI styling
│   └── *.png                # Extension icons
├── .env                     # Environment variables (create this)
├── run_server.bat           # Windows server launcher
└── README.md                # This file
```

## 🔧 API Reference

### Endpoints

- **GET** `/` - API status and version
- **GET** `/health` - Health check
- **POST** `/check` - Fact-check a claim

### Request Format

```json
{
  "tweet_text": "The Eiffel Tower grows 15cm in summer"
}
```

**Note**: Tweet text is automatically truncated to 400 characters (Tavily API limit)

### Response Format

```json
{
  "verdict": "True",
  "certainty": 0.95,
  "explanation": "The Eiffel Tower expands up to 15 centimeters in summer...",
  "evidences": [
    {
      "source": "Wikipedia - Eiffel Tower",
      "url": "https://...",
      "stance": "support",
      "score": 0.95
    }
  ]
}
```

**Verdict values**: `"True"`, `"False"`, `"Uncertain"`

## 🛠️ Development

### Running Tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run tests
pytest tests/ -v
```

### Testing the API

```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Test fact-checking endpoint
curl -X POST http://127.0.0.1:8000/check ^
  -H "Content-Type: application/json" ^
  -d "{\"tweet_text\":\"Water boils at 100 degrees Celsius.\"}"
```

API docs available at: `http://127.0.0.1:8000/docs`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tavily AI** - For providing the fact-checking search API
- **FastAPI** - For the excellent Python web framework
- **Firefox** - For the extension platform

## 📧 Contact

Youssef Elfeky

Project Link: [https://github.com/youssef-elfeky12/Fact-Checking-Extension](https://github.com/youssef-elfeky12/Fact-Checking-Extension)

## ⚠️ Disclaimer

This tool is for informational purposes only. Always verify important claims through multiple reliable sources. AI can make mistakes.

---

Made with ❤️ by Youssef Elfeky
