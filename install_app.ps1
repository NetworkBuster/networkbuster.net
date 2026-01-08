#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Application Installer
.DESCRIPTION
    Installs NetworkBuster as a Windows application with shortcuts, Start Menu entry, and system integration
#>

param(
    [switch]$Uninstall
)

$AppName = "NetworkBuster"
$AppVersion = "1.0.0"
$InstallPath = $PSScriptRoot
$StartMenuPath = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\$AppName"
$DesktopPath = "$env:PUBLIC\Desktop"

function Write-Header {
    param([string]$Text)
    Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Text" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Install-Application {
    Write-Header "NetworkBuster Application Installer v$AppVersion"
    
    Write-Host "`n📦 Installing NetworkBuster..." -ForegroundColor Yellow
    Write-Host "   Install Path: $InstallPath" -ForegroundColor Gray
    
    # Create Start Menu folder
    Write-Host "`n📁 Creating Start Menu entries..." -ForegroundColor Yellow
    if (-not (Test-Path $StartMenuPath)) {
        New-Item -Path $StartMenuPath -ItemType Directory -Force | Out-Null
    }
    
    # Create shortcuts
    $WshShell = New-Object -ComObject WScript.Shell
    
    # 1. Main Launcher Shortcut
    Write-Host "   Creating: NetworkBuster Launcher" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\NetworkBuster Launcher.lnk")
    $Shortcut.TargetPath = "$InstallPath\.venv\Scripts\pythonw.exe"
    $Shortcut.Arguments = "`"$InstallPath\networkbuster_launcher.py`""
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "NetworkBuster All-in-One Launcher"
    $Shortcut.IconLocation = "imageres.dll,1"
    $Shortcut.Save()
    
    # 2. Admin Launcher Shortcut
    Write-Host "   Creating: NetworkBuster (Admin Mode)" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\NetworkBuster (Admin Mode).lnk")
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallPath\run_launcher_admin.ps1`""
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "NetworkBuster with Administrator privileges"
    $Shortcut.IconLocation = "imageres.dll,73"
    $Shortcut.Save()
    
    # 3. Start Services Shortcut
    Write-Host "   Creating: Start All Services" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\Start All Services.lnk")
    $Shortcut.TargetPath = "$InstallPath\.venv\Scripts\python.exe"
    $Shortcut.Arguments = "`"$InstallPath\networkbuster_launcher.py`" --start"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Start all NetworkBuster services"
    $Shortcut.IconLocation = "shell32.dll,137"
    $Shortcut.Save()
    
    # 4. Status Monitor Shortcut
    Write-Host "   Creating: Status Monitor" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\Status Monitor.lnk")
    $Shortcut.TargetPath = "$InstallPath\.venv\Scripts\python.exe"
    $Shortcut.Arguments = "`"$InstallPath\networkbuster_launcher.py`" --status"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Check NetworkBuster service status"
    $Shortcut.IconLocation = "shell32.dll,16"
    $Shortcut.Save()
    
    # 5. Mission Control Shortcut
    Write-Host "   Creating: Mission Control Dashboard" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\Mission Control Dashboard.lnk")
    $Shortcut.TargetPath = "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
    $Shortcut.Arguments = "--new-window http://localhost:5000"
    $Shortcut.Description = "Open Mission Control Dashboard"
    $Shortcut.IconLocation = "shell32.dll,43"
    $Shortcut.Save()
    
    # 6. API Tracer Shortcut
    Write-Host "   Creating: API Tracer" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\API Tracer.lnk")
    $Shortcut.TargetPath = "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
    $Shortcut.Arguments = "--new-window http://localhost:8000"
    $Shortcut.Description = "Open API Tracer Dashboard"
    $Shortcut.IconLocation = "shell32.dll,21"
    $Shortcut.Save()
    
    # 7. Uninstaller Shortcut
    Write-Host "   Creating: Uninstaller" -ForegroundColor Gray
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\Uninstall NetworkBuster.lnk")
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallPath\install_app.ps1`" -Uninstall"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Uninstall NetworkBuster"
    $Shortcut.IconLocation = "shell32.dll,131"
    $Shortcut.Save()
    
    # Create Desktop Shortcut
    Write-Host "`n🖥️  Creating desktop shortcut..." -ForegroundColor Yellow
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\NetworkBuster.lnk")
    $Shortcut.TargetPath = "$InstallPath\.venv\Scripts\pythonw.exe"
    $Shortcut.Arguments = "`"$InstallPath\networkbuster_launcher.py`""
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "NetworkBuster All-in-One Launcher"
    $Shortcut.IconLocation = "imageres.dll,1"
    $Shortcut.Save()
    
    # Add to Windows Registry
    Write-Host "`n📝 Registering application..." -ForegroundColor Yellow
    $RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$AppName"
    
    if (-not (Test-Path $RegPath)) {
        New-Item -Path $RegPath -Force | Out-Null
    }
    
    Set-ItemProperty -Path $RegPath -Name "DisplayName" -Value $AppName
    Set-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value $AppVersion
    Set-ItemProperty -Path $RegPath -Name "Publisher" -Value "NetworkBuster Team"
    Set-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallPath
    Set-ItemProperty -Path $RegPath -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `"$InstallPath\install_app.ps1`" -Uninstall"
    Set-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value "imageres.dll,1"
    Set-ItemProperty -Path $RegPath -Name "NoModify" -Value 1
    Set-ItemProperty -Path $RegPath -Name "NoRepair" -Value 1
    
    # Create scheduled task for launch
    Write-Host "`n⏰ Creating scheduled task..." -ForegroundColor Yellow
    & "$InstallPath\.venv\Scripts\python.exe" "$InstallPath\networkbuster_launcher.py" --schedule
    
    # Firewall rules
    Write-Host "`n🔥 Configuring firewall rules..." -ForegroundColor Yellow
    $ports = @(3000, 3001, 3002, 4000, 5000, 6000, 7000, 8000)
    foreach ($port in $ports) {
        $ruleName = "NetworkBuster Port $port"
        $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        
        if (-not $existing) {
            New-NetFirewallRule -DisplayName $ruleName `
                -Direction Inbound `
                -Action Allow `
                -Protocol TCP `
                -LocalPort $port `
                -Profile Any `
                -Description "NetworkBuster service port" | Out-Null
            Write-Host "   ✅ Port $port allowed" -ForegroundColor Green
        } else {
            Write-Host "   ℹ️  Port $port already configured" -ForegroundColor Gray
        }
    }
    
    # Create uninstall script
    Write-Host "`n📄 Creating uninstall script..." -ForegroundColor Yellow
    $uninstallScript = @"
# NetworkBuster Uninstaller
Write-Host "Uninstalling NetworkBuster..." -ForegroundColor Yellow
Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$StartMenuPath" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$DesktopPath\NetworkBuster.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$RegPath" -Recurse -Force -ErrorAction SilentlyContinue
schtasks /Delete /TN "NetworkBuster_ScheduledLaunch" /F 2>`$null
Write-Host "NetworkBuster uninstalled successfully!" -ForegroundColor Green
"@
    $uninstallScript | Out-File "$InstallPath\uninstall.ps1" -Encoding UTF8
    
    # Installation complete
    Write-Host "`n" -ForegroundColor Green
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ INSTALLATION COMPLETE!                                ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
    Write-Host "`n📊 Installation Summary:" -ForegroundColor Cyan
    Write-Host "   ✅ Start Menu entries created" -ForegroundColor Green
    Write-Host "   ✅ Desktop shortcut created" -ForegroundColor Green
    Write-Host "   ✅ Application registered in Windows" -ForegroundColor Green
    Write-Host "   ✅ Scheduled task created (Jan 17, 2026)" -ForegroundColor Green
    Write-Host "   ✅ Firewall rules configured (ports 3000-8000)" -ForegroundColor Green
    Write-Host "   ✅ Uninstaller created" -ForegroundColor Green
    
    Write-Host "`n🚀 How to Launch:" -ForegroundColor Cyan
    Write-Host "   • Start Menu → NetworkBuster" -ForegroundColor White
    Write-Host "   • Desktop → NetworkBuster icon" -ForegroundColor White
    Write-Host "   • Search → 'NetworkBuster'" -ForegroundColor White
    
    Write-Host "`n📅 Scheduled Launch:" -ForegroundColor Cyan
    Write-Host "   Date: January 17, 2026 at 9:00 AM" -ForegroundColor White
    Write-Host "   Countdown: 14 days" -ForegroundColor White
    
    Write-Host "`n🌐 Quick Access URLs:" -ForegroundColor Cyan
    Write-Host "   Mission Control:  http://localhost:5000" -ForegroundColor White
    Write-Host "   API Tracer:       http://localhost:8000" -ForegroundColor White
    Write-Host "   Universal Launch: http://localhost:7000" -ForegroundColor White
    
    Write-Host "`n"
}

