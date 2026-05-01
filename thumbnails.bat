@echo off
REM Extract network thumbnails

cd /d "%~dp0"

echo Extracting thumbnails...

call .venv\Scripts\activate.bat
python extract_thumbnails.py

echo.
echo Opening gallery...
start network_thumbnails\index.html

pause
