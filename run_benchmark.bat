@echo off
cd Code\backend
start "Backend" python -m uvicorn app:app --host 0.0.0.0 --port 8000
timeout /t 10 /nobreak
cd ..\..
python benchmark_test.py
pause
