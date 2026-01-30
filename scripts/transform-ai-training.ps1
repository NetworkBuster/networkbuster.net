Param(
  [string]$Source = 'E:\DATACENTRA',
  [string]$Output = 'E:\DATACENTRA\data\training.jsonl',
  [switch]$VerboseOutput,
  [string]$VpnName = '',
  [string]$VpnUser = '',
  [string]$VpnPass = ''
)

# VPN helper functions (uses rasdial for Windows VPN connections)
function Connect-Vpn {
  param($Name, $User, $Pass)
  if (-not $Name) { return $false }
  Write-Output "Attempting to connect VPN: $Name"
  try {
    $args = @($Name)
    if ($User) { $args += $User; $args += $Pass }
    $out = & rasdial @args 2>&1
    Write-Output $out
    if ($out -match 'Command completed successfully') { return $true } else { return $false }
  } catch {
    Write-Warning "Failed to run rasdial: $($_.Exception.Message)"; return $false
  }
}

function Disconnect-Vpn {
  param($Name)
  if (-not $Name) { return }
  try { & rasdial $Name /disconnect 2>&1 | Write-Output } catch { }
}

# Track VPN state for cleanup
$vpnConnected = $false
if ($VpnName) {
  $vpnConnected = Connect-Vpn -Name $VpnName -User $VpnUser -Pass $VpnPass
  if ($vpnConnected) { Write-Output "VPN $VpnName connected" } else { Write-Warning "VPN $VpnName not connected" }

  # Optional: set proxy env vars if needed for downstream tools
  if ($env:HTTP_PROXY -or $env:HTTPS_PROXY) {
    Write-Output "Using existing proxy settings from environment"
  }
}

# Ensure we disconnect VPN on exit
$exitAction = {
  if ($vpnConnected -and $VpnName) {
    Write-Output "Disconnecting VPN $VpnName"
    Disconnect-Vpn -Name $VpnName
  }
}
Register-EngineEvent PowerShell.Exiting -Action $exitAction | Out-Null

Function Ensure-Dir {
  param($p)
  $d = Split-Path $p -Parent
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

Ensure-Dir -p $Output

Write-Output "Transforming AI training files from $Source -> $Output"

$patterns = @('*.md','*.jsx','*.js','*.txt')
$files = @()
foreach ($pat in $patterns) { $files += Get-ChildItem -Path $Source -Recurse -Force -Include $pat -File -ErrorAction SilentlyContinue }
$seen = @{}
$outRows = @()

foreach ($file in $files) {
  try {
    $text = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
  } catch {
    Write-Warning "Failed to read $($file.FullName): $($_.Exception.Message)"; continue
  }

  $ext = $file.Extension.ToLower()
  $blocks = @()

  if ($ext -eq '.md') {
    # Remove code fences and HTML comments
    $clean = [regex]::Replace($text, '```.*?```', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $clean = [regex]::Replace($clean, '<!--.*?-->', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    # Split into paragraphs
    $para = $clean -split "\r?\n\r?\n" | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 20 }
    $blocks += $para
  } elseif ($ext -in @('.jsx','.js')) {
    # Extract template text from JSX: text nodes between > and < and string literals
    $jsxText = [regex]::Matches($text, '>([^<>]{20,})<') | ForEach-Object { $_.Groups[1].Value.Trim() }
    $strLits = [regex]::Matches($text, '`([^`]{20,})`', [System.Text.RegularExpressions.RegexOptions]::Singleline) | ForEach-Object { $_.Groups[1].Value.Trim() }
    $singleD = [regex]::Matches($text, '"([^"]{20,})"') | ForEach-Object { $_.Groups[1].Value.Trim() }
    $singleS = [regex]::Matches($text, "'([^']{20,})'") | ForEach-Object { $_.Groups[1].Value.Trim() }
    $blocks += $jsxText; $blocks += $strLits; $blocks += $singleD; $blocks += $singleS
  } else {
    # plain text or others
    $clean = $text -replace '\r?\n', ' \n '
    $lines = $clean -split '\n' | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 20 }
    $blocks += $lines
  }

  foreach ($b in $blocks) {
    # Normalize
    $n = $b -replace '\s+', ' ' -replace 'https?://\S+','' -replace '\S+@\S+',''
    $n = $n.Trim()
    if ($n.Length -lt 30) { continue }
    # Deduplicate
    $key = ([Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($n)))
    if ($seen.ContainsKey($key)) { continue }
    $seen[$key] = $true

    $obj = [PSCustomObject]@{
      source = ($file.FullName -replace "^$Source\\?", '')
      path = $file.FullName
      type = $ext
      text = $n
      length = $n.Length
      timestamp = (Get-Date -Format s)
    }
    $outRows += ($obj | ConvertTo-Json -Compression)
  }
}

# Write JSONL
Set-Content -Path $Output -Value $outRows -Encoding UTF8
$hash = Get-FileHash -Algorithm SHA256 -Path $Output | Select-Object -ExpandProperty Hash
Write-Output "Wrote $($outRows.Count) records to $Output (sha256: $hash)"

# Mirror to S: module location if exists
$moduleOut = 'S:\NetworkBuster_Production\modules\datacentra\data\training.jsonl'
Ensure-Dir -p $moduleOut
Copy-Item -Path $Output -Destination $moduleOut -Force
Write-Output "Mirrored training dataset to $moduleOut"
