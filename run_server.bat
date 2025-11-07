@echo off
REM Fact Checker API - Standard mode (template explanations)
set PYTHONPATH=%~dp0backend
set HF_HOME=%USERPROFILE%\.cache\huggingface
"%~dp0.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
