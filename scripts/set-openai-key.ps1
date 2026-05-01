<#
Set OPENAI_API_KEY for the current session or persist for the current user.

Usage:
  # Temporarily for this session:
  .\set-openai-key.ps1 -Key 'sk-...'

  # Persist for the current user (requires confirmation):
  .\set-openai-key.ps1 -Key 'sk-...' -Persist
#>
param(
  [Parameter(Mandatory=$true)][string]$Key,
  [switch]$Persist
)

Write-Output "Setting OPENAI_API_KEY for current session."
$env:OPENAI_API_KEY = $Key

if ($Persist) {
  Write-Output 'Persisting OPENAI_API_KEY for the current user using setx. This will apply to new shells only.'
  setx OPENAI_API_KEY "$Key" | Out-Null
  Write-Output 'Persisted. Restart shells to pick up the value.'
}

Write-Output 'Done.'
