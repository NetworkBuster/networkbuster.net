@echo off
REM NetworkBuster One-Click Auto-Start
REM Automatically requests permissions and starts everything

cd /d "%~dp0"

echo.
echo ==========================================
echo   NetworkBuster One-Click Launcher
echo ==========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator permissions...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Running with administrator privileges...
echo.
echo Starting all services...
echo.

call .venv\Scripts\activate.bat
python auto_start_service.py

echo.
echo All services started!
echo Window will close in 3 seconds...
timeout /t 3 /nobreak >nul
