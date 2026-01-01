$ShortcutPath = 'C:\Users\Public\Desktop\Copy Project to USB - NetworkBusterSetup.lnk'
$CopyScript = 'K:\networkbuster.net\scripts\Copy-ProjectToUsb.ps1'
$Icon = 'K:\networkbuster.net\favicon.ico'

try {
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut($ShortcutPath)
    $lnk.TargetPath = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
    $lnk.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $CopyScript + '" -AutoDetect'
    $lnk.WorkingDirectory = 'K:\networkbuster.net'
    if (Test-Path $Icon) { $lnk.IconLocation = $Icon + ',0' }
    $lnk.Save()
    Write-Output "Created shortcut: $ShortcutPath"
} catch {
    Write-Error "Failed to create shortcut: $_"
    exit 1
}