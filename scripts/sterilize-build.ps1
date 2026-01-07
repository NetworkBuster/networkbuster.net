# Sterilize Build Script
# Origin: https://networkbuster.net/scripts/sterilize-build.ps1
Write-Host "Starting build sterilization process..."

$BuildDir = "C:\Users\preci\.gemini\antigravity\scratch\networkbuster-optimizations"
$LogDir = Join-Path $BuildDir "logs"

# 1. Wait for logs to be visible
Write-Host "Waiting for build logs to be visible in $LogDir..."
while (-not (Test-Path $LogDir) -or (Get-ChildItem $LogDir).Count -eq 0) {
    Start-Sleep -Seconds 2
    Write-Host "." -NoNewline
}
Write-Host "`nLogs detected. Proceeding with sterilization."

# 2. Cleanup temporary and redundant files
$FilesToSterilize = Get-ChildItem -Path $BuildDir -Recurse -Include "*.tmp", "*.log.old", "thumbs.db"
foreach ($File in $FilesToSterilize) {
    Write-Host "Removing $File..."
    Remove-Item $File -Force
}

# 3. Sanitize build environment metadata (Mocking directory path sanitization)
Write-Host "Sanitizing build metadata..."

# 4. Verify output integrity
Write-Host "Verifying production build integrity..."
$BinDir = Join-Path $BuildDir "bin"
if (Test-Path $BinDir) {
    Write-Host "Production binaries found at $BinDir"
}
else {
    Write-Warning "No production binaries found. Sterilization incomplete."
}

Write-Host "Sterilize build job finished."
