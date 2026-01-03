# set_k_permissions.ps1
# Usage: Run in an elevated Administrator PowerShell session.
# This script:
#  - Backs up K:\ ACLs
#  - Grants Everyone Read & Execute on K:\
#  - Hides and secures "K:\service - Shortcut.lnk" (grants Full control to specified account)
#  - Adds preciseliens@gmail.com to the local Administrators group
#  - Provides a simple rollback function

param(
    [string]$KPath = "K:\",
    [string]$File = "K:\service - Shortcut.lnk",
    [string]$FileAccount = "ceanskiier27@networkbuster.net",
    [string]$NewAdmin = "preciseliens@gmail.com",
    [string]$AclBackup = "C:\temp\K_acl_backup.txt"
)

function Require-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Error "This script must be run from an elevated Administrator PowerShell. Exiting."
        exit 1
    }
}

function Rollback {
    Write-Host "Rolling back ACLs from backup (if present)..." -ForegroundColor Yellow
    if (Test-Path $AclBackup) {
        icacls $KPath /restore $AclBackup
        Write-Host "ACLs restored from $AclBackup"
    } else {
        Write-Host "ACL backup not found at $AclBackup; nothing restored." -ForegroundColor Red
    }
    if (Test-Path $File) {
        attrib -h $File -ErrorAction SilentlyContinue
        Write-Host "Un-hidden $File"
    }
}

# Start
Require-Admin

Write-Host "1) Creating backup folder and backing up K:\ ACLs to $AclBackup" -ForegroundColor Cyan
$dir = Split-Path $AclBackup -Parent
if (-not (Test-Path $dir)) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }

icacls $KPath /save $AclBackup /T | Out-Null
Write-Host "ACLs saved to $AclBackup" -ForegroundColor Green

Write-Host "2) Granting Everyone Read & Execute on $KPath (this is safer than FullControl)" -ForegroundColor Cyan
cmd /c "icacls `"$KPath`" /grant Everyone:(OI)(CI)(RX) /T"

Write-Host "3) Hiding $File (attrib +h)" -ForegroundColor Cyan
if (Test-Path $File) { attrib +h $File } else { Write-Host "Warning: $File not found. Please confirm path." -ForegroundColor Yellow }

Write-Host "4) Securing the file: removing inheritance, granting $FileAccount Full control, granting Administrators Full control, and removing Everyone" -ForegroundColor Cyan
if (Test-Path $File) {
    cmd /c "icacls `"$File`" /inheritance:r /grant `"$FileAccount`":F /grant Administrators:F /remove Everyone /T"
    Write-Host "File ACLs updated for $File" -ForegroundColor Green
} else {
    Write-Host "Skipping ACL change: $File does not exist." -ForegroundColor Yellow
}

Write-Host "5) Adding $NewAdmin to local Administrators group" -ForegroundColor Cyan
try {
    # Preferred: Add-LocalGroupMember (PowerShell 5+)
    Add-LocalGroupMember -Group "Administrators" -Member $NewAdmin -ErrorAction Stop
    Write-Host "$NewAdmin added to local Administrators (Add-LocalGroupMember)." -ForegroundColor Green
} catch {
    Write-Host "Add-LocalGroupMember failed, attempting 'net localgroup' command. Error: $_" -ForegroundColor Yellow
    $netCmd = "net localgroup Administrators `"$NewAdmin`" /add"
    Write-Host "Running: $netCmd" -ForegroundColor Cyan
    $netOut = cmd /c $netCmd
    Write-Host $netOut
}

Write-Host "6) Verification: showing final ACLs and Administrators group membership" -ForegroundColor Cyan
if (Test-Path $File) { icacls $File } else { Write-Host "File not present to show ACLs." }

Write-Host "Administrators group members:" -ForegroundColor Cyan
try { Get-LocalGroupMember -Group "Administrators" } catch { net localgroup Administrators }

Write-Host "Done. If anything went wrong, you can run the Rollback function in this session: Rollback" -ForegroundColor Green
Write-Host "Note: if Windows requires a different principal format (AzureAD\user, MicrosoftAccount\user, domain\user), the Add-LocalGroupMember/net command may fail. In that case, resolve the exact principal name and retry." -ForegroundColor Yellow

# End of script
