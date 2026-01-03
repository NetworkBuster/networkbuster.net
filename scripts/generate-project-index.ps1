<#
Generate a Markdown project index for the repository.
Creates PROJECT_INDEX.md in the repository root with a table of contents
and short descriptions for each top-level folder and notable files.

Usage: .\generate-project-index.ps1 [-OutputFile ..\PROJECT_INDEX.md]
#>
param(
  [string]$OutputFile = "$(Split-Path -Parent $PSScriptRoot)\PROJECT_INDEX.md",
  [int]$MaxFilePreviewLines = 3
)

Write-Output "Generating project index -> $OutputFile"
Write-Output "PSScriptRoot: $PSScriptRoot"
Write-Output "Computed OutputFile: $OutputFile"

function Get-DescriptionFromReadme($path) {
  $readme = Join-Path $path 'README.md'
  if (Test-Path $readme) {
    $lines = Get-Content $readme -ErrorAction SilentlyContinue | Select-Object -First 4
    $title = ($lines | Select-String -Pattern '^#\s*(.+)' -SimpleMatch | ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -First 1)
    if ($title) { return $title }
    if ($lines) { return ($lines -join ' ') }
  }
  # fallback to package.json description
  $pkg = Join-Path $path 'package.json'
  if (Test-Path $pkg) {
    try { $o = Get-Content $pkg -Raw | ConvertFrom-Json; if ($o.description) { return $o.description } } catch {}
  }
  return ''
}

function Get-FilePreview($file) {
  try { $lines = Get-Content $file -ErrorAction SilentlyContinue | Select-Object -First $MaxFilePreviewLines; return ($lines -join ' ' ) } catch { return '' }
}

$root = Split-Path -Parent $PSScriptRoot
$items = Get-ChildItem -Path $root | Where-Object { $_.Name -notlike '.git' -and $_.Name -notlike 'node_modules' } | Sort-Object PSIsContainer -Descending,Name

$md = @()
$md += "# Project Index"
$md += ""
$md += "Generated: $(Get-Date -Format 'u')"
$md += ""
$md += "## Table of Contents"
$md += ""

# Build TOC
$toc = @()
foreach ($it in $items) {
  if ($it.PSIsContainer) { $toc += "- [$($it.Name)](#${($it.Name -replace ' ','-')})" } else { $toc += "- [$($it.Name)](#${($it.Name -replace ' ','-')})" }
}
$md += $toc
$md += ""

$md += "---"
$md += ""

# Add detail sections
foreach ($it in $items) {
  $md += "### $($it.Name)"
  if ($it.PSIsContainer) {
    $desc = Get-DescriptionFromReadme $it.FullName
    if ($desc) { $md += "**Description:** $desc" }
    $md += ""
    $md += "**Contents:**"
    $md += ""
    $children = Get-ChildItem -Path $it.FullName -Force | Sort-Object PSIsContainer -Descending,Name | Select-Object -First 50
    foreach ($c in $children) {
      if ($c.PSIsContainer) { $md += "- **$($c.Name)**/" }
      else {
        $preview = Get-FilePreview $c.FullName
        if ($preview) { $md += "- $($c.Name) — `$($preview)`" } else { $md += "- $($c.Name)" }
      }
    }
    $md += ""
  } else {
    $preview = Get-FilePreview $it.FullName
    if ($preview) { $md += "`$($it.Name)` — $preview" } else { $md += "`$($it.Name)`" }
    $md += ""
  }
}

$md += "---"
$md += ""
$md += "> **Note:** If you want more detail per file/folder run the generator with a smaller `MaxFilePreviewLines` or extend the script to include file size, hash, or a deep recursive index."

$md -join "`n" | Out-File -FilePath $OutputFile -Encoding utf8 -Force

Write-Output "Project index written to $OutputFile"
