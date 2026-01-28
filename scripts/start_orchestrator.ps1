# Start the AI Training orchestrator as a background process and redirect logs
$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$script = Join-Path $PSScriptRoot "run_orchestrator.py"
$logdir = Join-Path $PSScriptRoot "..\logs"
if (-not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$stdout = Join-Path $logdir "orchestrator.out.log"
$stderr = Join-Path $logdir "orchestrator.err.log"

Write-Output "Starting orchestrator: $python $script"
# Ensure Python uses UTF-8 for stdout/stderr to avoid encoding problems
$env:PYTHONIOENCODING = 'utf-8'
Start-Process -FilePath $python -ArgumentList $script -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden
Write-Output "Orchestrator started; logs: $stdout, $stderr"