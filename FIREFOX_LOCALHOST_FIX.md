# Firefox Extension Localhost Access Issue - SOLUTION

## The Problem

You're getting: **"Backend not available. Make sure the server is running on http://127.0.0.1:8000"**

Even though:

- ✅ Backend is running (`Uvicorn running on http://127.0.0.1:8000`)
- ✅ You can access http://127.0.0.1:8000 in your browser
- ✅ The manifest.json has `host_permissions: ["http://127.0.0.1:8000/*"]`

## Why This Happens

Firefox has a **security feature** that blocks extensions from accessing localhost by default, even with `host_permissions` declared. This is to prevent malicious extensions from attacking local services.

## ✅ SOLUTION: Enable Localhost Access in Firefox

### Method 1: Firefox Configuration (Recommended)

1. **Open Firefox Config Page**

   - Type `about:config` in the address bar
   - Click "Accept the Risk and Continue"

2. **Enable Extension Access to Localhost**

   - Search for: `extensions.webextensions.restrictedDomains`
   - Double-click the preference
   - Remove `localhost` and `127.0.0.1` from the list
   - **Default value**:
     ```
     accounts-static.cdn.mozilla.net,accounts.firefox.com,addons.cdn.mozilla.net,addons.mozilla.org,api.accounts.firefox.com,content.cdn.mozilla.net,discovery.addons.mozilla.org,install.mozilla.org,oauth.accounts.firefox.com,profile.accounts.firefox.com,support.mozilla.org,sync.services.mozilla.com,localhost,127.0.0.1
     ```
   - **New value** (remove localhost and 127.0.0.1):
     ```
     accounts-static.cdn.mozilla.net,accounts.firefox.com,addons.cdn.mozilla.net,addons.mozilla.org,api.accounts.firefox.com,content.cdn.mozilla.net,discovery.addons.mozilla.org,install.mozilla.org,oauth.accounts.firefox.com,profile.accounts.firefox.com,support.mozilla.org,sync.services.mozilla.com
     ```
   - Click the checkmark to save

3. **Reload the Extension**

   - Go to `about:debugging#/runtime/this-firefox`
   - Find "Fact Checker for Twitter"
   - Click "Reload"

4. **Test Again**
   - Navigate to twitter.com or x.com
   - Click "🔍 Check Fact" on a tweet
   - Should now connect successfully!

### Method 2: Alternative Approach (If Method 1 Doesn't Work)

Change the backend to listen on `0.0.0.0` instead of `127.0.0.1`:

1. **Modify the run script** (`run_server.bat`):

   ```batch
   .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Update manifest.json** to allow all local IPs:

   ```json
   "host_permissions": [
     "http://127.0.0.1:8000/*",
     "http://localhost:8000/*",
     "http://0.0.0.0:8000/*"
   ]
   ```

3. **Update API_URL in content_script.js**:
   ```javascript
   const API_URL = "http://localhost:8000/check";
   ```
   (Try `localhost` instead of `127.0.0.1`)

### Method 3: Use a Proxy (Advanced)

If you need more complex setups, you can use a proxy:

1. Install `http-server` globally:

   ```cmd
   npm install -g http-server
   ```

2. Create a proxy configuration that forwards requests
   (Not recommended for this project - too complex)

## ✅ Quick Verification

After applying Method 1, test in the browser console (F12):

```javascript
fetch("http://127.0.0.1:8000/health")
  .then((r) => r.json())
  .then((d) => console.log("Success:", d))
  .catch((e) => console.error("Failed:", e));
```

If you see `Success: {status: "ok", ...}`, it's working!

## Additional Debugging Steps

### 1. Check Browser Console

- Press **F12** on Twitter/X page
- Click "Console" tab
- Look for red error messages
- Common errors:
  - `NetworkError` → Localhost is blocked (use Method 1)
  - `CORS error` → Backend CORS misconfigured (already correct in our code)
  - `TypeError: Failed to fetch` → Backend not running or wrong URL

### 2. Check Extension Console

- Go to `about:debugging#/runtime/this-firefox`
- Find "Fact Checker for Twitter"
- Click "Inspect" button
- Look for errors in the console

### 3. Verify Backend is Really Running

Open in browser:

- http://127.0.0.1:8000 → Should show JSON with "Fact Checker API is running"
- http://127.0.0.1:8000/health → Should show `{"status":"ok",...}`
- http://127.0.0.1:8000/docs → Should show FastAPI Swagger UI

### 4. Test with curl

```cmd
curl -X POST http://127.0.0.1:8000/check -H "Content-Type: application/json" -d "{\"tweet_text\":\"Water boils at 100 degrees Celsius\"}"
```

Should return JSON with `percent_true` and `evidences`.

## Still Not Working?

### Check Windows Firewall

Windows might be blocking localhost connections:

1. Open **Windows Defender Firewall**
2. Click "Allow an app through firewall"
3. Find "Python" and ensure both Private and Public are checked
4. If not listed, click "Allow another app..." and add `python.exe`

### Check Antivirus

Some antivirus software blocks localhost requests:

- Temporarily disable antivirus
- Test if extension works
- If it does, add exception for Python/uvicorn

### Try Different Browser

Test in Chrome to see if it's a Firefox-specific issue:

1. Convert manifest.json to Chrome format (minimal changes needed)
2. Load in Chrome via `chrome://extensions/`
3. If it works in Chrome but not Firefox → It's the Firefox localhost restriction

## Summary: Most Likely Solution

**→ Use Method 1 above** (modify `about:config` to remove localhost from restricted domains)

This is the standard solution for Firefox extensions that need to access local servers.

## For Production (Future)

If you want to deploy this publicly:

1. Host backend on a real domain (e.g., Heroku, Railway, Fly.io)
2. Update `API_URL` to `https://your-domain.com/check`
3. Update `host_permissions` in manifest.json
4. No more localhost issues!

---

**Need more help?** Check the full error message in the browser console (F12) and search for the specific error on [Mozilla's extension documentation](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions).
