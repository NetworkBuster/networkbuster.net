<#
.SYNOPSIS
  Copy-ProjectToUsb.ps1 - PowerShell helper to copy a project folder to a USB drive (Windows)

.DESCRIPTION
  Usage:
    -Source <path> (defaults to repo root, parent of script)
    -Destination <path> (drive root or folder, e.g. E:\Project)
    -Zip (switch) to create a zip archive at the destination
    -Exclude (array) to exclude directories like node_modules

.EXAMPLE
  .\Copy-ProjectToUsb.ps1 -Destination 'E:\NetworkBuster' -Exclude 'node_modules','.git'
#>
param(
  [string]$Source = "",
  [string]$Destination = "E:\NetworkBuster",
  [switch]$Zip,
  [string[]]$Exclude = @('node_modules', '.git', 'dist'),  [switch]$AutoDetect,  [switch]$WhatIf
)

Set-StrictMode -Version Latest

if (-not $Source) {
  $ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
  $Source = (Split-Path -Parent $ScriptPath)
}

Write-Host "Source: $Source"
Write-Host "Destination: $Destination"

# Auto-detect removable drives when requested or when destination doesn't exist
if ($AutoDetect -or -not (Test-Path $Destination)) {
  Write-Host "Detecting removable drives..."
  $rem = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=2" | Select-Object DeviceID, VolumeName
  if (-not $rem -or $rem.Count -eq 0) {
    Write-Host "No removable drives found. Please specify -Destination or insert a removable drive." -ForegroundColor Yellow
    exit 1
  }

  if ($rem.Count -eq 1) {
    $drive = $rem[0].DeviceID
    $Destination = Join-Path "$drive\" "NetworkBuster"
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Write-Host "Using destination: $Destination"
  } else {
    Write-Host "Multiple removable drives detected:" 
    $i = 0
    foreach ($d in $rem) { $i++; Write-Host "[$i] $($d.DeviceID) - $($d.VolumeName)" }
    $sel = Read-Host "Choose a drive by number (or press Enter to cancel)"
    if (-not $sel) { Write-Host "Cancelled"; exit 1 }
    if (-not ($sel -as [int])) { Write-Host "Invalid selection"; exit 1 }
    $idx = [int]$sel - 1
    if ($idx -lt 0 -or $idx -ge $rem.Count) { Write-Host "Invalid selection"; exit 1 }
    $picked = $rem[$idx].DeviceID
    $Destination = Join-Path "$picked\" "NetworkBuster"
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Write-Host "Using destination: $Destination"
  }
}

if ($Zip) {
  $timestamp = Get-Date -Format yyyyMMdd-HHmmss
  $archive = Join-Path -Path $Destination -ChildPath "project-$timestamp.zip"
  New-Item -ItemType Directory -Force -Path $Destination | Out-Null
  Write-Host "Creating zip: $archive"

  $excludeParams = foreach ($e in $Exclude) { """$e""" }
  Compress-Archive -Path (Join-Path $Source '*') -DestinationPath $archive -Force
  Write-Host "Archive created: $archive"
} else {
  # Use robocopy for robust copying
  $exArgs = @()
  foreach ($e in $Exclude) { $exArgs += "/XD"; $exArgs += $e }

  $robocopyArgs = @($Source, $Destination, '/E', '/MT:8') + $exArgs
  if ($WhatIf) { $robocopyArgs += '/L' }

  Write-Host "+ robocopy $($robocopyArgs -join ' ')"
  robocopy @robocopyArgs | Write-Host
  Write-Host "Robocopy finished. Check output for file counts and errors."
}

Write-Host "Done. Remember to safely eject the USB drive before removal."
