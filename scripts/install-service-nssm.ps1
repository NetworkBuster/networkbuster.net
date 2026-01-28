<#
Install NetworkBuster as a Windows service using NSSM.
Run this script as Administrator.

Usage:
  .\install-service-nssm.ps1 -WatchdogPath 'S:\NetworkBuster_Production\scripts\watchdog.ps1' -NodePath 'C:\Program Files\nodejs\node.exe'
#>
param(
  [string]$WatchdogPath = 'S:\NetworkBuster_Production\scripts\watchdog.ps1',
  [string]$NodePath = 'C:\Program Files\nodejs\node.exe',
  [string]$AppArgs = 'start-servers.js',
  [string]$WorkingDir = 'S:\NetworkBuster_Production',
  [string]$LogDir = 'S:\NetworkBuster_Production\logs',
  [string]$ServiceName = 'NetworkBuster',
  [string]$NssmDir = 'C:\tools\nssm'
)

function Assert-Admin {
  if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator."; exit 1
  }
}

Assert-Admin

if (-not (Test-Path $WatchdogPath)) { Write-Error "Watchdog not found at $WatchdogPath"; exit 1 }
if (-not (Test-Path $NodePath)) { Write-Error "Node not found at $NodePath"; exit 1 }

# Ensure logs dir
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

# Download and install NSSM if missing
$nssmExe = Join-Path $NssmDir 'nssm.exe'
if (-not (Test-Path $nssmExe)) {
  Write-Output "NSSM not found. Installing to $NssmDir"
  try {
    New-Item -ItemType Directory -Path $NssmDir -Force | Out-Null
    $tmpZip = Join-Path $env:TEMP 'nssm.zip'
    $url = 'https://nssm.cc/release/nssm-2.24.zip'
    Write-Output "Downloading NSSM from $url"
    Invoke-WebRequest -Uri $url -OutFile $tmpZip -UseBasicParsing -ErrorAction Stop
    # Ensure file fully written and non-empty
    $tries = 0
    while ($tries -lt 5) {
      if ((Test-Path $tmpZip) -and ((Get-Item $tmpZip).Length -gt 10240)) { break }
      Start-Sleep -Seconds 1
      $tries++
    }
    if (-not (Test-Path $tmpZip)) { Write-Error "Download failed: $tmpZip not found"; exit 1 }
    if ((Get-Item $tmpZip).Length -le 10240) { Write-Error "Downloaded file is too small (${(Get-Item $tmpZip).Length} bytes); aborting."; exit 1 }
    Expand-Archive -Path $tmpZip -DestinationPath $env:TEMP -Force
    # copy win64 nssm.exe if present
    $candidate = Get-ChildItem -Path (Join-Path $env:TEMP 'nssm-*') -Recurse -Filter 'nssm.exe' -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'win64' } | Select-Object -First 1
    if (-not $candidate) { $candidate = Get-ChildItem -Path (Join-Path $env:TEMP 'nssm-*') -Recurse -Filter 'nssm.exe' -ErrorAction SilentlyContinue | Select-Object -First 1 }
    if ($candidate) { Copy-Item -Path $candidate.FullName -Destination $nssmExe -Force; Write-Output "Installed NSSM from $($candidate.FullName)" } else { Write-Warning "Could not locate nssm.exe in archive. Please install NSSM manually to $NssmDir and re-run."; exit 1 }
  } catch { Write-Error "Failed to install NSSM: $($_.Exception.Message)"; exit 1 }
}

# Build watchdog command
$watchdogCmd = "-NoProfile -ExecutionPolicy Bypass -File `"$WatchdogPath`" -AppExe `"$NodePath`" -AppArgs `"$AppArgs`" -WorkingDir `"$WorkingDir`" -LogDir `"$LogDir`" -HealthUrl `"http://localhost:3001/api/health`" -HealthInterval 30 -RestartBackoff 5"

# Install service
Write-Output "Installing service $ServiceName using $nssmExe"
& $nssmExe install $ServiceName 'powershell.exe' $watchdogCmd
# Configure stdout/stderr and other settings
& $nssmExe set $ServiceName AppStdout (Join-Path $LogDir 'service.out.log')
& $nssmExe set $ServiceName AppStderr (Join-Path $LogDir 'service.err.log')
& $nssmExe set $ServiceName AppRotateFiles 1
& $nssmExe set $ServiceName AppRestartDelay 5000

# Set service to auto-start and start it
Set-Service -Name $ServiceName -StartupType Automatic
Start-Service -Name $ServiceName

Start-Sleep -Seconds 2
$svc = Get-Service -Name $ServiceName
Write-Output "Service status: $($svc.Status)"
Write-Output "Service $ServiceName installed and started. Logs: $LogDir"
