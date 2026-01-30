@echo off
echo.
echo ========================================
echo  NetworkBuster Quick Installer
echo ========================================
echo.

cd /d "%~dp0"

echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\NetworkBuster.lnk'); $Shortcut.TargetPath = '%CD%\.venv\Scripts\pythonw.exe'; $Shortcut.Arguments = '\"%CD%\networkbuster_app.pyw\"'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'NetworkBuster Control Panel'; $Shortcut.IconLocation = 'imageres.dll,1'; $Shortcut.Save()"

echo Creating Start Menu shortcut...
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\NetworkBuster.lnk'); $Shortcut.TargetPath = '%CD%\.venv\Scripts\pythonw.exe'; $Shortcut.Arguments = '\"%CD%\networkbuster_app.pyw\"'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'NetworkBuster Control Panel'; $Shortcut.IconLocation = 'imageres.dll,1'; $Shortcut.Save()"

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo   Desktop: NetworkBuster shortcut
echo   Start Menu: NetworkBuster
echo   Search: Type "NetworkBuster"
echo.
echo Launching NetworkBuster...
echo.

start "" "%CD%\.venv\Scripts\pythonw.exe" "%CD%\networkbuster_app.pyw"

timeout /t 2 >nul
