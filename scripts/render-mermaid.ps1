<#
Render Mermaid `.mmd` files in `docs/diagrams` to SVG using `@mermaid-js/mermaid-cli` via npx.
It attempts to use the repo-local Node if present, or system `npx` otherwise.

Usage: .\render-mermaid.ps1 [-OutDir docs/diagrams]
#>
param(
  [string]$DiagDir = 'docs/diagrams',
  [string]$OutDir = 'docs/diagrams'
)

function Find-Node {
  $candidates = @('C:\\Program Files\\nodejs\\node.exe', (Get-Command node -ErrorAction SilentlyContinue).Path, 'tools\\node\\node.exe')
  foreach ($c in $candidates) { if ($c -and (Test-Path $c)) { return $c } }
  return $null
}

$node = Find-Node
if (-not $node) { Write-Warn 'Node not found in PATH or tools/node; rendering requires Node and npx/mermaid-cli; skipping.'; exit 0 }

$mmds = Get-ChildItem -Path $DiagDir -Filter '*.mmd' -ErrorAction SilentlyContinue
if (-not $mmds) { Write-Output 'No .mmd files found'; exit 0 }

foreach ($f in $mmds) {
  $in = $f.FullName
  $out = Join-Path $OutDir ($f.BaseName + '.svg')
  Write-Output "Rendering $in -> $out"
  & npx -y @mermaid-js/mermaid-cli -i "$in" -o "$OutDir" -f svg || Write-Warn "Failed to render $in"
}

Write-Output 'Render complete.'
