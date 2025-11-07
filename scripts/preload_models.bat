@echo off
REM Pre-download AI models to avoid live downloads during demos
REM Run this once after installing requirements

echo ===============================================
echo  Pre-downloading AI Models
echo ===============================================
echo.
echo This script will download:
echo - roberta-large-mnli (NLI verifier) - ~1.4GB
echo - Optional: Mistral-7B-Instruct (LLM explainer) - ~3.5GB
echo.
echo Models will be cached in: %USERPROFILE%\.cache\huggingface
echo.

REM Set cache location
set HF_HOME=%USERPROFILE%\.cache\huggingface

REM Navigate to project root
cd /d "%~dp0.."

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate
    echo Then: pip install -r backend\requirements.txt
    pause
    exit /b 1
)

echo.
echo [1/2] Downloading roberta-large-mnli (NLI model)...
echo.
.venv\Scripts\python.exe -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Loading tokenizer...'); AutoTokenizer.from_pretrained('roberta-large-mnli'); print('Loading model...'); AutoModelForSequenceClassification.from_pretrained('roberta-large-mnli'); print('✓ NLI model downloaded')"

if errorlevel 1 (
    echo.
    echo ❌ Failed to download NLI model
    pause
    exit /b 1
)

echo.
echo ✓ NLI model downloaded successfully
echo.

REM Ask user if they want to download LLM
set /p DOWNLOAD_LLM="Download Mistral 7B LLM (~3.5GB)? This is optional. (y/n): "

if /i "%DOWNLOAD_LLM%"=="y" (
    echo.
    echo [2/2] Downloading Mistral-7B-Instruct (LLM explainer)...
    echo This may take 5-10 minutes depending on your connection...
    echo.
    
    .venv\Scripts\python.exe -c "from transformers import AutoTokenizer, AutoModelForCausalLM; print('Loading Mistral tokenizer...'); AutoTokenizer.from_pretrained('mistralai/Mistral-7B-Instruct-v0.2'); print('Loading Mistral model (this is large)...'); AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.2'); print('✓ Mistral 7B downloaded')"
    
    if errorlevel 1 (
        echo.
        echo ❌ Failed to download Mistral 7B
        echo You can skip this and use template explanations instead
    ) else (
        echo.
        echo ✓ Mistral 7B downloaded successfully
    )
) else (
    echo.
    echo Skipping Mistral 7B download. You can use template explanations.
    echo To enable LLM later, run: run_server_with_llm.bat
)

echo.
echo ===============================================
echo  All Models Downloaded!
echo ===============================================
echo.
echo Models are cached in: %HF_HOME%
echo.
echo Next steps:
echo 1. Build FAISS index: python backend\build_index.py
echo 2. Start server: run_server.bat
echo 3. Test API: curl -X POST http://127.0.0.1:8000/check -H "Content-Type: application/json" -d "{\"tweet_text\":\"test claim\"}"
echo.
pause
