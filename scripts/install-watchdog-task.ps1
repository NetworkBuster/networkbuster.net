<#
Install a Scheduled Task (current user) to run the watchdog at logon and keep it running.
Usage (run once):
  .\install-watchdog-task.ps1 -WatchdogPath 'C:\path\to\watchdog.ps1' -NodePath 'C:\Program Files\nodejs\node.exe' -AppArgs 'S:\NetworkBuster_Production\start-servers.js' -LogDir 'S:\NetworkBuster_Production\logs'
#>
param(
  [Parameter(Mandatory=$true)] [string]$WatchdogPath,
  [Parameter(Mandatory=$true)] [string]$NodePath,
  [string]$AppArgs = 'S:\NetworkBuster_Production\start-servers.js',
  [string]$WorkingDir = 'S:\NetworkBuster_Production',
  [string]$LogDir = 'S:\NetworkBuster_Production\logs',
  [string]$TaskName = 'NetworkBusterWatchdog'
)

# Build action command
$action = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$WatchdogPath`" -AppExe `"$NodePath`" -AppArgs `"$AppArgs`" -WorkingDir `"$WorkingDir`" -LogDir `"$LogDir`" -HealthUrl `"http://localhost:3001/api/health`" -HealthInterval 30 -RestartBackoff 5"

# Create task trigger: At log on for current user
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel LeastPrivilege
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable
$actionObj = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"& { $action }\""

try {
  Register-ScheduledTask -TaskName $TaskName -Action $actionObj -Trigger $trigger -Settings $settings -Principal $principal -Force
  Write-Output "Scheduled task '$TaskName' registered for user $env:USERNAME"
} catch {
  Write-Error "Failed to register scheduled task: $($_.Exception.Message)"
}
