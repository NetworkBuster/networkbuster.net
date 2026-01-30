<#
.SYNOPSIS
  Sync two drives (S: and E:) using Git when available, otherwise using Robocopy.

.DESCRIPTION
  This script attempts a Git-based mirror if Git is installed and the user requests it. If Git is not available or the "-UseGit:$false" flag is passed, it falls back to using Robocopy mirroring (/MIR).

.PARAMETER Source
  Source path to sync from (default: S:\NetworkBuster_Production)

.PARAMETER Dest
  Destination path to sync to (default: E:\NetworkBuster_Backup)

.PARAMETER UseGit
  Whether to prefer Git-based sync. Defaults to $true.

.PARAMETER DryRun
  If set, shows commands without executing (Robocopy uses /L)

.PARAMETER Log
  Log file path (default: .\sync-drives.log)

.EXAMPLE
  .\sync-drives.ps1 -Source 'S:\NetworkBuster_Production' -Dest 'E:\NetworkBuster_Backup' -UseGit $true

#>
param(
  [string]$Source = 'S:\NetworkBuster_Production',
  [string]$Dest = 'E:\NetworkBuster_Backup',
  [bool]$UseGit = $true,
  [ValidateSet('push','pull','mirror')][string]$Direction = 'push',
  [switch]$Reverse,
  [switch]$DryRun,
  [string]$Log = '.\sync-drives.log'
)

# Support reverse/pull modes: -Reverse or -Direction pull will swap Source and Dest
if ($Reverse -or $Direction -eq 'pull') {
  Log "Reverse/pull mode enabled — swapping Source and Dest"
  $tmp = $Source; $Source = $Dest; $Dest = $tmp
  Log "Source is now: $Source"
  Log "Dest is now:   $Dest"
}

function Log { param($m) Write-Output $m; Add-Content -Path $Log -Value ("$(Get-Date -Format s) - $m") }

# Validate paths
if (-not (Test-Path $Source)) { Log "Source not found: $Source"; throw "Source not found: $Source" }
if (-not (Test-Path $Dest)) { Log "Destination not found; creating: $Dest"; New-Item -ItemType Directory -Path $Dest -Force | Out-Null }

# Detect Git
$git = Get-Command git -ErrorAction SilentlyContinue
if ($UseGit -and $git) {
  Log "Git detected at $($git.Path). Proceeding with Git-based mirror."

  # Prepare bare repo on destination
  $bare = Join-Path $Dest 'networkbuster.git'
  if (-not (Test-Path $bare)) {
    Log "Creating bare repository at $bare"
    if ($DryRun) { Log "DryRun: git init --bare $bare" } else { & git init --bare "$bare" } 
  } else {
    Log "Bare repository already exists at $bare"
  }

  # Initialize and commit in source if needed
  Push-Location $Source
  try {
    if (-not (Test-Path (Join-Path $Source '.git'))) {
      Log "Initializing git repository in source: $Source"
      if ($DryRun) { Log "DryRun: git init" } else { & git init } 
      if ($DryRun) { Log "DryRun: git add . ; git commit -m 'Initial commit for sync'" } else { & git add .; & git commit -m "Sync commit: $(Get-Date -Format s)" -a } 
    } else {
      Log ".git exists; committing current changes"
      if (-not $DryRun) { & git add .; & git commit -m "Sync commit: $(Get-Date -Format s)" -a } else { Log "DryRun: git add . ; git commit -m 'Sync commit' -a" }
    }

    # Add remote and push
    if ($DryRun) { Log "DryRun: git remote add backup $bare ; git push --mirror backup" } else {
      try { & git remote remove backup 2>$null } catch { }
      try { & git remote add backup "$bare" 2>$null } catch { }
      & git push --mirror backup
    }
  } finally {
    Pop-Location
  }

  Log "Git-based sync completed."
  exit 0
}

# Fallback: Robocopy mirroring
Log "Git not used or not available. Falling back to Robocopy mirror."
$rcArgs = @($Source, $Dest, "/MIR", "/COPYALL", "/R:3", "/W:5", "/MT:16")
$display = "robocopy `"$Source`" `"$Dest`" /MIR /COPYALL /R:3 /W:5 /MT:16"
if ($DryRun) { Log "DryRun Robocopy: $display /L"; exit 0 }

Log "Executing: $display"
# Execute robocopy with arguments
try {
  & robocopy @rcArgs | Tee-Object -FilePath $Log -Append
  Log "Robocopy sync completed."
} catch {
  Log "Robocopy failed: $($_.Exception.Message)"
  exit 1
}

