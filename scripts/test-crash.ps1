# Simple helper to find node processes and kill them to test watchdog auto-restart
$nodes = Get-Process -Name node -ErrorAction SilentlyContinue
if (-not $nodes) { Write-Output "No node processes found"; exit 0 }
foreach ($p in $nodes) {
  Write-Output "Killing PID $($p.Id) - $($p.ProcessName)"
  try { Stop-Process -Id $p.Id -Force } catch { Write-Warning "Failed to kill $($p.Id): $($_.Exception.Message)" }
}
