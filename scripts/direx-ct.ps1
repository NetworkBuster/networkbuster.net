<#
.SYNOPSIS
  direx-ct: copy and package release artifacts, labels and produce checksums/tags.

.DESCRIPTION
  Modes:
    - safe    : copy approved/staged artifacts from the DB and labels PDF to the target safe folder and produce checksums
    - current : copy the entire `releases/` directory to current snapshot folder and produce checksums
    - secure  : compute and write .sha256 files in-repo for release artifacts, optionally GPG-sign and attach to release, commit them on a new branch, and create annotated tags

  Supports DryRun to preview actions without changing repo or remote.

.EXAMPLE
  .\scripts\direx-ct.ps1 -Mode safe -DryRun
  .\scripts\direx-ct.ps1 -Mode secure -OutRoot K:\direx-ct -Branch direx-ct-batch -AttachToRelease
#>
param(
    [Parameter(Mandatory=$true)][ValidateSet('safe','current','secure')][string]$Mode,
    [switch]$DryRun,
    [string]$OutRoot = 'K:\direx-ct',
    [string]$Branch = 'direx-ct-batch',
    [switch]$GpgSign,
    [switch]$AttachToRelease,
    [string]$ReleaseTag = 'test-standstill-v1.0.0'
)

function Log { param($msg) Write-Host "[direx-ct] $msg" }
function RunIf([string]$cmd) { if ($DryRun) { Log "DRYRUN: $cmd" } else { iex $cmd } }

# helpers
function Compute-Sha256([string]$path) {
    if (-not (Test-Path $path)) { throw "File not found: $path" }
    $h = Get-FileHash -Algorithm SHA256 -Path $path
    return $h.Hash.ToLower()
}

function Write-ShaFile([string]$path, [string]$sha) {
    $shaLine = "$sha  $(Split-Path $path -Leaf)"
    if ($DryRun) { Log "Would write: $path.sha256 => $shaLine"; return }
    Set-Content -Path ($path + '.sha256') -Value $shaLine -Encoding ascii
}

function Gpg-SignIfRequested([string]$shaFile) {
    if (-not $GpgSign) { return }
    if ($DryRun) { Log "DRYRUN: gpg --detach-sign -a $shaFile"; return }
    if (-not (Get-Command gpg -ErrorAction SilentlyContinue)) { Log "gpg not found; skipping signing"; return }
    & gpg --detach-sign -a $shaFile
}

function Git-CommitAndTag([string]$message, [array]$tagInfos) {
    # tagInfos: array of @{ Name=; Message= }
    if ($DryRun) { Log "DRYRUN: git add -A; git commit -m '$message'"; foreach ($t in $tagInfos) { Log "DRYRUN: git tag -a $($t.Name) -m '$($t.Message)'" } ; return }
    git add -A
    git commit -m $message
    foreach ($t in $tagInfos) {
        git tag -a $($t.Name) -m "$($t.Message)"
    }
}

function Upload-ToRelease([string[]]$files) {
    if (-not $AttachToRelease) { return }
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Log "gh CLI not found; skipping release upload."; return }
    if ($DryRun) { Log "DRYRUN: gh release upload $ReleaseTag $($files -join ' ') --clobber"; return }
    gh release upload $ReleaseTag $files --clobber
}

# Start
Log "Mode=$Mode DryRun=$DryRun OutRoot=$OutRoot Branch=$Branch"

# Ensure OutRoot exists when not dry-run
if (-not $DryRun) { New-Item -ItemType Directory -Path $OutRoot -Force | Out-Null }

# Use database for safe mode selection
$dbPath = Join-Path 'firmware' 'checksums_db.json'
if (-not (Test-Path $dbPath)) { Log "DB not found at $dbPath" }

