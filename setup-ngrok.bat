@echo off
REM Quick ngrok setup for NetworkBuster
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  NetworkBuster - Quick ngrok Setup                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check if ngrok auth is configured
echo [1/5] Checking ngrok authentication...
ngrok.exe config check >nul 2>&1
if errorlevel 1 (
    echo ⚠️  ngrok not authenticated yet!
    echo.
    echo 📋 To authenticate:
    echo    1. Visit: https://dashboard.ngrok.com/get-started/your-authtoken
    echo    2. Copy your authtoken
    echo    3. Run: ngrok.exe config add-authtoken YOUR_TOKEN
    echo.
    echo Press any key to open ngrok dashboard in browser...
    pause >nul
    start https://dashboard.ngrok.com/get-started/your-authtoken
    echo.
    echo After getting your token, run this command:
    echo ngrok.exe config add-authtoken YOUR_TOKEN
    echo.
    echo Then run this script again!
    pause
    exit
)

echo ✅ ngrok is authenticated!
echo.

REM Start NetworkBuster AI
echo [2/5] Starting NetworkBuster AI on port 8000...
start "NetworkBuster AI" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python networkbuster_ai.py"
timeout /t 5 >nul

REM Start Network Map Viewer
echo [3/5] Starting Network Map Viewer on port 8080...
start "Network Map" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python network_map_viewer.py"
timeout /t 5 >nul

REM Start ngrok tunnel for Network Map
echo [4/5] Starting ngrok tunnel for Network Map (port 8080)...
start "ngrok - Network Map" cmd /k "cd /d %~dp0 && ngrok.exe http 8080 --region us"
timeout /t 3 >nul

REM Start ngrok tunnel for NetworkBuster AI
echo [5/5] Starting ngrok tunnel for NetworkBuster AI (port 8000)...
start "ngrok - AI Dashboard" cmd /k "cd /d %~dp0 && ngrok.exe http 8000 --region us"
timeout /t 3 >nul

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ All services started successfully!                   ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 📍 Local Access:
echo    Network Map: http://localhost:8080
echo    AI Dashboard: http://localhost:8000
echo.
echo 🌐 Remote Access:
echo    Check the ngrok windows for public URLs
echo    They look like: https://abc-123-def.ngrok-free.app
echo.
echo 💡 Tip: Copy the ngrok URLs and share them for remote access!
echo.
pause
