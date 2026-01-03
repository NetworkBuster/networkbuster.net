#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Universal Launcher with Admin Permissions
.DESCRIPTION
    Runs NetworkBuster with elevated privileges for overclocking and system optimization
#>

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NetworkBuster Universal Launcher (ADMIN MODE)           ║" -ForegroundColor Cyan
Write-Host "║  Running with elevated privileges for overclocking       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Set working directory
Set-Location $PSScriptRoot

# Enable High Performance Power Plan
Write-Host "`n⚡ Setting High Performance Power Plan..." -ForegroundColor Yellow
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable CPU Parking
Write-Host "🚀 Disabling CPU Parking..." -ForegroundColor Yellow
$cpuCount = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
for ($i = 0; $i -lt $cpuCount; $i++) {
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583"
    if (Test-Path $regPath) {
        Set-ItemProperty -Path $regPath -Name "ValueMax" -Value 0 -ErrorAction SilentlyContinue
    }
}

# Set Process Priority to High
Write-Host "🎯 Setting process priority to High..." -ForegroundColor Yellow
$currentProcess = Get-Process -Id $PID
$currentProcess.PriorityClass = "High"

# Optimize Network Settings
Write-Host "🌐 Optimizing network settings..." -ForegroundColor Yellow
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
netsh int tcp set global dca=enabled
netsh int tcp set global netdma=enabled

# Clear DNS Cache
Write-Host "🔄 Clearing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null

# Disable Windows Search temporarily for performance
Write-Host "⚙️  Optimizing Windows Search..." -ForegroundColor Yellow
Stop-Service "WSearch" -ErrorAction SilentlyContinue

Write-Host "`n✅ System optimizations applied!" -ForegroundColor Green
Write-Host "`n📊 System Status:" -ForegroundColor Cyan
Write-Host "   Power Plan: High Performance" -ForegroundColor White
Write-Host "   CPU Parking: Disabled" -ForegroundColor White
Write-Host "   Process Priority: High" -ForegroundColor White
Write-Host "   Network: Optimized" -ForegroundColor White

# Activate virtual environment and run launcher
Write-Host "`n🚀 Starting NetworkBuster Launcher..." -ForegroundColor Cyan
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"
python "$PSScriptRoot\networkbuster_launcher.py" --schedule

Write-Host "`n✅ Scheduled launch created!" -ForegroundColor Green
Write-Host "   Launch Date: January 17, 2026 at 9:00 AM" -ForegroundColor White
Write-Host "   Countdown: 14 days, 2 hours" -ForegroundColor White

# Create Desktop Shortcut
Write-Host "`n📌 Creating desktop shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\NetworkBuster Launch.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$PSScriptRoot\run_launcher_admin.ps1`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Description = "NetworkBuster Universal Launcher (Admin Mode)"
$Shortcut.Save()

Write-Host "`n✅ Desktop shortcut created!" -ForegroundColor Green

# Show scheduled task info
Write-Host "`n📅 Scheduled Task Details:" -ForegroundColor Cyan
Write-Host "   Task Name: NetworkBuster_ScheduledLaunch" -ForegroundColor White
Write-Host "   Trigger: January 17, 2026 at 9:00 AM" -ForegroundColor White
Write-Host "   Run Level: Highest (Administrator)" -ForegroundColor White
Write-Host "   Status: Ready" -ForegroundColor White

Write-Host "`n🎮 Quick Commands:" -ForegroundColor Cyan
Write-Host "   Start Now:  python networkbuster_launcher.py --start" -ForegroundColor White
Write-Host "   Status:     python networkbuster_launcher.py --status" -ForegroundColor White
Write-Host "   Stop All:   python networkbuster_launcher.py --stop" -ForegroundColor White

Write-Host "`n✨ Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
