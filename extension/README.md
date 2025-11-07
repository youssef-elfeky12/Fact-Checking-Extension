# Fact Checker Browser Extension

A Firefox extension that adds AI-powered fact-checking to Twitter/X. Click the "🔍 Check Fact" button on any tweet to verify claims using semantic search and NLI verification.

## Features

- **One-Click Fact Checking**: Check any tweet with a single button click
- **Real-time Verification**: Instant results using local AI models
- **Evidence Display**: Shows supporting/contradicting evidence with source links
- **Color-Coded Truth Scores**: Visual indicators (green/yellow/red) for claim accuracy
- **No External Services**: All processing runs locally on your machine

## Requirements

- **Firefox Browser**: Version 109.0 or later
- **Backend API**: Must be running on `http://127.0.0.1:8000`
- **Python Environment**: See main project README for backend setup

## Installation (Temporary Extension for Development)

1. **Prepare Icon Files** (Required)

   - You need to create 3 icon files: `icon-16.png`, `icon-48.png`, `icon-128.png`
   - Place them in the `extension/` folder
   - Recommended: Use a simple magnifying glass or checkmark icon
   - Tools: Figma, Canva, or any online icon generator

2. **Start the Backend Server**

   ```cmd
   cd backend
   ..\run_server.bat
   ```

   - Wait for "Uvicorn running on http://127.0.0.1:8000" message
   - Verify models are loaded (you should see "✓ NLI verifier ready")

3. **Load Extension in Firefox**

   - Open Firefox
   - Navigate to `about:debugging#/runtime/this-firefox`
   - Click **"Load Temporary Add-on..."**
   - Browse to your `extension/` folder
   - Select `manifest.json`
   - You should see "Fact Checker" appear in the loaded extensions list

4. **Test the Extension**

   - Navigate to [twitter.com](https://twitter.com) or [x.com](https://x.com)
   - Look for purple "🔍 Check Fact" buttons below tweets
   - Click a button to fact-check a tweet
   - Results will appear below the tweet with color-coded truth scores

5. **Open Extension Popup** (Optional)
   - Click the puzzle piece icon in Firefox toolbar
   - Click "Fact Checker" to see backend status and usage info

## Usage Tips

- **Best Results**: Works best on factual claims (science, history, statistics)
- **Limited Knowledge Base**: Currently uses 10 seed facts (see `data/seed_data.json`)
- **Relevance Filtering**: If evidence is too dissimilar, you'll see "No sufficiently relevant evidence"
- **Offline Mode**: Extension requires backend to be running locally

## Troubleshooting

### "Backend Offline" in Popup

- Check if backend is running: Open `http://127.0.0.1:8000/health` in browser
- Restart backend: Close terminal and run `run_server.bat` again
- Check CORS: Ensure `allow_origins=["*"]` in `backend/main.py`

### "Check Fact" Buttons Not Appearing

- Refresh the Twitter/X page after loading extension
- Check browser console (F12) for JavaScript errors
- Verify you're on `twitter.com` or `x.com` (not `about:debugging`)

### Extension Disappears After Firefox Restart

- Temporary extensions are removed when Firefox closes
- You need to reload via `about:debugging` after each restart
- For permanent installation, see "Publishing" section below

### Permission Errors

- Extension needs `activeTab` permission (auto-granted)
- Extension needs `http://127.0.0.1:8000/*` for API calls (auto-granted)

## File Structure

```
extension/
├── manifest.json         # Extension configuration
├── popup.html            # Extension popup UI
├── popup.js              # Popup backend status checker
├── content_script.js     # Twitter/X injection logic
├── styles.css            # UI styling
├── icon-16.png          # 16x16 icon (YOU MUST CREATE)
├── icon-48.png          # 48x48 icon (YOU MUST CREATE)
├── icon-128.png         # 128x128 icon (YOU MUST CREATE)
└── README.md            # This file
```

## Architecture

**Content Script** (`content_script.js`):

- Injects "Check Fact" buttons into Twitter/X DOM
- Uses `MutationObserver` to handle infinite scroll
- Extracts tweet text with multiple selector fallbacks
- Calls backend API at `http://127.0.0.1:8000/check`
- Displays color-coded results inline

**Popup** (`popup.html` + `popup.js`):

- Shows backend connection status
- Displays current page info
- Provides usage instructions

**Backend API** (see `backend/README.md`):

- `/check`: Verify claims with NLI + semantic search
- `/health`: Status endpoint for popup monitoring

## Publishing to Firefox Add-ons (Optional)

If you want to make this a permanent extension:

1. **Create Mozilla Developer Account**

   - Go to [addons.mozilla.org/developers](https://addons.mozilla.org/developers/)
   - Sign up (free)

2. **Prepare Extension Package**

   - Ensure all icon files exist
   - Test thoroughly with `about:debugging`
   - Create a `.zip` file of the `extension/` folder contents
   - **Important**: Zip the _contents_, not the folder itself

3. **Submit for Review**

   - Upload `.zip` to Mozilla Add-ons Developer Hub
   - Fill out listing details (name, description, screenshots)
   - Add privacy policy (required if collecting data)
   - Wait for review (usually 1-7 days)

4. **Review Requirements**
   - Must not contain minified/obfuscated code
   - Must include source code if using build tools
   - Must declare all permissions used
   - Must have clear privacy practices

**Note**: For a demo/portfolio project, temporary installation is sufficient. Publishing is only needed for public distribution.

## Demo Creation (For Portfolio)

### Screenshots

1. Open Twitter/X with extension loaded
2. Find a tweet with factual claims
3. Click "Check Fact" button
4. Capture screenshot showing:
   - Tweet content
   - Truth score (color-coded)
   - Evidence list with sources
5. Use Windows Snipping Tool (Win + Shift + S)

### Screen Recording

1. Install OBS Studio or use Windows Game Bar (Win + G)
2. Record workflow:
   - Open Twitter/X
   - Scroll to find tweet
   - Click "Check Fact"
   - Show results appearing
   - Open extension popup
   - Show backend status
3. Export as GIF (< 10MB for GitHub README)
   - Use [ezgif.com](https://ezgif.com) to convert MP4 to GIF
   - Optimize for web (reduce frame rate, resize)

### Portfolio Description

```markdown
## AI Fact Checker Browser Extension

A Firefox extension that brings AI-powered fact-checking directly into Twitter/X.
Built with FastAPI, Sentence Transformers, and Hugging Face's RoBERTa NLI model.

**Tech Stack**: Python, FastAPI, FAISS, Transformers, Firefox WebExtensions API
**Features**: Semantic search, NLI verification, real-time tweet analysis
**Demo**: [Insert GIF here]
```

## Limitations

- **Knowledge Base**: Limited to facts in `data/seed_data.json` (10 facts currently)
- **Local Only**: Requires backend running on localhost (not cloud-deployed)
- **Twitter/X Only**: Only works on twitter.com and x.com domains
- **No Persistence**: Temporary extension removed on Firefox restart
- **English Only**: Models are trained on English text

## Future Enhancements

- Add more facts to seed database
- Support for other social media platforms (Reddit, Facebook)
- User feedback mechanism (thumbs up/down)
- Claim history tracking
- Cloud deployment for always-on availability
- Multi-language support

## License

See main project LICENSE file.

## Credits

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Sentence Transformers](https://www.sbert.net/) - Semantic embeddings
- [Hugging Face Transformers](https://huggingface.co/) - NLI models
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search

---

**Version**: 0.1.0  
**Last Updated**: 2024
