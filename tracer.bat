@echo off
REM Open API Tracer

cd /d "%~dp0"

echo Opening API Tracer...
start http://localhost:8000

call .venv\Scripts\activate.bat
start /min python api_tracer.py
