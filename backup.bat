@echo off
REM Quick Git Backup

cd /d "%~dp0"

echo Backing up to D: and K: drives...

call .venv\Scripts\activate.bat
python flash_git_backup.py

pause
