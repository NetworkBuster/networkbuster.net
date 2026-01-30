<#
Download and install Node MSI (24.x) safely.
This script ensures the MSI is fully downloaded before launching the installer.

Usage:
  .\install-node-msi.ps1 -Version '24.x' -AcceptUAC
#>
param(
  [string]$VersionPath = 'latest-v24.x',
  [switch]$AcceptUAC
)

function Fail([string]$m) { Write-Error $m; exit 1 }

$base = "https://nodejs.org/dist/$VersionPath/"
Write-Output "Fetching index from $base"
try { $index = Invoke-WebRequest -Uri $base -UseBasicParsing -ErrorAction Stop; $content = $index.Content } catch { Fail "Failed to fetch Node index: $($_.Exception.Message)" }

$match = [regex]::Match($content,'href="(?<name>node-v(?<ver>\d+\.\d+\.\d+)-x64\.msi)"')
if (-not $match.Success) { Fail 'Could not find MSI on Node index page' }

$msiName = $match.Groups['name'].Value
$msiUrl = $base + $msiName
$tmp = Join-Path $env:TEMP $msiName

Write-Output "Downloading $msiUrl -> $tmp"
Invoke-WebRequest -Uri $msiUrl -OutFile $tmp -UseBasicParsing -ErrorAction Stop

# Wait until file is stable (size not changing) and above a sensible threshold
$maxWait = 60; $waited = 0; $prevSize = -1
while ($waited -lt $maxWait) {
  if (Test-Path $tmp) {
    $s = (Get-Item $tmp).Length
    if ($s -gt 1024*1024 -and $s -eq $prevSize) { break }
    $prevSize = $s
  }
  Start-Sleep -Seconds 1
  $waited++
}
if (-not (Test-Path $tmp)) { Fail "Downloaded file missing: $tmp" }
if ((Get-Item $tmp).Length -lt 1024*1024) { Fail "Downloaded MSI appears too small: $((Get-Item $tmp).Length) bytes" }

Write-Output "Installer ready: $tmp (size: $((Get-Item $tmp).Length) bytes)"
if (-not $AcceptUAC) { Fail 'Refusing to run installer without UAC acceptance. Re-run with -AcceptUAC to proceed.' }

Write-Output 'Launching MSI (UAC prompt will appear)'
Start-Process -FilePath 'msiexec.exe' -ArgumentList '/i',"$tmp",'/passive' -Verb RunAs -Wait
Write-Output 'Installer finished.'
