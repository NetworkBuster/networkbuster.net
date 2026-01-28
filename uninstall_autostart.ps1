#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Uninstall NetworkBuster Auto-Start
#>

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║  NetworkBuster Auto-Start Uninstaller                     ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Red

$confirm = Read-Host "`nRemove auto-start? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`n[1/3] Removing scheduled task..." -ForegroundColor Yellow
schtasks /Delete /TN "NetworkBuster_AutoStart" /F 2>$null
Write-Host "   ✅ Task removed" -ForegroundColor Green

Write-Host "`n[2/3] Removing startup shortcut..." -ForegroundColor Yellow
$startupFolder = [Environment]::GetFolderPath("Startup")
Remove-Item "$startupFolder\NetworkBuster.lnk" -ErrorAction SilentlyContinue
Write-Host "   ✅ Shortcut removed" -ForegroundColor Green

Write-Host "`n[3/3] Cleaning up files..." -ForegroundColor Yellow
Remove-Item "$PSScriptRoot\startup_service.bat" -ErrorAction SilentlyContinue
Remove-Item "$PSScriptRoot\autostart_task.xml" -ErrorAction SilentlyContinue
Write-Host "   ✅ Files cleaned" -ForegroundColor Green

Write-Host "`n✅ Auto-start removed successfully!" -ForegroundColor Green
Write-Host "   NetworkBuster will no longer start automatically" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
