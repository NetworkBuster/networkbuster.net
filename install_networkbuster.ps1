#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Application Installer
.DESCRIPTION
    Complete installation with desktop shortcuts and Start Menu integration
#>

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         NetworkBuster Application Installer               ║" -ForegroundColor Cyan
Write-Host "║         Version 1.0.1 - Production Ready                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$InstallDir = $PSScriptRoot
Set-Location $InstallDir

Write-Host "`n[1/7] 🔍 Checking Python environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "   ✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "   ❌ Virtual environment not found!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/7] 📦 Building NetworkBuster package..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
& ".venv\Scripts\pip.exe" install --upgrade pip setuptools wheel
& ".venv\Scripts\pip.exe" install -e .

Write-Host "`n[3/7] 🎨 Creating application icon..." -ForegroundColor Yellow
$IconPath = Join-Path $InstallDir "networkbuster.ico"

# Create simple ICO file (placeholder - you can replace with real icon)
Add-Type -AssemblyName System.Drawing
$bitmap = New-Object System.Drawing.Bitmap(64, 64)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::Black)
$graphics.FillEllipse([System.Drawing.Brushes]::Lime, 10, 10, 44, 44)
$graphics.DrawString("NB", (New-Object System.Drawing.Font("Arial", 16, [System.Drawing.FontStyle]::Bold)), [System.Drawing.Brushes]::Black, 16, 20)

# Save as icon
$iconStream = New-Object System.IO.MemoryStream
$bitmap.Save($iconStream, [System.Drawing.Imaging.ImageFormat]::Png)
$iconBytes = $iconStream.ToArray()
[System.IO.File]::WriteAllBytes($IconPath, $iconBytes)

$graphics.Dispose()
$bitmap.Dispose()
$iconStream.Dispose()

Write-Host "   ✅ Icon created at $IconPath" -ForegroundColor Green

Write-Host "`n[4/7] 📌 Creating Desktop shortcuts..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell

# Main launcher shortcut
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\NetworkBuster.lnk")
$Shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
$Shortcut.Arguments = "`"$InstallDir\networkbuster_launcher.py`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $IconPath
$Shortcut.Description = "NetworkBuster - Network Management Suite"
$Shortcut.Save()
Write-Host "   ✅ Desktop: NetworkBuster.lnk" -ForegroundColor Green

# Network Map shortcut
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\NetworkBuster Map.lnk")
$Shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
$Shortcut.Arguments = "`"$InstallDir\network_map_viewer.py`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $IconPath
$Shortcut.Description = "NetworkBuster - Network Topology Map"
$Shortcut.Save()
Write-Host "   ✅ Desktop: NetworkBuster Map.lnk" -ForegroundColor Green

# API Tracer shortcut
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\NetworkBuster API Tracer.lnk")
$Shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
$Shortcut.Arguments = "`"$InstallDir\api_tracer.py`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $IconPath
$Shortcut.Description = "NetworkBuster - API Endpoint Tracer"
$Shortcut.Save()
Write-Host "   ✅ Desktop: NetworkBuster API Tracer.lnk" -ForegroundColor Green

Write-Host "`n[5/7] 📂 Creating Start Menu folder..." -ForegroundColor Yellow
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\NetworkBuster"
New-Item -ItemType Directory -Force -Path $StartMenuPath | Out-Null

# Start Menu shortcuts
$shortcuts = @(
    @{Name="NetworkBuster Launcher"; Script="networkbuster_launcher.py"; Desc="Main application launcher"},
    @{Name="Network Map Viewer"; Script="network_map_viewer.py"; Desc="Interactive network topology map"},
    @{Name="API Tracer"; Script="api_tracer.py"; Desc="API endpoint monitoring"},
    @{Name="Mission Control"; Script="nasa_home_base.py"; Desc="Mission control dashboard"},
    @{Name="Universal Launcher"; Script="universal_launcher.py"; Desc="Universal service launcher"},
    @{Name="Git Cloud Shortcuts"; Script="git_cloud_shortcuts.py"; Desc="Git repository shortcuts"},
    @{Name="Flash Git Backup"; Script="flash_git_backup.py"; Desc="Quick git backup tool"}
)

foreach ($item in $shortcuts) {
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\$($item.Name).lnk")
    $Shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
    $Shortcut.Arguments = "`"$InstallDir\$($item.Script)`""
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = $IconPath
    $Shortcut.Description = $item.Desc
    $Shortcut.Save()
    Write-Host "   ✅ Start Menu: $($item.Name)" -ForegroundColor Green
}

# Uninstaller
$Shortcut = $WshShell.CreateShortcut("$StartMenuPath\Uninstall NetworkBuster.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallDir\uninstall_networkbuster.ps1`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Uninstall NetworkBuster"
$Shortcut.Save()
Write-Host "   ✅ Start Menu: Uninstall NetworkBuster" -ForegroundColor Green

Write-Host "`n[6/7] ⚙️  Creating scheduled task..." -ForegroundColor Yellow
& ".venv\Scripts\python.exe" networkbuster_launcher.py --schedule

Write-Host "`n[7/7] 📝 Registering application..." -ForegroundColor Yellow
$RegPath = "HKCU:\Software\NetworkBuster"
New-Item -Path $RegPath -Force | Out-Null
Set-ItemProperty -Path $RegPath -Name "InstallPath" -Value $InstallDir
Set-ItemProperty -Path $RegPath -Name "Version" -Value "1.0.1"
Set-ItemProperty -Path $RegPath -Name "InstallDate" -Value (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Write-Host "   ✅ Registry keys created" -ForegroundColor Green

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ INSTALLATION COMPLETE!                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📦 Installed Components:" -ForegroundColor Cyan
Write-Host "   • NetworkBuster package (pip installable)" -ForegroundColor White
Write-Host "   • 3 Desktop shortcuts" -ForegroundColor White
Write-Host "   • 8 Start Menu shortcuts" -ForegroundColor White
Write-Host "   • Scheduled task (January 17, 2026)" -ForegroundColor White
Write-Host "   • Registry integration" -ForegroundColor White

Write-Host "`n🎯 Quick Access:" -ForegroundColor Cyan
Write-Host "   Desktop:    NetworkBuster.lnk" -ForegroundColor White
Write-Host "   Start Menu: Programs > NetworkBuster" -ForegroundColor White
Write-Host "   Command:    networkbuster" -ForegroundColor White

Write-Host "`n🚀 Launch Options:" -ForegroundColor Cyan
Write-Host "   1. Double-click desktop icon" -ForegroundColor White
Write-Host "   2. Start Menu > NetworkBuster" -ForegroundColor White
Write-Host "   3. Command: python networkbuster_launcher.py --start" -ForegroundColor White

Write-Host "`n⏰ Scheduled Launch:" -ForegroundColor Cyan
Write-Host "   Date: January 17, 2026 at 9:00 AM" -ForegroundColor White
Write-Host "   Task: NetworkBuster_ScheduledLaunch" -ForegroundColor White

Write-Host "`n✨ Press any key to launch NetworkBuster Map..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Launch network map to show the new navigation
Start-Process "$InstallDir\.venv\Scripts\python.exe" -ArgumentList "`"$InstallDir\network_map_viewer.py`"" -WorkingDirectory $InstallDir

Write-Host "`n✅ NetworkBuster Map launched with enhanced navigation!" -ForegroundColor Green
Write-Host "   Use the navigation buttons to explore the topology" -ForegroundColor White
