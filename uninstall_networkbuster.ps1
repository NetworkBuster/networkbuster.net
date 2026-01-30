#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Uninstaller
#>

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║         NetworkBuster Uninstaller                         ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Red

$confirm = Read-Host "`nAre you sure you want to uninstall NetworkBuster? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n[1/5] 🗑️  Removing Desktop shortcuts..." -ForegroundColor Yellow
Remove-Item "$env:USERPROFILE\Desktop\NetworkBuster*.lnk" -ErrorAction SilentlyContinue
Write-Host "   ✅ Desktop shortcuts removed" -ForegroundColor Green

Write-Host "`n[2/5] 🗑️  Removing Start Menu folder..." -ForegroundColor Yellow
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\NetworkBuster"
Remove-Item $StartMenuPath -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✅ Start Menu folder removed" -ForegroundColor Green

Write-Host "`n[3/5] 🗑️  Removing scheduled task..." -ForegroundColor Yellow
schtasks /Delete /TN "NetworkBuster_ScheduledLaunch" /F 2>$null
Write-Host "   ✅ Scheduled task removed" -ForegroundColor Green

Write-Host "`n[4/5] 🗑️  Removing registry keys..." -ForegroundColor Yellow
Remove-Item "HKCU:\Software\NetworkBuster" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✅ Registry keys removed" -ForegroundColor Green

Write-Host "`n[5/5] 📝 Cleanup complete" -ForegroundColor Yellow
Write-Host "   ℹ️  Project files remain in: $PSScriptRoot" -ForegroundColor Cyan
Write-Host "   ℹ️  To fully remove, delete the folder manually" -ForegroundColor Cyan

Write-Host "`n✅ NetworkBuster has been uninstalled" -ForegroundColor Green
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
