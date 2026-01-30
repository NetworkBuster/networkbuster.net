<#
Install the nbapp application from GitHub and optionally register it as a Windows service using NSSM.

Usage:
  .\install-nbapp-service.ps1 -Repo 'https://github.com/NetworkBuster/nbapp.git' -InstallDir 'S:\apps\nbapp' -InstallService -ServiceName 'nbapp'

#>
param(
  [string]$Repo = 'https://github.com/NetworkBuster/nbapp.git',
  [string]$Branch = 'main',
  [string]$InstallDir = 'S:\apps\nbapp',
  [switch]$InstallService,
  [string]$ServiceName = 'nbapp',
  [string]$NodePath = '',
  [string]$LogDir = 'S:\apps\nbapp\logs'
)

function Write-Ok { param($m) Write-Host $m -ForegroundColor Green }
function Write-Warn { param($m) Write-Host $m -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host $m -ForegroundColor Red }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Err 'git is required but not found in PATH.'; exit 1 }

# Ensure install dir
if (-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null }

if ((Get-ChildItem -Path $InstallDir -Force -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0) {
  Write-Ok "Cloning $Repo into $InstallDir"
  git clone --branch $Branch $Repo $InstallDir
} else {
  Write-Ok "Directory exists, updating: $InstallDir"
  Push-Location $InstallDir; try { git fetch origin; git checkout $Branch; git pull --ff-only origin $Branch } catch { Write-Warn "Git pull failed: $($_.Exception.Message)" } ; Pop-Location
}

# Run npm install if package.json present
if (Test-Path (Join-Path $InstallDir 'package.json')) {
  Write-Ok 'Running npm install in application directory'
  $npm = (Get-Command npm -ErrorAction SilentlyContinue).Path
  if (-not $npm) { Write-Warn 'npm not found on PATH; try running "npm install" manually or provide a Node runtime.' } else {
    Push-Location $InstallDir; & $npm install --no-audit --no-fund; Pop-Location
  }
} else {
  Write-Warn 'No package.json found; skipping npm install.'
}

# Determine application entry script (prefer package.json main, fallback to server.js)
$appArgs = 'server.js'
try {
  $pkg = Get-Content (Join-Path $InstallDir 'package.json') -Raw -ErrorAction SilentlyContinue | ConvertFrom-Json
  if ($pkg) {
    if ($pkg.main) { $appArgs = $pkg.main }
    elseif ($pkg.scripts -and $pkg.scripts.start) {
      # if start script refers to node <file>, attempt to extract file name; else fallback to npm start
      if ($pkg.scripts.start -match 'node\s+(?<file>\S+)') { $appArgs = $Matches['file'] } else { $appArgs = 'npm start' }
    }
  }
} catch {}

Write-Ok "Using app args: $appArgs"

# Determine node runtime
if (-not $NodePath) {
  # prefer repo-local tools/node if present
  $candidate = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) '..' | Resolve-Path -ErrorAction SilentlyContinue
  $repoRoot = if ($candidate) { (Resolve-Path $candidate).Path } else { (Split-Path -Parent $MyInvocation.MyCommand.Definition) }
  $localNode = Join-Path $repoRoot 'tools\node\node.exe'
  if (Test-Path $localNode) { $NodePath = $localNode }
  else { $NodePath = (Get-Command node -ErrorAction SilentlyContinue).Path }
}

if (-not $NodePath) { Write-Warn 'Node runtime not found automatically. You can pass -NodePath to this script to point to a node.exe' }
else { Write-Ok "Using Node runtime: $NodePath" }

if ($InstallService) {
  # Call install-service-nssm.ps1 as admin to register the watchdog/service
  $installer = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) 'install-service-nssm.ps1'
  if (-not (Test-Path $installer)) { Write-Err "Service installer not found: $installer"; exit 1 }

  $watchdog = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) 'watchdog.ps1'
  if (-not (Test-Path $watchdog)) { Write-Err "Watchdog script not found: $watchdog"; exit 1 }

  # Build AppArgs: if it's 'npm start', install-service will invoke node with 'npm start' which doesn't work; instead use 'node <file>' or call npm as exe. We'll support both.
  $appArgsToPass = $appArgs
  $useNpm = $false
  if ($appArgs -eq 'npm start') { $useNpm = $true }

  if ($useNpm) {
    $appExe = (Get-Command npm -ErrorAction SilentlyContinue).Path
    if (-not $appExe) { Write-Warn 'npm not found; service install may fail; consider installing Node or providing NodePath'; $appExe = $NodePath }
    $appArgsToPass = 'start'
    # For NSSM, we will call install script with AppExe = npm and AppArgs = start
    $nssmArgs = @{
      WatchdogPath = $watchdog; NodePath = $appExe; AppArgs = $appArgsToPass; WorkingDir = $InstallDir; LogDir = $LogDir; ServiceName = $ServiceName
    }
  } else {
    # AppExe will be NodePath and AppArgs $appArgsToPass
    $nssmArgs = @{
      WatchdogPath = $watchdog; NodePath = $NodePath; AppArgs = $appArgsToPass; WorkingDir = $InstallDir; LogDir = $LogDir; ServiceName = $ServiceName
    }
  }

  Write-Ok "Installing service '$ServiceName' via NSSM (this will prompt for elevation)."
  $argList = "-NoProfile -ExecutionPolicy Bypass -File `"$installer`" -WatchdogPath `"$($nssmArgs.WatchdogPath)`" -NodePath `"$($nssmArgs.NodePath)`" -AppArgs `"$($nssmArgs.AppArgs)`" -WorkingDir `"$($nssmArgs.WorkingDir)`" -LogDir `"$($nssmArgs.LogDir)`" -ServiceName `"$($nssmArgs.ServiceName)`""
  Start-Process -FilePath powershell -ArgumentList $argList -Verb RunAs -Wait
  Write-Ok 'Service installer finished. Check service status with Get-Service -Name ' + $ServiceName
} else {
  Write-Ok 'Install completed (service not installed). To install the service, re-run with -InstallService and accept UAC when prompted.'
}
