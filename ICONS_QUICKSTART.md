# Quick Start: Icon Files

You need 3 icon files before loading the extension. Here's the fastest way to create them:

## 🚀 Fastest Method (5 minutes)

### Option 1: AI Icon Generator

1. Go to [favicon.io/favicon-generator/](https://favicon.io/favicon-generator/)
2. Settings:
   - Text: `✓` or `🔍`
   - Background: Gradient (Purple to Blue)
   - Font: Bold, 80 size
3. Click "Download"
4. Extract ZIP file
5. Rename files:
   - `favicon-16x16.png` → `icon-16.png`
   - `favicon-32x32.png` → (delete, not needed)
   - `android-chrome-192x192.png` → (delete, not needed)
6. Create `icon-48.png` and `icon-128.png`:
   - Go to [iloveimg.com/resize-image](https://iloveimg.com/resize-image)
   - Upload `android-chrome-192x192.png`
   - Resize to 48x48, download as `icon-48.png`
   - Resize to 128x128, download as `icon-128.png`
7. Move all 3 files to `extension/` folder

### Option 2: Use Free Icon (3 minutes)

1. Go to [flaticon.com](https://flaticon.com)
2. Search "fact check" or "verify"
3. Download any icon as PNG (free account)
4. Go to [iloveimg.com/resize-image](https://iloveimg.com/resize-image)
5. Upload downloaded icon
6. Create 3 versions:
   - Resize to 16x16 → Save as `icon-16.png`
   - Resize to 48x48 → Save as `icon-48.png`
   - Resize to 128x128 → Save as `icon-128.png`
7. Move files to `extension/` folder

### Option 3: Simple Colored Square (1 minute)

If you just want to test the extension first:

1. Go to [dummyimage.com](https://dummyimage.com)
2. Create 3 images:
   - [dummyimage.com/16x16/764ba2/fff.png&text=✓](https://dummyimage.com/16x16/764ba2/fff.png&text=✓) → Save as `icon-16.png`
   - [dummyimage.com/48x48/764ba2/fff.png&text=✓](https://dummyimage.com/48x48/764ba2/fff.png&text=✓) → Save as `icon-48.png`
   - [dummyimage.com/128x128/764ba2/fff.png&text=✓](https://dummyimage.com/128x128/764ba2/fff.png&text=✓) → Save as `icon-128.png`
3. Move files to `extension/` folder

## ✅ Verify Icons Are Ready

Open Command Prompt:

```cmd
cd C:\Users\youss\Important\Projects\Fact-Checking-Extension\extension
dir icon-*.png
```

You should see:

```
icon-16.png
icon-48.png
icon-128.png
```

## 🎯 Next Step

Once icons are ready:

1. Start backend: `run_server.bat`
2. Open Firefox
3. Go to `about:debugging#/runtime/this-firefox`
4. Click "Load Temporary Add-on..."
5. Select `extension/manifest.json`

See `MANUAL_STEPS.md` for detailed testing instructions.
