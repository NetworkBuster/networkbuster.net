@echo off
REM NetworkBuster - Quick Start with ngrok Tunnel
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  NetworkBuster Remote Access - Quick Start              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Start NetworkBuster AI (Port 8000)
echo [1/4] Starting NetworkBuster AI on port 8000...
start "NetworkBuster AI" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python networkbuster_ai.py"
timeout /t 3 >nul

REM Start Network Map Viewer (Port 8080)
echo [2/4] Starting Network Map Viewer on port 8080...
start "Network Map" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python network_map_viewer.py"
timeout /t 3 >nul

REM Check if ngrok exists
if not exist "%~dp0ngrok.exe" (
    echo.
    echo ⚠️  ngrok.exe not found!
    echo.
    echo Download ngrok:
    echo    1. Visit: https://ngrok.com/download
    echo    2. Download Windows 64-bit
    echo    3. Extract ngrok.exe to: %~dp0
    echo    4. Sign up and get auth token: https://dashboard.ngrok.com
    echo    5. Run: ngrok authtoken YOUR_TOKEN
    echo.
    echo Skipping tunnel setup...
    goto :end
)

REM Start ngrok tunnel for Network Map
echo [3/4] Starting ngrok tunnel for Network Map (port 8080)...
start "ngrok - Network Map" cmd /k "cd /d %~dp0 && ngrok.exe http 8080 --region us"
timeout /t 2 >nul

REM Start ngrok tunnel for NetworkBuster AI
echo [4/4] Starting ngrok tunnel for NetworkBuster AI (port 8000)...
start "ngrok - AI Dashboard" cmd /k "cd /d %~dp0 && ngrok.exe http 8000 --region us"
timeout /t 2 >nul

:end
echo.
echo ✅ NetworkBuster services started!
echo.
echo 📍 Local Access:
echo    Network Map: http://localhost:8080
echo    AI Dashboard: http://localhost:8000
echo.
echo 🌐 Remote Access (ngrok):
echo    Check the ngrok windows for public URLs
echo    URLs look like: https://abc123.ngrok-free.app
echo.
echo 📖 Full guide: REMOTE-ACCESS-GUIDE.md
echo.
pause
