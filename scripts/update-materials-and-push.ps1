Param(
  [switch]$Push = $false
)

$items = @(
  'Nitrile gloves',
  'N95 respirators or PAPRs',
  'Safety goggles / face shields',
  'Lint-free wipes (microfiber)',
  'Sterile swabs (foam tipped)',
  'Isopropyl alcohol (70%–90%)',
  'Manufacturer-approved optical cleaning fluids',
  'HEPA portable air purifier',
  'UV-C lamp (supplementary only)',
  'Disposable gowns / shoe covers',
  'Sealable waste bags'
)

$md = 'MATERIALS.md'
if (-not (Test-Path $md)) { throw "$md not found" }

$content = Get-Content -Raw -Path $md
foreach ($it in $items) {
  if ($content -notmatch [regex]::Escape($it)) {
    Add-Content -Path $md -Value "- $it"
    Write-Output "Added: $it"
  } else {
    Write-Output "Already present: $it"
  }
}

if ($Push) {
  git add $md
  git commit -m "docs: add sterilization supplies to MATERIALS.md" || Write-Output "No changes to commit"
  git push origin HEAD || Write-Warning "Push failed"
}
