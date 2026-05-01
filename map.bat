@echo off
REM Open NetworkBuster Map

cd /d "%~dp0"

echo Opening Network Map...
start http://localhost:6000

call .venv\Scripts\activate.bat
start /min python network_map_viewer.py
