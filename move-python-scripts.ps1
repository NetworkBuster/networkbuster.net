<#
.SYNOPSIS
  Move the `python-scripts` folder to a target location and optionally generate a SHA256 manifest.

.DESCRIPTION
  Uses robocopy to move and preserve file attributes. If -VerifySha is supplied, computes SHA256 for all moved files and writes a manifest file at the destination root.

.PARAMETER Source
  Source folder to move (default: .\python-scripts).

.PARAMETER DestinationRoot
  Root destination folder where `python-scripts` will be placed (default: K:\py scripts\networkbustersetup).

.PARAMETER VerifySha
  If set, compute SHA256 hashes for all files under the destination and write a manifest file `sha256-manifest.txt` in the destination root.

.EXAMPLE
  .\move-python-scripts.ps1 -DestinationRoot 'K:\py scripts\networkbustersetup' -VerifySha
#>
param(
    [string]$Source = '.\python-scripts',
    [string]$DestinationRoot = 'K:\py scripts\networkbustersetup',
    [switch]$VerifySha,
    [switch]$RunNpmBuild,
    [string]$NpmInstallCmd = 'ci',
    [string]$NpmInstallArgs = '--no-audit --no-fund',
    [string]$NpmBuildCmd = 'run',
    [string]$NpmBuildArgs = 'build'
) 

Set-StrictMode -Version Latest

try {
    $SourceFull = (Resolve-Path $Source).ProviderPath
} catch {
    Write-Error "Source path '$Source' not found. Aborting."
    exit 1
}

$Dest = Join-Path -Path $DestinationRoot -ChildPath 'python-scripts'

Write-Output "Ensuring destination root exists: '$DestinationRoot'"
New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null

Write-Output "Starting move: '$SourceFull' -> '$Dest'"
robocopy $SourceFull $Dest /E /MOVE /COPYALL /R:3 /W:5 /MT:8 | Out-Null
$rc = $LASTEXITCODE

if ($rc -le 7) {
    Write-Output "Move completed (Robocopy exit code $rc) ✅"
} else {
    Write-Error "Robocopy reported exit code $rc — move may have failed or be incomplete. Inspect robocopy output/logs and re-run as needed."
    exit $rc
}

# Summary counts and sizes
$srcItems = Get-ChildItem -Path $SourceFull -Recurse -File -ErrorAction SilentlyContinue
$dstItems = Get-ChildItem -Path $Dest -Recurse -File

$sc = if ($srcItems) { $srcItems.Count } else { 0 }
$dc = $dstItems.Count
$ss = if ($srcItems) { [math]::Round(($srcItems | Measure-Object -Property Length -Sum).Sum/1MB,2) } else { 0 }
$ds = [math]::Round(($dstItems | Measure-Object -Property Length -Sum).Sum/1MB,2)

Write-Output "Source remaining: $sc files, $ss MB"
Write-Output "Destination:        $dc files, $ds MB"

if ($VerifySha) {
    Write-Output "Computing SHA256 manifest (this may take some time)..."
    $manifest = Join-Path $DestinationRoot 'sha256-manifest.txt'

    Get-ChildItem -Path $Dest -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Dest.Length).TrimStart('\')
        $hash = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
        "{0}  {1}" -f $hash, $rel
    } | Out-File -FilePath $manifest -Encoding UTF8

    Write-Output "SHA256 manifest written to: $manifest"
}

if ($RunNpmBuild) {
    $buildPath = $Dest
    $pkg = Join-Path $buildPath 'package.json'
    if (Test-Path $pkg) {
        Write-Output "Running npm $NpmInstallCmd $NpmInstallArgs and npm $NpmBuildCmd $NpmBuildArgs in $buildPath"
        Push-Location $buildPath
        try {
            npm $NpmInstallCmd $NpmInstallArgs
            npm $NpmBuildCmd $NpmBuildArgs
            Write-Output "npm build completed successfully"
        } catch {
            Write-Error "npm command failed: $_"
        } finally {
            Pop-Location
        }
    } else {
        Write-Output "package.json not found in $buildPath — skipping npm build"
    }
}

Write-Output "All done."
exit 0