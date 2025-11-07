@echo off
REM Run the Fact Checker API with LLM Explainer ENABLED
REM This will load Mistral 7B (requires ~6-7GB GPU memory)

echo ===============================================
echo  Fact Checker API - WITH LLM Explainer
echo ===============================================
echo.
echo This will enable Mistral 7B for enhanced explanations
echo Requires: 11GB+ GPU or will run slowly on CPU
echo First run downloads model (~3.5-4GB)
echo.

REM Enable LLM explainer
set ENABLE_LLM_EXPLAINER=true

REM Set Python path
set PYTHONPATH=%~dp0backend

REM Navigate to project root
cd /d "%~dp0"

echo Starting server with LLM enabled...
echo API will be available at: http://127.0.0.1:8000
echo API docs at: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run uvicorn
.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000
