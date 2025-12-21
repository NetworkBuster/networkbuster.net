<#
Transform raw recycling dataset (CSV/TSV) into JSONL for training or analysis.
Usage: .\transform-recycling-data.ps1 -Input data/raw.csv -Output data/recycling.jsonl
#>
param(
  [Parameter(Mandatory=$true)][string]$Input,
  [string]$Output = 'data/recycling.jsonl'
)

if (-not (Test-Path $Input)) { Write-Error "Input not found: $Input"; exit 1 }

Get-Content $Input | ConvertFrom-Csv | ForEach-Object {
  $obj = @{ item = $_.Item; category = $_.Category; notes = $_.Notes }
  $obj | ConvertTo-Json -Depth 5
} | Out-File -FilePath $Output -Encoding utf8

Write-Output "Wrote $Output"
