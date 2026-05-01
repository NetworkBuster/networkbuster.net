<#
Simple watchdog to keep a command running and auto-restart on exit.
Usage example:
  .\watchdog.ps1 -AppExe 'C:\Program Files\nodejs\node.exe' -AppArgs 'start-servers.js' -WorkingDir 'S:\NetworkBuster_Production' -LogDir 'S:\NetworkBuster_Production\logs' -HealthUrl 'http://localhost:3001/api/health'
#>
param(
  [Parameter(Mandatory=$true)] [string]$AppExe,
  [Parameter(Mandatory=$false)] [string]$AppArgs = '',
  [string]$WorkingDir = '.',
  [string]$LogDir = '.\logs',
  [string]$HealthUrl = '',
  [int]$HealthInterval = 30,
  [int]$RestartBackoff = 5
)

# Ensure log dir
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$log = Join-Path $LogDir "watchdog.log"
function Log { param($m) $ts = (Get-Date).ToString('s'); "$ts - $m" | Out-File -FilePath $log -Append -Encoding utf8 }

Log "Watchdog starting: $AppExe $AppArgs (cwd: $WorkingDir)"

# Helper to start the app
function Start-App {
  $out = Join-Path $LogDir "app.stdout.log"
  $err = Join-Path $LogDir "app.stderr.log"
  Log "Starting app: $AppExe $AppArgs"
  $si = New-Object System.Diagnostics.ProcessStartInfo
  $si.FileName = $AppExe
  if ($AppArgs) { $si.Arguments = $AppArgs }
  $si.WorkingDirectory = $WorkingDir
  $si.RedirectStandardOutput = $true
  $si.RedirectStandardError = $true
  $si.UseShellExecute = $false
  $si.CreateNoWindow = $true

  $proc = New-Object System.Diagnostics.Process
  $proc.StartInfo = $si
  $started = $proc.Start()
  if ($started) {
    # asynchronously read output
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()
    # Wire up events
    Register-ObjectEvent -InputObject $proc -EventName Exited -Action { Log "Child process exited (code: $($Event.SourceEventArgs.ExitCode))" } | Out-Null
    return $proc
  } else {
    Log "Failed to start process."
    return $null
  }
}

# Health check function
function Check-Health {
  param($url)
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { return $true } else { return $false }
  } catch {
    return $false
  }
}

while ($true) {
  $proc = Start-App
  if (-not $proc) { Log "Start failed; sleeping $RestartBackoff seconds"; Start-Sleep -Seconds $RestartBackoff; continue }

  # Monitor loop: health checks + process exit
  while (-not $proc.HasExited) {
    Start-Sleep -Seconds 1
    if ($HealthUrl) {
      try {
        if (-not (Check-Health -url $HealthUrl)) {
          Log "Health check failed for $HealthUrl - restarting app"
          try { $proc.Kill() } catch {}
          break
        }
      } catch {
        # ignored
      }
      Start-Sleep -Seconds $HealthInterval
    }
  }

  $code = $null
  try { $code = $proc.ExitCode } catch {}
  Log "Process ended with exit code: $code. Backing off for $RestartBackoff seconds before restart."
  Start-Sleep -Seconds $RestartBackoff
}
