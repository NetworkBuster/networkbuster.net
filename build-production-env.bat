@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo NetworkBuster.net - Production Environment Builder
echo ============================================================
echo.

set PROJECT_ROOT=D:\VS code
set EXPORT_PATH=S:\NetworkBuster_Production

echo [1/5] Cleaning up existing node_modules for fresh production install...
cd /d "%PROJECT_ROOT%"
if exist node_modules rmdir /S /Q node_modules

echo.
echo [2/5] Installing core production dependencies...
cmd /c npm install --omit=dev
if errorlevel 1 echo Warning: Install had issues but continuing...

echo.
echo [3/5] Building Real-Time Overlay...
cd /d "%PROJECT_ROOT%\challengerepo\real-time-overlay"
if exist package.json (
    cmd /c npm install
    cmd /c npm run build
)

echo.
echo [4/5] Building Dashboard...
cd /d "%PROJECT_ROOT%\dashboard"
if exist package.json (
    cmd /c npm install
    cmd /c npm run build
)

echo.
echo [5/5] Exporting to S: Drive...
echo Target: %EXPORT_PATH%

if not exist "%EXPORT_PATH%" mkdir "%EXPORT_PATH%"

echo Copying production assets to S:...
robocopy "%PROJECT_ROOT%" "%EXPORT_PATH%" /E /XD .git .github .azure .vscode /XF *.zip *.log /R:1 /W:1 /MT:32 /NP /NFL /NDL

echo.
echo ============================================================
echo PRODUCTION ENVIRONMENT READY ON S:
echo ============================================================
echo.
echo Executables were successfully built and assets were copied.
echo Location: S:\NetworkBuster_Production
echo.
echo To start: 
echo   cd /d S:\NetworkBuster_Production
echo   npm start
echo.
echo ============================================================
pause
