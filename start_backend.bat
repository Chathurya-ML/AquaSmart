@echo off
cd Code\backend
set USE_AWS=false
set FALLBACK_ENABLED=true
venv\Scripts\python.exe app.py
