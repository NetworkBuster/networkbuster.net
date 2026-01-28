Param(
  [string]$Source = 'S:\NetworkBuster_Production',
  [string]$Dest = 'E:\DATACENTRA',
  [switch]$CompareOnly
)

Function Require-Admin {
  if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Output "Re-launching as Administrator..."

    # If F: is available, copy the script there and run from F: so elevated session uses F:\ context
    $runFromF = $false
    if (Test-Path 'F:\') {
      try {
        $destDir = 'F:\scripts'
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        $destPath = Join-Path $destDir (Split-Path $PSCommandPath -Leaf)
        Copy-Item -Path $PSCommandPath -Destination $destPath -Force
        $runFromF = Test-Path $destPath
        if ($runFromF) { Write-Output "Copied script to $destPath and will relaunch from F: drive" }
      } catch {
        Write-Warning "Could not prepare F: relaunch: $($_.Exception.Message)"
        $runFromF = $false
      }
    }

    if ($runFromF) {
      $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$destPath,'-Source',$Source,'-Dest',$Dest)
      Start-Process -FilePath powershell -ArgumentList $args -Verb RunAs
    } else {
      $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath,'-Source',$Source,'-Dest',$Dest)
      Start-Process -FilePath powershell -ArgumentList $args -Verb RunAs
    }
    Exit
  }
}

Require-Admin

Write-Output "Installing DATACENTRA from $Source to $Dest"

# Ensure dest exists
if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }

# Files to copy
$files = @(
  'docs\\AI_TRAINING_AND_DATA_PERSONALIZATION.md',
  'challengerepo\\real-time-overlay\\src\\components\\ImmersiveReader.jsx',
  'challengerepo\\real-time-overlay\\src\\App.jsx'
)

foreach ($f in $files) {
  $s = Join-Path $Source $f
  $d = Join-Path $Dest $f
  if (Test-Path $s) {
    $dDir = Split-Path $d -Parent
    if (-not (Test-Path $dDir)) { New-Item -ItemType Directory -Path $dDir -Force | Out-Null }
    Copy-Item -Path $s -Destination $d -Force
    Write-Output "Copied: $f"
  } else {
    Write-Output "Missing source: $s"
  }
}

# Compare AI training related files and produce a diff report
$report = Join-Path $Source 'data\\datacentra-diff.txt'
Write-Output "Comparing AI training files and writing report to $report"
"DATACENTRA diff report - $(Get-Date -Format s)" | Out-File $report
foreach ($f in $files) {
  $sPath = Join-Path $Source $f
  $dPath = Join-Path $Dest $f
  if (Test-Path $sPath -and Test-Path $dPath) {
    $sHash = Get-FileHash -Algorithm SHA256 -Path $sPath | Select-Object -ExpandProperty Hash
    $dHash = Get-FileHash -Algorithm SHA256 -Path $dPath | Select-Object -ExpandProperty Hash
    if ($sHash -eq $dHash) {
      "MATCH: $f" | Out-File -Append $report
    } else {
      "DIFFER: $f" | Out-File -Append $report
      "  SourceHash: $sHash" | Out-File -Append $report
      "  DestHash:   $dHash" | Out-File -Append $report
    }
  } else {
    "MISSING: $f (source or dest missing)" | Out-File -Append $report
  }
}

Write-Output "Install and compare complete. Report: $report"
