<#
.SYNOPSIS
  Test AI Robot endpoint (PowerShell version).

.PARAMETER Url
  API URL (default: http://localhost:3001/api/robot)

.PARAMETER Mock
  If set, simulate responses locally without calling the API.

.PARAMETER Prompt
  One or more prompts to test.

.PARAMETER Concurrency
  Number of concurrent requests per prompt (default: 1)
#>
param(
  [string]$Url = 'http://localhost:3001/api/robot',
  [switch]$Mock,
  [int]$Concurrency = 1,
  [string[]]$Prompt
)

if (-not $Prompt -or $Prompt.Length -eq 0) {
  $Prompt = @(
    'Summarize lunar recycling best practices in one paragraph.',
    'List three risks of regolith processing on the Moon and one mitigation for each.',
    'Generate an example test query for the NetworkBuster AI robot that checks audio synthesis.'
  )
}

Write-Output "AI Robot Test - Url: $Url  Mock: $Mock  Concurrency: $Concurrency"

function Invoke-Test ($p) {
  if ($Mock) {
    return @{ message = "MOCK RESPONSE for prompt: $p" }
  }
  try {
    $body = @{ prompt = $p } | ConvertTo-Json
    $res = Invoke-RestMethod -Method Post -Uri $Url -Body $body -ContentType 'application/json' -ErrorAction Stop
    return $res
  } catch {
    throw "Request failed for prompt: $p - $($_.Exception.Message)"
  }
}

$fail = 0
foreach ($p in $Prompt) {
  Write-Output "`n== Prompt: $p =="
  if ($Concurrency -gt 1) {
    $jobs = @()
    for ($i=1; $i -le $Concurrency; $i++) {
      $jobs += Start-Job -ScriptBlock { param($prm,$u,$m) try { $b = @{ prompt=$prm } | ConvertTo-Json; if ($m) { @{ message = "MOCK" } } else { Invoke-RestMethod -Method Post -Uri $u -Body $b -ContentType 'application/json' } } catch { $_ } } -ArgumentList $p,$Url,$Mock
    }
    Receive-Job -Job $jobs -Wait | ForEach-Object {
      if ($_ -is [System.Management.Automation.ErrorRecord]) { Write-Error $_; $fail++ } else {
        if ($_ -and $_.message) { Write-Output "OK: message present" } else { Write-Warning "No message in response"; $fail++ }
      }
    }
    Remove-Job -Job $jobs
  } else {
    try {
      $res = Invoke-Test $p
      if ($res -and $res.message) { Write-Output "OK: message present" } else { Write-Warning "No message in response"; $fail++ }
    } catch {
      Write-Error $_
      $fail++
    }
  }
}

if ($fail -eq 0) { Write-Output "All tests passed!"; exit 0 } else { Write-Error "$fail tests failed"; exit 1 }