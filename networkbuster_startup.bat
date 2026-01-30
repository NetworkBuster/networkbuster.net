@echo off
echo ========================================
echo NetworkBuster All-in-One Launcher
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Launch NetworkBuster
python networkbuster_launcher.py --start

echo.
echo Press any key to exit...
pause > nul
