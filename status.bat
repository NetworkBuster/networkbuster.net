@echo off
REM Show NetworkBuster status

cd /d "%~dp0"

call .venv\Scripts\activate.bat
python networkbuster_launcher.py --status

pause
