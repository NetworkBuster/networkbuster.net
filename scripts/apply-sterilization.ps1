Param(
  [string]$InstrumentId = '',
  [string]$InstrumentModel = '',
  [string]$Technician = $env:USERNAME,
  [string]$Location = '',
  [string]$Notes = '',
  [switch]$Commit,
  [switch]$DryRun
)

# Safe default locations
$recordsDir = 'S:\NetworkBuster_Production\data\sterilization-records'
if (-not (Test-Path $recordsDir)) { New-Item -ItemType Directory -Path $recordsDir -Force | Out-Null }

$timestamp = (Get-Date).ToString('s')
$fname = Join-Path $recordsDir ("sterilization_{0}_{1}.md" -f $timestamp.Replace(':','-'), ($InstrumentId -replace '[^\w\-]','_'))

$content = @()
$content += "# Sterilization Record"
$content += "date: $timestamp"
$content += "technician: $Technician"
if ($InstrumentId) { $content += "instrument_id: $InstrumentId" }
if ($InstrumentModel) { $content += "instrument_model: $InstrumentModel" }
if ($Location) { $content += "location: $Location" }
$content += "notes: "$Notes""

# Append a short checklist stub
$content += ''
$content += 'checklist:'
$content += '  pre_clean: false'
$content += '  mechanical_clean: false'
$content += '  disinfection: false'
$content += '  uvc_used: false'
$content += '  functional_check: false'

if ($DryRun) {
  Write-Output "DRYRUN: Would write record to: $fname"
  $content | ForEach-Object { Write-Output $_ }
  exit 0
}

$content -join "`n" | Out-File -FilePath $fname -Encoding UTF8
Write-Output "Wrote sterilization record: $fname"

if ($Commit) {
  git add $fname
  git commit -m "chore: add sterilization record for $InstrumentId by $Technician" || Write-Output "No changes to commit"
  git push origin HEAD || Write-Warning "Push failed"
}
