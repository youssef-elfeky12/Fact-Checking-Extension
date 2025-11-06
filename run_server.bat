@echo off
set PYTHONPATH=%~dp0backend
"%~dp0.venv\Scripts\uvicorn.exe" backend.main:app --host 127.0.0.1 --port 8000
