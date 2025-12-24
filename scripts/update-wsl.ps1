<#
.SYNOPSIS
  Update packages in WSL distros from Windows (PowerShell script).

.DESCRIPTION
  This script enumerates available WSL distros and runs apt update/full-upgrade/autoremove inside each.
  Run from an elevated PowerShell prompt.

.PARAMETER Distro
  Optional specific distro name. If omitted, all installed distros will be updated.

.EXAMPLE
  .\scripts\update-wsl.ps1
  Updates all WSL distros.

  .\scripts\update-wsl.ps1 -Distro ubuntu
  Updates only the 'ubuntu' distro.
#>
[CmdletBinding()]
param(
  [string]$Distro,
  [switch]$DryRun,
  [string]$WorkingDir,
  [switch]$UseRoot,
  [switch]$RegisterScheduledTask,
  [string]$ScheduleTime = '03:00',  # HH:mm (24h) local time
  [switch]$SkipWSLUpdate,
  [string]$WslPath,
  [string]$LogDir
) # $LogDir: optional path to write logs (e.g., 'G:\cadil\logs')

# Note: when running with -UseRoot the WSL commands will be executed as the root user
# (wsl -d <distro> -u root -- <cmd>) so sudo prompts inside the distro are skipped.

# If a working directory is provided, switch to it (useful when running from a mounted drive like G:\kodak)
if ($WorkingDir) {
  if (-not (Test-Path -Path $WorkingDir)) {
    Write-Error "Working directory '$WorkingDir' does not exist."
    exit 1
  }
  Write-Host "Switching to working directory: $WorkingDir" -ForegroundColor Cyan
  Set-Location -Path $WorkingDir
}

