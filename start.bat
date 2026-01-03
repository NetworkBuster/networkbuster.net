@echo off
REM NetworkBuster Quick Launch - Auto-permissions
REM Requests admin if needed, then starts everything

cd /d "%~dp0"

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator permissions...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ==========================================
echo   NetworkBuster Quick Launch
echo ==========================================
echo.
echo Starting all services with admin privileges...
echo.

call .venv\Scripts\activate.bat
start /min python auto_start_service.py

echo.
echo Services starting in background...
timeout /t 3 /nobreak >nul

echo Opening dashboards...
start http://localhost:7000

echo.
echo Done! All services running.
echo Close this window anytime.
pause
