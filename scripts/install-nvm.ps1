<#
Download and run nvm-windows installer safely. Ensures the EXE is fully downloaded before launch.

Usage:
  .\install-nvm.ps1 -AcceptUAC
#>
param(
  [switch]$AcceptUAC
)

function Fail([string]$m) { Write-Error $m; exit 1 }

$releases = 'https://github.com/coreybutler/nvm-windows/releases/latest'
Write-Output "Fetching releases page: $releases"
try { $page = Invoke-WebRequest -Uri $releases -UseBasicParsing -ErrorAction Stop; $content = $page.Content } catch { Fail "Failed to fetch releases page: $($_.Exception.Message)" }

$m = [regex]::Match($content,'href="(?<url>/coreybutler/nvm-windows/releases/download/[^"]*nvm-setup.exe)"')
if (-not $m.Success) { Fail 'Could not locate nvm-setup.exe link on releases page' }

$url = 'https://github.com' + $m.Groups['url'].Value
$dest = Join-Path $env:TEMP 'nvm-setup.exe'
Write-Output "Downloading $url -> $dest"
Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -ErrorAction Stop

# Wait until file is stable and reasonable size
$maxWait = 60; $waited = 0; $prevSize = -1
while ($waited -lt $maxWait) {
  if (Test-Path $dest) {
    $s = (Get-Item $dest).Length
    if ($s -gt 10240 -and $s -eq $prevSize) { break }
    $prevSize = $s
  }
  Start-Sleep -Seconds 1; $waited++
}
if (-not (Test-Path $dest)) { Fail "Downloaded file missing: $dest" }
if ((Get-Item $dest).Length -lt 10240) { Fail "Downloaded installer appears too small: $((Get-Item $dest).Length) bytes" }

Write-Output "Installer ready: $dest"
if (-not $AcceptUAC) { Fail 'Refusing to run installer without UAC acceptance. Re-run with -AcceptUAC to proceed.' }

Write-Output 'Launching nvm installer (UAC prompt will appear)'
Start-Process -FilePath $dest -Verb RunAs -Wait
Write-Output 'nvm installer finished.'