if ($Mode -eq 'safe') {
    $target = Join-Path $OutRoot 'safe'
    Log "Preparing safe archive -> $target"
    if (-not $DryRun) { New-Item -ItemType Directory -Path $target -Force | Out-Null }

    # copy labels PDF if present
    $labelsPdf = Join-Path 'labels' 'labels.pdf'
    if (Test-Path $labelsPdf) { RunIf "Copy-Item -Force -Path '$labelsPdf' -Destination '$target'" } else { Log "No labels PDF found at $labelsPdf" }

    # copy DB-listed files from releases
    if (Test-Path $dbPath) {
        $db = Get-Content $dbPath | ConvertFrom-Json
        foreach ($rel in $db.files.Keys) {
            $src = Join-Path 'releases' $rel
            if (Test-Path $src) {
                $dst = Join-Path $target (Split-Path $rel -Parent)
                if ($DryRun) { Log "DRYRUN: Copy $src -> $target" } else { New-Item -ItemType Directory -Path $dst -Force | Out-Null; Copy-Item -Path $src -Destination $dst -Force }
            } else { Log "Missing source: $src" }
        }
    }

    # produce checksums in target
    $filesToHash = Get-ChildItem -Path $target -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
    foreach ($f in $filesToHash) { $sha = Compute-Sha256 $f; if ($DryRun) { Log "DRYRUN: sha256 $f => $sha" } else { Set-Content -Path (Join-Path (Split-Path $f -Parent) (Split-Path $f -Leaf + '.sha256')) -Value "$sha  $(Split-Path $f -Leaf)" -Encoding ascii } }

    Log "Safe mode complete (dryrun=$DryRun)."
    exit 0
}

if ($Mode -eq 'current') {
    $target = Join-Path $OutRoot 'current'
    Log "Snapshotting releases -> $target"
    if ($DryRun) { RunIf "Copy-Item -Recurse -Force -Path 'releases\*' -Destination '$target'" } else { New-Item -ItemType Directory -Path $target -Force | Out-Null; Copy-Item -Recurse -Force -Path 'releases\*' -Destination $target }

    # produce checksums for snapshot
    $filesToHash = Get-ChildItem -Path $target -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
    foreach ($f in $filesToHash) { $sha = Compute-Sha256 $f; if ($DryRun) { Log "DRYRUN: sha256 $f => $sha" } else { Set-Content -Path ($f + '.sha256') -Value "$sha  $(Split-Path $f -Leaf)" -Encoding ascii } }

    Log "Current mode complete (dryrun=$DryRun)."
    exit 0
}

if ($Mode -eq 'secure') {
    # create and check out branch
    if ($DryRun) { Log "DRYRUN: git checkout -b $Branch" } else { git checkout -b $Branch }

    # For every file in releases, compute sha and write .sha256 next to it in repo (not in OutRoot)
    $files = Get-ChildItem -Path 'releases' -Recurse -File | Where-Object { $_.Name -notlike '*.sha256' }
    $tagInfos = @()
    foreach ($f in $files) {
        $full = $f.FullName
        $sha = Compute-Sha256 $full
        $shaFile = $full + '.sha256'
        $leaf = $f.Name
        if ($DryRun) { Log "DRYRUN: would write $shaFile with '$sha  $leaf'" } else { Set-Content -Path $shaFile -Value "$sha  $leaf" -Encoding ascii }
        Gpg-SignIfRequested $shaFile
        # prepare tag name
        $safeName = ($f.FullName -replace '[\\/]', '-') -replace '^releases-','' -replace '\s+','-'
        $short = $sha.Substring(0,12)
        $tagName = "kit-$safeName-sha256-$short"
        $tagMsg = "SHA256 for $($f.FullName): $sha"
        $tagInfos += @{ Name=$tagName; Message=$tagMsg }
    }

    $commitMsg = "Add .sha256 files via direx-ct secure mode"
    Git-CommitAndTag $commitMsg $tagInfos

    # push branch and tags
    if ($DryRun) { Log "DRYRUN: git push -u origin $Branch; git push --tags" } else { git push -u origin $Branch; git push --tags }

    # Optionally attach to release
    $shaFiles = Get-ChildItem -Path 'releases' -Recurse -Filter '*.sha256' | ForEach-Object { $_.FullName }
    Upload-ToRelease $shaFiles

    Log "Secure mode complete (dryrun=$DryRun). Created $($tagInfos.Count) tags."
    exit 0
}

Log "Unknown mode: $Mode"; exit 1
