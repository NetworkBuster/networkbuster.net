param(
  [string]$Version = "1.0.0",
  [string]$Tag = "test-standstill-v1.0.0"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root\.. 

$releaseDir = Join-Path -Path (Get-Location) -ChildPath "releases\test-standstill-v$Version"
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
New-Item -ItemType Directory -Path $releaseDir | Out-Null
Copy-Item -Path ci\integration_test.py -Destination $releaseDir
Copy-Item -Path firmware\device_simulator.py -Destination $releaseDir
Copy-Item -Path firmware\README-SIMULATOR.md -Destination $releaseDir
Copy-Item -Path .github\workflows\integration.yml -Destination $releaseDir
Copy-Item -Path scripts\make_standstill_release.ps1 -Destination $releaseDir

$zipFile = "test-standstill-v$Version.zip"
if (Test-Path $zipFile) { Remove-Item $zipFile }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($releaseDir, $zipFile)

# Tag (if not exists)
$tagExists = git tag --list $Tag
if (-not $tagExists) {
    git add $releaseDir $zipFile
    git commit -m "chore(release): standstill test release $Tag" --allow-empty
    git tag -a $Tag -m "Standstill release of integration test $Version"
}

Pop-Location
Write-Host "Packaged $zipFile and tag $Tag (local)" -ForegroundColor Green
