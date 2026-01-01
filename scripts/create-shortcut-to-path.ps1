param(
    [Parameter(Mandatory=$true)] [string]$DestinationFolder,
    [string]$LinkName = 'Copy Project to USB - NetworkBusterSetup',
    [string]$CopyScript = 'K:\\networkbuster.net\\scripts\\Copy-ProjectToUsb.ps1',
    [string]$RepoRoot = 'K:\\networkbuster.net'
)

# Ensure folder exists
New-Item -ItemType Directory -Force -Path $DestinationFolder | Out-Null

$ShortcutPath = Join-Path $DestinationFolder ($LinkName + '.lnk')
try {
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut($ShortcutPath)
    $lnk.TargetPath = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
    $lnk.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $CopyScript + '" -Path "' + $DestinationFolder + '" -AutoDetect'
    $lnk.WorkingDirectory = $RepoRoot
    $icon = Join-Path $RepoRoot 'favicon.ico'
    if (Test-Path $icon) { $lnk.IconLocation = $icon + ',0' }
    $lnk.Save()
    Write-Output "Created shortcut: $ShortcutPath"
} catch {
    Write-Error "Failed to create shortcut: $_"
    exit 1
}