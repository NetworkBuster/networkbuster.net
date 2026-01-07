# Origin: https://networkbuster.net/scripts/Grant-AdminPermissions.ps1
# Grant permissions to Project Administrators
Write-Host "Initializing Grant-AdminPermissions script..."

$ProjectRoot = "C:\Users\preci\.gemini\antigravity\scratch\networkbuster-optimizations"
$AdminGroup = "Administrators" # Generic local admin group

Write-Host "Granting Full Control to $AdminGroup on $ProjectRoot"

# Grant Full Control recursively
icacls $ProjectRoot /grant "$($AdminGroup):(OI)(CI)F" /T /C /Q

# List permissions to verify
icacls $ProjectRoot
Write-Host "Permissions update complete."
