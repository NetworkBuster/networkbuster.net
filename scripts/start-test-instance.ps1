<#
Creates a test instance record that is "pending approval" and will auto-accept
after a timeout (default: 1 second). Optionally starts the Node server for the
instance if Node is available and -StartProcess is specified.

Usage:
  .\start-test-instance.ps1 -Name test1 -Port 3002 -AutoAcceptSeconds 1 -StartProcess
#>
param(
  [string]$Name = "test-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
  [int]$Port = 3002,
  [int]$AutoAcceptSeconds = 1,
  [switch]$StartProcess = $true,
  [string]$InstancesDir = 'S:\NetworkBuster_Production\instances'
)

function Resolve-InstancesDir {
  param($d)
  if (Test-Path $d) { return $d }
  $repo = (Split-Path -Parent $PSScriptRoot)
  $fallback = Join-Path $repo 'instances'
  if (-not (Test-Path $fallback)) { New-Item -ItemType Directory -Path $fallback -Force | Out-Null }
  return $fallback
}

$InstancesDir = Resolve-InstancesDir -d $InstancesDir
if (-not (Test-Path $InstancesDir)) { New-Item -ItemType Directory -Path $InstancesDir -Force | Out-Null }

$instanceFile = Join-Path $InstancesDir "$Name.json"
$record = [ordered]@{
  name = $Name
  status = 'pending'
  created = (Get-Date).ToString('o')
  port = $Port
}
$record | ConvertTo-Json -Depth 5 | Out-File -FilePath $instanceFile -Encoding utf8

Write-Host "Instance '$Name' created and is pending approval. Will auto-accept in $AutoAcceptSeconds second(s)." -ForegroundColor Cyan
Write-Host "Press 'Y' to accept now, 'N' to cancel. Waiting..."

$end = (Get-Date).AddSeconds($AutoAcceptSeconds)
$approved = $false
$cancelled = $false
while ((Get-Date) -lt $end) {
  if ([console]::KeyAvailable) {
    $k = [console]::ReadKey($true)
    if ($k.Key -eq 'Y') { $approved = $true; break }
    if ($k.Key -eq 'N') { $cancelled = $true; break }
  }
  Start-Sleep -Milliseconds 100
}

if (-not $approved -and -not $cancelled) { $approved = $true } # auto-accept on timeout

if ($cancelled) {
  $record.status = 'cancelled'
  $record.cancelledAt = (Get-Date).ToString('o')
  $record | ConvertTo-Json -Depth 5 | Out-File -FilePath $instanceFile -Encoding utf8
  Write-Host "Instance '$Name' was cancelled by user." -ForegroundColor Yellow
  exit 0
}

if ($approved) {
  $record.status = 'accepted'
  $record.approvedAt = (Get-Date).ToString('o')

  # Attempt to start the Node server for this instance if requested
  if ($StartProcess) {
    $nodeExe = 'C:\Program Files\nodejs\node.exe'
    $nodeCmd = 'node'
    if (Test-Path $nodeExe) { $nodePath = $nodeExe } else {
      $found = Get-Command node -ErrorAction SilentlyContinue
      if ($found) { $nodePath = $found.Source } else { $nodePath = $null }
    }

    if ($nodePath) {
      try {
        $startInfo = @{
          FilePath = $nodePath
          ArgumentList = 'server.js'
          WorkingDirectory = (Split-Path -Parent $PSScriptRoot)
          PassThru = $true
        }
        $env:PORT = $Port
        $p = Start-Process @startInfo
        Start-Sleep -Seconds 1
        $record.processId = $p.Id
        $record.processStarted = (Get-Date).ToString('o')
        Write-Host "Started Node server for instance '$Name' (PID: $($p.Id))" -ForegroundColor Green
      } catch {
        $record.processError = $_.Exception.Message
        Write-Host "Failed to start Node server: $($_.Exception.Message)" -ForegroundColor Red
      }
    } else {
      Write-Host "Node runtime not found; skipping process start." -ForegroundColor Yellow
      $record.processSkipped = $true
    }
  }

  $record | ConvertTo-Json -Depth 10 | Out-File -FilePath $instanceFile -Encoding utf8
  Write-Host "Instance '$Name' accepted and updated: $instanceFile" -ForegroundColor Green
}

# Print summary
Get-Content $instanceFile -Raw | Write-Output
