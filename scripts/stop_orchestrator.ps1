# Stop the running orchestrator process (looks for python process running run_orchestrator.py)
$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'run_orchestrator.py' }
if (-not $procs) { Write-Output 'No orchestrator process found.'; exit 0 }
foreach ($p in $procs) {
    Write-Output "Stopping process Id $($p.ProcessId)"
    Stop-Process -Id $p.ProcessId -Force
}
Write-Output 'Orchestrator stopped.'