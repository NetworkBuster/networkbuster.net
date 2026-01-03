@echo off
REM Stop all NetworkBuster services

cd /d "%~dp0"

echo.
echo Stopping NetworkBuster services...
echo.

call .venv\Scripts\activate.bat
python networkbuster_launcher.py --stop

echo.
echo All services stopped.
pause
