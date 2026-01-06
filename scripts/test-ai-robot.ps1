<#
.SYNOPSIS
  Test AI Robot endpoint (PowerShell version).

.PARAMETER Url
  API URL (default: http://localhost:3001/api/robot)

.PARAMETER Mock
  If set, simulate responses locally without calling the API.

.PARAMETER Prompt
  One or more prompts to test.

.PARAMETER Concurrency
  Number of concurrent requests per prompt (default: 1)
#>
param(
  [string]$Url = 'http://localhost:3001/api/robot',
  [switch]$Mock,
  [int]$Concurrency = 1,
  [string[]]$Prompt,
  [switch]$EnsureWsl,
  [string[]]$WslPaths = @('\\wsl.localhost\Ubuntu','\\wsl.localhost\docker-desktop'),
  [int]$EnsureWslTimeout = 30,
  [switch]$MapWslDrive,
  [string]$MapDriveName = 'networkbustersetup',
  [switch]$MapDriveLetter,
  [ValidatePattern('^[A-Z]$')][string]$DriveLetter = 'K',
  [string]$DriveLabel = 'setup'
)

if (-not $Prompt -or $Prompt.Length -eq 0) {
  $Prompt = @(
    'Summarize lunar recycling best practices in one paragraph.',
    'List three risks of regolith processing on the Moon and one mitigation for each.',
    'Generate an example test query for the NetworkBuster AI robot that checks audio synthesis.'
  )
}

Write-Output "AI Robot Test - Url: $Url  Mock: $Mock  Concurrency: $Concurrency"

# Launch the provided Windows shortcut if present (useful for starting Linux VM or related tools)
$ShortcutPath = 'C:\Users\daypi\OneDrive\Desktop\Linux - Shortcut.lnk'
if ($env:OS -eq 'Windows_NT' -and (Test-Path $ShortcutPath)) {
  try {
    Write-Output "Launching shortcut: $ShortcutPath"
    Start-Process -FilePath $ShortcutPath -ErrorAction Stop
    Write-Output "Launched shortcut successfully."
  } catch {
    Write-Warning "Failed to launch shortcut $ShortcutPath - $($_.Exception.Message)"
  }
} else {
  Write-Output "Shortcut not found or not running on Windows; skipping launch."
}

# Ensure WSL UNC paths are available and optionally map one to a PSDrive
if ($env:OS -eq 'Windows_NT' -and $EnsureWsl) {
  function Start-And-Wait-For-Path {
    param(
      [string]$Path,
      [int]$TimeoutSeconds
    )
    if (Test-Path $Path) { Write-Output "Accessible: $Path"; return $true }
    Write-Output "$Path not accessible. Attempting to start corresponding WSL distro..."
    if ($Path -match '\\\\wsl\.localhost\\([^\\]+)') {
      $distro = $Matches[1]
      try {
        Write-Output "Starting WSL distro: $distro"
        Start-Process -FilePath 'wsl.exe' -ArgumentList '-d',$distro,'--','echo','starting' -NoNewWindow -Wait -ErrorAction Stop
      } catch {
        Write-Warning "Failed to start WSL distro $distro - $($_.Exception.Message)"
      }
    } else {
      Write-Warning "Could not determine distro name from path $Path"
    }
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
      if (Test-Path $Path) { Write-Output "Now accessible: $Path"; return $true }
      Start-Sleep -Seconds 1
    }
    Write-Warning "Timed out waiting for $Path to become available"
    return $false
  }

  foreach ($p in $WslPaths) {
    try {
      $ok = Start-And-Wait-For-Path -Path $p -TimeoutSeconds $EnsureWslTimeout
      if ($ok) {
        if ($MapWslDrive) {
          try {
            if (Get-PSDrive -Name $MapDriveName -ErrorAction SilentlyContinue) {
              Remove-PSDrive -Name $MapDriveName -Force -ErrorAction SilentlyContinue
            }
            New-PSDrive -Name $MapDriveName -PSProvider FileSystem -Root $p -ErrorAction Stop | Out-Null
            Write-Output "Mapped $p to PSDrive $MapDriveName"
          } catch {
            Write-Warning "Failed to map $p to drive $MapDriveName - $($_.Exception.Message)"
          }
        }
        if ($MapDriveLetter) {
          try {
            if (Get-PSDrive -Name $DriveLetter -ErrorAction SilentlyContinue) {
              Remove-PSDrive -Name $DriveLetter -Force -ErrorAction SilentlyContinue
            }
            New-PSDrive -Name $DriveLetter -PSProvider FileSystem -Root $p -ErrorAction Stop | Out-Null
            Write-Output ("Mapped {0} to drive {1}:" -f $p, $DriveLetter)
            if ($DriveLabel) {
              $labelDir = Join-Path "$($DriveLetter):" $DriveLabel
              if (-not (Test-Path $labelDir)) { New-Item -Path $labelDir -ItemType Directory -Force | Out-Null }
              Write-Output "Created folder: $labelDir"
            }
          } catch {
            Write-Warning ("Failed to map {0} to drive {1} - {2}" -f $p, $DriveLetter, $_.Exception.Message)
          }
        }
        break
      }
    } catch {
      Write-Warning "Unexpected error ensuring WSL path $p - $($_.Exception.Message)"
    }
  }
}
function Invoke-Test ($p) {
  if ($Mock) {
    return @{ message = "MOCK RESPONSE for prompt: $p" }
  }
  try {
    $body = @{ prompt = $p } | ConvertTo-Json
    $res = Invoke-RestMethod -Method Post -Uri $Url -Body $body -ContentType 'application/json' -ErrorAction Stop
    return $res
  } catch {
    throw "Request failed for prompt: $p - $($_.Exception.Message)"
  }
}

$fail = 0
foreach ($p in $Prompt) {
  Write-Output "`n== Prompt: $p =="
  if ($Concurrency -gt 1) {
    $jobs = @()
    for ($i=1; $i -le $Concurrency; $i++) {
      $jobs += Start-Job -ScriptBlock { param($prm,$u,$m) try { $b = @{ prompt=$prm } | ConvertTo-Json; if ($m) { @{ message = "MOCK" } } else { Invoke-RestMethod -Method Post -Uri $u -Body $b -ContentType 'application/json' } } catch { $_ } } -ArgumentList $p,$Url,$Mock
    }
    Receive-Job -Job $jobs -Wait | ForEach-Object {
      if ($_ -is [System.Management.Automation.ErrorRecord]) { Write-Error $_; $fail++ } else {
        if ($_ -and $_.message) { Write-Output "OK: message present" } else { Write-Warning "No message in response"; $fail++ }
      }
    }
    Remove-Job -Job $jobs
  } else {
    try {
      $res = Invoke-Test $p
      if ($res -and $res.message) { Write-Output "OK: message present" } else { Write-Warning "No message in response"; $fail++ }
    } catch {
      Write-Error $_
      $fail++
    }
  }
}

if ($fail -eq 0) { Write-Output "All tests passed!"; exit 0 } else { Write-Error "$fail tests failed"; exit 1 }