function Uninstall-Application {
    Write-Header "NetworkBuster Application Uninstaller"
    
    Write-Host "`n🛑 Uninstalling NetworkBuster..." -ForegroundColor Yellow
    
    # Stop all processes
    Write-Host "`n   Stopping services..." -ForegroundColor Gray
    Stop-Process -Name python,node,pythonw -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Remove Start Menu folder
    Write-Host "   Removing Start Menu entries..." -ForegroundColor Gray
    Remove-Item -Path $StartMenuPath -Recurse -Force -ErrorAction SilentlyContinue
    
    # Remove Desktop shortcut
    Write-Host "   Removing desktop shortcut..." -ForegroundColor Gray
    Remove-Item -Path "$DesktopPath\NetworkBuster.lnk" -Force -ErrorAction SilentlyContinue
    
    # Remove Registry entries
    Write-Host "   Removing registry entries..." -ForegroundColor Gray
    $RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$AppName"
    Remove-Item -Path $RegPath -Recurse -Force -ErrorAction SilentlyContinue
    
    # Remove scheduled task
    Write-Host "   Removing scheduled task..." -ForegroundColor Gray
    schtasks /Delete /TN "NetworkBuster_ScheduledLaunch" /F 2>$null | Out-Null
    
    # Remove firewall rules (optional)
    Write-Host "   Removing firewall rules..." -ForegroundColor Gray
    $ports = @(3000, 3001, 3002, 4000, 5000, 6000, 7000, 8000)
    foreach ($port in $ports) {
        Remove-NetFirewallRule -DisplayName "NetworkBuster Port $port" -ErrorAction SilentlyContinue
    }
    
    Write-Host "`n✅ NetworkBuster has been uninstalled successfully!" -ForegroundColor Green
    Write-Host "   Note: Source files in $InstallPath were preserved" -ForegroundColor Gray
    Write-Host "`n"
}

# Main execution
if ($Uninstall) {
    Uninstall-Application
} else {
    Install-Application
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
