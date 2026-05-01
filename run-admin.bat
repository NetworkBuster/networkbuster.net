@echo off
title NetworkBuster - Run as Admin
echo.
echo ========================================
echo   NetworkBuster Admin Launcher
echo ========================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running as Administrator
) else (
    echo [!] Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo.
echo Select an option:
echo   1. Launch Everything (recommended)
echo   2. Quick Admin Menu
echo   3. System Health Check
echo   4. Service Manager
echo   5. Start Servers Only
echo   6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" python launch.py
if "%choice%"=="2" python quick_admin.py
if "%choice%"=="3" python system_health.py
if "%choice%"=="4" python service_manager.py
if "%choice%"=="5" node start-servers.js
if "%choice%"=="6" exit

pause
