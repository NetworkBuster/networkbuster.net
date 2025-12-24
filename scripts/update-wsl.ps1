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
  Write-Host "Scheduled task '$TaskName' created to run daily at $RunTime (script: $scriptPath)$($UseRoot ? ' (runs updates as root)' : '')$($LogDir ? "; logs -> $LogDir" : '')" -ForegroundColor Green
} 

function Run-UpdateInDistro {
  param($name)
  Write-Host "==> Updating distro: $name" -ForegroundColor Cyan

  $execUser = ''
  if ($UseRoot) { $execUser = '-u root' }

  if ($DryRun) {
    Write-Host "Dry-run: wsl -d $name $execUser -- bash -lc 'sudo apt update && sudo apt full-upgrade -y && sudo apt autoremove -y'"
    return
  }

  $cmd = "sudo apt update && sudo apt full-upgrade -y && sudo apt autoremove -y"
  try {
    if ($UseRoot) {
      wsl -d $name -u root -- bash -lc "$cmd"
    } else {
      wsl -d $name -- bash -lc "$cmd"
    }
    Write-Host "Finished update for $name" -ForegroundColor Green
  } catch {
    Write-Host "Update failed for $name: $_" -ForegroundColor Red
  }
}

# Ensure wsl is available
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
  Write-Error "WSL is not available on this system. Install WSL or run updates inside your distro directly."
  exit 1
}

# If requested, register a scheduled task to run this script daily and exit
if ($RegisterScheduledTask) {
  Register-UpdateScheduledTask -TaskName "WSL-Update" -RunTime $ScheduleTime -UseRoot:$UseRoot -LogDir $LogDir
  exit 0
} 

if ($Distro) {
  # Update single distro
  Run-UpdateInDistro -name $Distro
  exit 0
}

# Get list of distros
$distroList = wsl -l -q 2>$null | Where-Object { $_ -ne '' }
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
