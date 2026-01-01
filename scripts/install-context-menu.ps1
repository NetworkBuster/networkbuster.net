<#
install-context-menu.ps1
Creates a Public Desktop shortcut and registers Folder/Background/Drive context menu
for "Copy Project to USB (NetworkBusterSetup)" which runs the repo's Copy-ProjectToUsb.ps1

Usage (run as admin to write HKCR):
  - To apply:   .\install-context-menu.ps1 -Apply
  - To remove:  .\install-context-menu.ps1 -Remove
  - To preview: .\install-context-menu.ps1 -WhatIf
#>

param(
    [switch]$Apply,
    [switch]$Remove,
    [switch]$WhatIf
)

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Warning "This script requires Administrator privileges to write registry entries for all users. Re-run in an elevated PowerShell session." 
        return $false
    }
    return $true
}

$ScriptPath = (Split-Path -Parent $MyInvocation.MyCommand.Definition)
$RepoRoot = Join-Path $ScriptPath ".." | Resolve-Path -Relative
$RepoRoot = (Resolve-Path "$RepoRoot").ProviderPath
$CopyScript = Join-Path $RepoRoot "scripts\Copy-ProjectToUsb.ps1"
$IconPath = Join-Path $RepoRoot "favicon.ico"
$ShortcutPath = "C:\Users\Public\Desktop\Copy Project to USB - NetworkBusterSetup.lnk"
$VerbLabel = "Copy Project to USB (NetworkBusterSetup)"

if ($Remove) {
    if (-not (Ensure-Admin)) { exit 1 }
    Write-Output "Removing registry keys and Public Desktop shortcut..."
    Remove-Item -Path "Registry::HKEY_CLASSES_ROOT\Directory\shell\NetworkBusterCopy" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path "Registry::HKEY_CLASSES_ROOT\Directory\Background\shell\NetworkBusterCopy" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path "Registry::HKEY_CLASSES_ROOT\Drive\shell\NetworkBusterCopy" -Recurse -ErrorAction SilentlyContinue
    if (Test-Path $ShortcutPath) { Remove-Item $ShortcutPath -Force }
    Write-Output "Removed."; exit 0
}

if ($WhatIf) {
    Write-Output "WhatIf: would create shortcut: $ShortcutPath"
    Write-Output "WhatIf: would add HKCR context menu keys for Directory, Directory\Background and Drive pointing to: $CopyScript -AutoDetect"
    exit 0
}

# Create Public Desktop shortcut
try {
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut($ShortcutPath)
    $lnk.TargetPath = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
    $lnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"$CopyScript\" -AutoDetect"
    $lnk.WorkingDirectory = $RepoRoot
    if (Test-Path $IconPath) { $lnk.IconLocation = "$IconPath,0" }
    $lnk.Save()
    Write-Output "Shortcut created at: $ShortcutPath"
} catch {
    Write-Warning "Failed to create Public Desktop shortcut: $_"
}

# Add registry entries (requires admin)
if (-not (Ensure-Admin)) { Write-Warning "Skipping registry install—not elevated."; exit 0 }

$commandTemplate = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"& '$CopyScript' -Path '%s' -AutoDetect\""

# Directory (folder) shell
New-Item -Path 'Registry::HKEY_CLASSES_ROOT\Directory\shell\NetworkBusterCopy' -Force | Out-Null
New-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Directory\shell\NetworkBusterCopy' -Name 'MUIVerb' -Value $VerbLabel -Force | Out-Null
if (Test-Path $IconPath) { New-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Directory\shell\NetworkBusterCopy' -Name 'Icon' -Value $IconPath -Force | Out-Null }
New-Item -Path 'Registry::HKEY_CLASSES_ROOT\Directory\shell\NetworkBusterCopy\command' -Force | Out-Null
Set-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Directory\shell\NetworkBusterCopy\command' -Name '(default)' -Value ([string]::Format($commandTemplate,'%1')) -Force

# Background (when right-clicking inside folder background)
New-Item -Path 'Registry::HKEY_CLASSES_ROOT\Directory\Background\shell\NetworkBusterCopy' -Force | Out-Null
New-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Directory\Background\shell\NetworkBusterCopy' -Name 'MUIVerb' -Value $VerbLabel -Force | Out-Null
if (Test-Path $IconPath) { New-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Directory\Background\shell\NetworkBusterCopy' -Name 'Icon' -Value $IconPath -Force | Out-Null }
New-Item -Path 'Registry::HKEY_CLASSES_ROOT\Directory\Background\shell\NetworkBusterCopy\command' -Force | Out-Null
Set-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Directory\Background\shell\NetworkBusterCopy\command' -Name '(default)' -Value ([string]::Format($commandTemplate,'%V')) -Force

# Drive (right-click on drive)
New-Item -Path 'Registry::HKEY_CLASSES_ROOT\Drive\shell\NetworkBusterCopy' -Force | Out-Null
New-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Drive\shell\NetworkBusterCopy' -Name 'MUIVerb' -Value $VerbLabel -Force | Out-Null
if (Test-Path $IconPath) { New-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Drive\shell\NetworkBusterCopy' -Name 'Icon' -Value $IconPath -Force | Out-Null }
New-Item -Path 'Registry::HKEY_CLASSES_ROOT\Drive\shell\NetworkBusterCopy\command' -Force | Out-Null
Set-ItemProperty -Path 'Registry::HKEY_CLASSES_ROOT\Drive\shell\NetworkBusterCopy\command' -Name '(default)' -Value ([string]::Format($commandTemplate,'%1')) -Force

Write-Output "Registry context menu entries installed (Directory, Background, Drive)."
Write-Output "Done."