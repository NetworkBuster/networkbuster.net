<#
render-local.ps1

Convenience helper to render Mermaid `.mmd` files to SVG and then to PNG locally.

What it does:
- Verifies Node.js is available, otherwise downloads a portable Node zip into `tools/node-<ver>` and uses it for the session
- Runs `npx @mermaid-js/mermaid-cli` to render `.mmd` -> `.svg`
- Installs `puppeteer` (may download Chromium) and runs `node scripts/render-svgs.js` to convert SVG -> PNG
- Lists output PNG files in `docs/diagrams`

Usage examples:
  # Run with defaults (portable node if missing):
  .\scripts\render-local.ps1

  # Force using nvm-windows installer (requires UAC):
  .\scripts\render-local.ps1 -UseNvm -AcceptUAC

  # Skip Chromium download (not recommended unless you already have Chromium available):
  .\scripts\render-local.ps1 -SkipChromiumDownload
#>

param(
  [switch]$UseNvm,
  [switch]$AcceptUAC,
  [switch]$SkipChromiumDownload,
  [switch]$LongTimeout,
  [int]$RenderScale = 2
)

# Configure timeouts/retries
$nodeDownloadWaitMax = if ($LongTimeout) { 300 } else { 60 }
$pScreensScale = $RenderScale
$pptInstallRetries = if ($LongTimeout) { 5 } else { 2 }
$pptInstallBackoffSeconds = if ($LongTimeout) { 30 } else { 10 }

function Fail([string]$m) { Write-Error $m; exit 1 }

Write-Output "Starting local render helper"

# Ensure we are running from repo root
Push-Location -Path (Join-Path $PSScriptRoot '..') | Out-Null

# 1) Ensure Node exists (session PATH)
$nodeOK = $false
try { $nv = & node --version 2>$null; if ($LASTEXITCODE -eq 0) { Write-Output "Found node: $nv"; $nodeOK = $true } } catch { }

if (-not $nodeOK) {
  if ($UseNvm) {
    Write-Output "nvm installer chosen. Running scripts/install-nvm.ps1 (requires -AcceptUAC to proceed)."
    if (-not $AcceptUAC) { Fail 'nvm install requested but -AcceptUAC not provided. Rerun with -AcceptUAC to proceed.' }
    & powershell -ExecutionPolicy Bypass -File scripts/install-nvm.ps1 -AcceptUAC
    Write-Output "After nvm install, please re-open your shell or restart this PowerShell session and run this script again. Exiting."
    exit 0
  }

  # Try portable Node zip method
  Write-Output 'Node not found. Attempting to download and extract a portable Node 24.x ZIP to tools/ (no UAC required).'
  $tools = Join-Path (Get-Location) 'tools'
  if (-not (Test-Path $tools)) { New-Item -ItemType Directory -Path $tools | Out-Null }
  # Prefer index.json to reliably pick the latest v24 release
  $indexJsonUrl = 'https://nodejs.org/dist/index.json'
  try {
    $indexJson = Invoke-WebRequest -Uri $indexJsonUrl -UseBasicParsing -ErrorAction Stop
    $json = $indexJson.Content | ConvertFrom-Json
  } catch {
    Fail "Failed to fetch Node index JSON: $($_.Exception.Message)"
  }
  $entry = $json | Where-Object { $_.version -match '^v24\.' } | Select-Object -First 1
  if (-not $entry) { Fail 'No Node 24.x release found in index.json' }
  $ver = $entry.version.TrimStart('v')
  $zipName = "node-v${ver}-win-x64.zip"
  $zipUrl = "https://nodejs.org/dist/v${ver}/$zipName"
  $tmp = Join-Path $env:TEMP $zipName
  Write-Output "Downloading $zipUrl to $tmp"
  Invoke-WebRequest -Uri $zipUrl -OutFile $tmp -UseBasicParsing -ErrorAction Stop

  # Wait until file is stable
  $prev = -1
  for ($i=0;$i -lt 60;$i++) {
    if (Test-Path $tmp) {
      $s = (Get-Item $tmp).Length
      Write-Output "  size=$s"
      if ($s -gt 1024*1024 -and $s -eq $prev) { break }
      $prev = $s
    }
    Start-Sleep -Seconds 1
  }
  if (-not (Test-Path $tmp)) { Fail "Download failed: $tmp missing" }
  if ((Get-Item $tmp).Length -lt 1024*1024) { Fail "Downloaded Node zip appears too small" }

  $dest = Join-Path $tools ('node-'+$ver)
  if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
  Write-Output "Extracting to $dest"
  Expand-Archive -Path $tmp -DestinationPath $tools -Force
  if (Test-Path (Join-Path $tools ('node-v'+$ver))) { Rename-Item -Path (Join-Path $tools ('node-v'+$ver)) -NewName ('node-'+$ver) -Force }
  if (-not (Test-Path $dest)) { Fail 'Node extraction failed' }
  $nodeBin = Join-Path $dest 'node.exe'
  if (-not (Test-Path $nodeBin)) { Fail 'node.exe not found after extraction' }

  # Use node from extracted tools for this session
  $env:PATH = (Split-Path $nodeBin) + ';' + $env:PATH
  Write-Output "Using portable node: $(node --version)"
}

