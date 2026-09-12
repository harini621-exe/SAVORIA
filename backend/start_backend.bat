@echo off
cd /d C:\Users\Harini\Desktop\SAVORIA\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > savoria_backend.log 2>&1
