# Make a standstill release of the integration test (Windows PowerShell)
# Usage: .\make_standstill_release.ps1 -Version "1.0.0"
param(
  [string]$Version = "1.0.0",
  [string]$Tag = "test-standstill-v1.0.0"
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root\.. 

Write-Host "Starting standstill release for integration test: $Tag" -ForegroundColor Cyan

# Ensure dependencies
Write-Host "Installing Python deps..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install paho-mqtt prometheus_client websockets

# Start a Mosquitto container
$containerName = "nb-mosquitto-release"
$existing = (docker ps -a --filter "name=$containerName" --format "{{.Names}}") -split "\n" | Where-Object { $_ -ne "" }
if ($existing) {
    Write-Host "Removing existing container: $containerName" -ForegroundColor Yellow
    docker rm -f $containerName | Out-Null
}

Write-Host "Starting Mosquitto broker container..." -ForegroundColor Yellow
docker run -d --name $containerName -p 1883:1883 eclipse-mosquitto:2.0.15 | Out-Null

# Wait for port
for ($i=0; $i -lt 20; $i++) {
    try { 
        $s = Test-NetConnection -ComputerName 127.0.0.1 -Port 1883 -InformationLevel Quiet
        if ($s) { break }
    } catch { }
    Start-Sleep -Seconds 1
}

if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 1883 -InformationLevel Quiet)) {
    Write-Error "Broker did not start on port 1883"
    exit 1
}

Write-Host "Running integration test (CI-mode)..." -ForegroundColor Yellow
$rc = & python ci/integration_test.py --broker 127.0.0.1 --port 1883
if ($LASTEXITCODE -ne 0) {
    Write-Host "Integration test failed. Collecting logs and shutting down broker..." -ForegroundColor Red
    docker logs $containerName | Out-File -FilePath release-broker.log -Encoding utf8
    docker rm -f $containerName | Out-Null
    exit $LASTEXITCODE
}

# Package release artifacts
$releaseDir = Join-Path -Path (Get-Location) -ChildPath "releases\test-standstill-v$Version"
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
New-Item -ItemType Directory -Path $releaseDir | Out-Null

Write-Host "Copying artifacts to release folder..." -ForegroundColor Yellow
Copy-Item -Path ci\integration_test.py -Destination $releaseDir
Copy-Item -Path firmware\device_simulator.py -Destination $releaseDir
Copy-Item -Path firmware\README-SIMULATOR.md -Destination $releaseDir
Copy-Item -Path .github\workflows\integration.yml -Destination $releaseDir
Copy-Item -Path scripts\make_standstill_release.ps1 -Destination $releaseDir

# Create zip
$zipFile = "test-standstill-v$Version.zip"
if (Test-Path $zipFile) { Remove-Item $zipFile }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($releaseDir, $zipFile)

# Create tag
Write-Host "Creating git tag $Tag" -ForegroundColor Green
git add $releaseDir $zipFile
git commit -m "chore(release): standstill test release $Tag" --allow-empty
git tag -a $Tag -m "Standstill release of integration test $Version"

# Cleanup
Write-Host "Stopping and removing broker container..." -ForegroundColor Yellow
docker rm -f $containerName | Out-Null

Write-Host "Release package created: $zipFile" -ForegroundColor Green
Pop-Location

Write-Host "Done." -ForegroundColor Cyan