# Wait-for-download stability: ensure file size stabilizes before continuing
Write-Output "Waiting up to $nodeDownloadWaitMax seconds for the Node ZIP to stabilize"
$prev = -1
$stable = $false
for ($i=0;$i -lt $nodeDownloadWaitMax;$i++) {
    if (Test-Path $tmp) {
        $s = (Get-Item $tmp).Length
        Write-Output "  size=$s"
        if ($s -gt 1024*1024 -and $s -eq $prev) { $stable = $true; break }
        $prev = $s
    }
    Start-Sleep -Seconds 1
}
if (-not $stable) { Write-Warning "Node ZIP may not have stabilized after $nodeDownloadWaitMax seconds; proceeding but results may vary" }

# 2) Ensure mermaid CLI + render mmd->svg
Write-Output 'Rendering Mermaid sources (.mmd -> .svg) using npx @mermaid-js/mermaid-cli'
try {
  npx -y @mermaid-js/mermaid-cli -i "docs/diagrams/*.mmd" -o docs/diagrams -f svg --logLevel debug
  Write-Output 'Mermaid rendering complete.'
} catch {
  Write-Error "Mermaid rendering failed: $($_.Exception.Message)"; exit 2
}

# 3) Install puppeteer and run renderer (with retries/backoff if requested)
if (-not $SkipChromiumDownload) {
  Write-Output 'Installing puppeteer (this will download Chromium). This can take several minutes.'
  $success = $false
  for ($try=1; $try -le $pptInstallRetries; $try++) {
    Write-Output "Attempt $try of $($pptInstallRetries): npm install puppeteer --no-audit --no-fund"
    try {
      npm install puppeteer --no-audit --no-fund
      if ($LASTEXITCODE -eq 0) { $success = $true; break }
      Write-Warning "npm exited with code $LASTEXITCODE"
    } catch {
      Write-Warning "Install attempt failed: $($_.Exception.Message)"
    }

    if ($try -lt $pptInstallRetries) {
      $wait = $pptInstallBackoffSeconds * $try
      Write-Output "Waiting $wait seconds before retrying..."
      Start-Sleep -Seconds $wait
    }
  }
  if (-not $success) { Write-Error "Failed to install puppeteer after $pptInstallRetries attempts"; exit 4 }
} else {
  Write-Output 'Skipping Chromium download as requested (-SkipChromiumDownload). Ensure you have a Chromium available in PATH.'
}

# 4) Run the renderer
Write-Output "Running Node renderer: node scripts/render-svgs.js $pScreensScale"
try {
  node scripts/render-svgs.js $pScreensScale
} catch {
  Write-Error "Renderer failed: $($_.Exception.Message)"; exit 3
}

# 5) Show results
Write-Output 'PNG generation complete. Listing PNGs in docs/diagrams:'
Get-ChildItem -Path docs/diagrams -Recurse -Filter '*.png' | Select-Object FullName,Length | Format-Table -AutoSize

Write-Output 'Done. If PNGs are missing, consider re-running with -SkipChromiumDownload:$false and check network/firewall settings or run the CI with enhanced logging.'

Pop-Location | Out-Null
