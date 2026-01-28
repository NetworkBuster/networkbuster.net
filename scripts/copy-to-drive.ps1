<#
.SYNOPSIS
  Copy repository artifacts (default: LFS output) to a destination drive reliably.

.DESCRIPTION
  Performs sanity checks (disk space), creates a timestamped destination folder on the specified drive,
  copies files via Robocopy for reliability, and generates SHA256 checksums for copied files.

.PARAMETER Source
  The source directory to copy (default: os/lfs/output).

.PARAMETER DestDrive
  The destination drive letter (e.g. 'E:'). The script will create a subfolder `networkbuster-<timestamp>` there.

.PARAMETER IncludeRepo
  If set, copy the repository working tree (excludes .git) instead of the default LFS output.

.PARAMETER Zip
  If set, create a zip archive of the copied folder after copy completes.

.EXAMPLE
  # Copy LFS output to E: and produce checksums
  .\scripts\copy-to-drive.ps1 -DestDrive 'E:' -LogDir 'E:\logs'

  # Copy full repo working tree (no .git)
  .\scripts\copy-to-drive.ps1 -DestDrive 'E:' -IncludeRepo
#>
[CmdletBinding()]
param(
  [string]$Source = "$(Join-Path $PSScriptRoot '..\os\lfs\output')",
  [Parameter(Mandatory = $true)][string]$DestDrive,
  [switch]$IncludeRepo,
  [switch]$Zip,
  [string]$LogDir
)

function Format-Bytes($bytes){
  if ($bytes -lt 1KB) { "$bytes B" ; return }
  if ($bytes -lt 1MB) { "{0:N2} KB" -f ($bytes/1KB); return }
  if ($bytes -lt 1GB) { "{0:N2} MB" -f ($bytes/1MB); return }
  "{0:N2} GB" -f ($bytes/1GB)
}

if ($IncludeRepo) {
  $Source = Join-Path $PSScriptRoot '..' | Resolve-Path -ErrorAction Stop
  Write-Host "IncludeRepo: copying working tree from: $Source" -ForegroundColor Cyan
  # Exclude .git by using Robocopy /XD
}

if (-not (Test-Path $Source)) {
  Write-Error "Source path not found: $Source"
  exit 1
}

# Destination
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$destRoot = "${DestDrive.TrimEnd('\')}\networkbuster-$timestamp"

# Ensure drive exists
$drv = Get-PSDrive -Name ($DestDrive.TrimEnd(':')) -ErrorAction SilentlyContinue
if (-not $drv) {
  Write-Error "Destination drive $DestDrive not found or not accessible."
  exit 1
}

# Check free space
$sourceSize = (Get-ChildItem -Path $Source -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
if (-not $sourceSize) { $sourceSize = 0 }
$freeBytes = $drv.Free
Write-Host "Source size: $(Format-Bytes $sourceSize)    Dest free: $(Format-Bytes $freeBytes)"
if ($sourceSize -gt $freeBytes) {
  Write-Error "Not enough free space on $DestDrive (needed: $(Format-Bytes $sourceSize))."
  exit 1
}

# Create dest folder
New-Item -ItemType Directory -Path $destRoot -Force | Out-Null
Write-Host "Destination folder: $destRoot" -ForegroundColor Green

# Optional: create a log dir
if ($LogDir) {
  if (-not (Test-Path -Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
  $logFile = Join-Path $LogDir "copy-to-drive-$timestamp.log"
  Write-Host "Logging robocopy output to: $logFile" -ForegroundColor Cyan
} else {
  $logFile = $null
}

# Run Robocopy
$roboSource = (Resolve-Path $Source).Path
$roboDest = $destRoot
$roboOpts = '/MIR /COPY:DAT /R:2 /W:2 /NFL /NDL /NP /ETA'
$excludeArgs = ''
if ($IncludeRepo) { $excludeArgs = "/XD `"$($Source)\.git`"" }
$roboCmd = "robocopy `"$roboSource`" `"$roboDest`" $roboOpts $excludeArgs"
Write-Host "Running: $roboCmd"
if ($logFile) {
  cmd /c $roboCmd | Out-File -FilePath $logFile -Encoding utf8 -Append
} else {
  cmd /c $roboCmd
}

# Generate checksums for top-level files
Write-Host "Generating SHA256 checksums..."
$checksumFile = Join-Path $destRoot 'checksums.sha256'
Get-ChildItem -Path $destRoot -Recurse -File | Sort-Object FullName | ForEach-Object {
  $hash = Get-FileHash -Path $_.FullName -Algorithm SHA256
  "$($hash.Hash) *$($_.FullName.Substring($destRoot.Length+1))" | Out-File -FilePath $checksumFile -Append -Encoding utf8
}
Write-Host "Checksums written to: $checksumFile" -ForegroundColor Green

# Optionally zip
if ($Zip) {
  $zipPath = "${destRoot}.zip"
  Write-Host "Creating zip: $zipPath"
  Compress-Archive -Path (Join-Path $destRoot '*') -DestinationPath $zipPath -Force
  Write-Host "Zip created: $zipPath" -ForegroundColor Green
}

Write-Host "Copy complete. Destination: $destRoot" -ForegroundColor Cyan
if ($logFile) { Write-Host "Robocopy log: $logFile" -ForegroundColor Cyan }
if ($script:LogFile) { Write-Host "Script transcript (if any) ended at: $script:LogFile" -ForegroundColor Cyan }