# Setup logging to the provided LogDir (if any)
if ($LogDir) {
  try {
    if (-not (Test-Path -Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $script:LogFile = Join-Path $LogDir "wsl-update-$timestamp.log"
    Write-Host "Logging to: $script:LogFile" -ForegroundColor Cyan
    if (-not $DryRun) { Start-Transcript -Path $script:LogFile -Force }
  } catch {
    Write-Warning "Could not create or write to LogDir '$LogDir': $_"
  }
} else {
  $script:LogFile = $null
} 

function Register-UpdateScheduledTask {
  param(
    [string]$TaskName = "WSL-Update",
    [string]$RunTime = '03:00',
    [switch]$UseRoot,
    [string]$LogDir
  )

  if (-not (Get-Command Register-ScheduledTask -ErrorAction SilentlyContinue)) {
    Write-Error "Scheduled Task cmdlets are not available on this system. Run on Windows 10/11 with required privileges."
    exit 1
  }

  $scriptPath = (Get-Location).Path + '\\scripts\\update-wsl.ps1'
  if (-not (Test-Path $scriptPath)) {
    Write-Error "Cannot locate script at $scriptPath to register as scheduled task."
    exit 1
  }

  $timeParts = $RunTime -split ':'
  $trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date -Hour [int]$timeParts[0] -Minute [int]$timeParts[1] -Second 0)

  # Include -UseRoot flag if requested
  $useArg = ''
  if ($UseRoot) { $useArg = ' -UseRoot' }

  # Include -LogDir if provided
  $logArg = ''
  if ($LogDir) { $logArg = " -LogDir `"$LogDir`"" }

  $action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`"$useArg$logArg"

  # Register or update
  if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  }

  Register-ScheduledTask -TaskName $TaskName -Trigger $trigger -Action $action -RunLevel Highest -Force
  $runAsRootText = ''
  if ($UseRoot) { $runAsRootText = ' (runs updates as root)' }
  $logText = ''
  if ($LogDir) { $logText = "; logs -> $LogDir" }
  Write-Host "Scheduled task '$TaskName' created to run daily at $RunTime (script: $scriptPath)$runAsRootText$logText" -ForegroundColor Green
} 

function Run-UpdateInDistro {
  param($name)
  Write-Host "==> Updating distro: $name" -ForegroundColor Cyan

  $execUser = ''
  if ($UseRoot) { $execUser = '-u root' }

  # Detect package manager inside the distro
  $detectScript = 'if command -v apt >/dev/null 2>&1; then echo apt; elif command -v dnf >/dev/null 2>&1; then echo dnf; elif command -v pacman >/dev/null 2>&1; then echo pacman; elif command -v zypper >/dev/null 2>&1; then echo zypper; elif command -v apk >/dev/null 2>&1; then echo apk; else echo unknown; fi'
  try {
    $pkgmgr = & $wslCommand -d $name $execUser -- bash -lc "$detectScript" 2>$null
    $pkgmgr = ($pkgmgr -join "`n").Trim()
  } catch {
    Write-Host "Could not detect package manager for $($name): $($_)" -ForegroundColor Yellow
    return
  }

  switch ($pkgmgr) {
    'apt' { $updateCmd = 'apt update && apt full-upgrade -y && apt autoremove -y' }
    'dnf' { $updateCmd = 'dnf check-update || true; dnf upgrade -y; dnf autoremove -y' }
    'pacman' { $updateCmd = 'pacman -Syu --noconfirm' }
    'zypper' { $updateCmd = 'zypper refresh && zypper update -y' }
    'apk' { $updateCmd = 'apk update && apk upgrade' }
    default { $updateCmd = $null }
  }

  if (-not $updateCmd) {
    Write-Host "Could not detect a supported package manager in $name; skipping." -ForegroundColor Yellow
    return
  }

  # If not running as root inside the distro, prefix with sudo
  if (-not $UseRoot) { $updateCmd = "sudo $updateCmd" }

  if ($DryRun) {
    $wslDisplay = if ($wslCommand) { $wslCommand } else { 'wsl' }
    Write-Host "Dry-run: $wslDisplay -d $name $execUser -- bash -lc '$updateCmd'"
    return
  }

  $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
  if ($script:LogFile) {
    $distroLog = Join-Path (Split-Path $script:LogFile -Parent) "$($name)-$timestamp.log"
  } elseif ($LogDir) {
    if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
    $distroLog = Join-Path $LogDir "$($name)-$timestamp.log"
  } else {
    $distroLog = $null
  }

  try {
    if ($UseRoot) {
      $output = & $wslCommand -d $name -u root -- bash -lc "$updateCmd" 2>&1
    } else {
      $output = & $wslCommand -d $name -- bash -lc "$updateCmd" 2>&1
    }

    if ($distroLog) {
      $output | Out-File -FilePath $distroLog -Encoding utf8
      Write-Host "Log saved to: $distroLog" -ForegroundColor Cyan
    } else {
      Write-Host $output
    }

    Write-Host "Finished update for $name" -ForegroundColor Green
  } catch {
    Write-Host "Update failed for $($name): $($_)" -ForegroundColor Red
    if ($distroLog -and $output) { $output | Out-File -FilePath $distroLog -Append -Encoding utf8 }
  }
}

# Resolve wsl executable (honor -WslPath if provided)
$wslCommand = $null
if ($WslPath) {
  if (Test-Path $WslPath) {
    $wslCommand = $WslPath
  } else {
    Write-Warning "Provided WslPath '$WslPath' not found."
  }
}

if (-not $wslCommand) {
  $cmd = Get-Command wsl -ErrorAction SilentlyContinue
  if ($cmd) { $wslCommand = $cmd.Path }
}

if (-not $wslCommand) {
  $possible = @(
    "$env:SystemRoot\System32\wsl.exe",
    "$env:SystemRoot\Sysnative\wsl.exe",
    "$env:SystemRoot\SysWOW64\wsl.exe",
    "R:\\Windows\\System32\\wsl.exe",
    "R:\\Windows\\Sysnative\\wsl.exe"
  )
  foreach ($p in $possible) {
    if (Test-Path $p) { $wslCommand = $p; break }
  }
}

if (-not $wslCommand) {
  Write-Error "WSL executable not found. If WSL is installed in a non-standard location, provide its path with -WslPath. Example: -WslPath 'C:\\Windows\\System32\\wsl.exe'"
  exit 1
}

Write-Host "Using WSL executable: $wslCommand" -ForegroundColor Cyan

# If requested, register a scheduled task to run this script daily and exit
if ($RegisterScheduledTask) {
  Register-UpdateScheduledTask -TaskName "WSL-Update" -RunTime $ScheduleTime -UseRoot:$UseRoot -LogDir $LogDir
  exit 0
} 

# Run WSL kernel/component update (unless explicitly skipped)
Write-Host "Checking WSL update status..." -ForegroundColor Cyan
if ($DryRun) {
  Write-Host "Dry-run: $wslCommand --status"
  if (-not $SkipWSLUpdate) { Write-Host "Dry-run: $wslCommand --update" }
} else {
  try {
    & $wslCommand --status
  } catch {
    Write-Warning "$wslCommand --status is not available or failed: $($_)"
  }
  if (-not $SkipWSLUpdate) {
    try {
      & $wslCommand --update
      Write-Host "WSL components updated (if updates were available)." -ForegroundColor Green
    } catch {
      Write-Warning "$wslCommand --update failed or is not supported on this system: $($_)"
    }
  } else {
    Write-Host "Skipping 'wsl --update' as requested." -ForegroundColor Yellow
  }
} 

if ($Distro) {
  # Update single distro
  Run-UpdateInDistro -name $Distro
  exit 0
} 

# Get list of distros
$distroList = & $wslCommand -l -q 2>$null | Where-Object { $_ -ne '' }
if (-not $distroList) {
  Write-Host "No WSL distros found." -ForegroundColor Yellow
  exit 0
} 

Write-Host "Found distros: $($distroList -join ', ')" -ForegroundColor Cyan
foreach ($d in $distroList) {
  Run-UpdateInDistro -name $d
}

Write-Host "All WSL updates attempted." -ForegroundColor Green

# Stop logging transcript if it was started
if ($script:LogFile -and -not $DryRun) {
  try { Stop-Transcript -ErrorAction SilentlyContinue } catch { }
  Write-Host "Transcript saved to: $script:LogFile" -ForegroundColor Cyan
}
