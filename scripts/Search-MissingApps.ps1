# Origin: https://networkbuster.net/scripts/Search-MissingApps.ps1
# Search for missing app repositories and update configuration
Write-Host "Scanning system for missing app repositories..."

$SearchPaths = @("C:\", "D:\", "E:\", "K:\", "C:\Users\preci\.gemini\antigravity\scratch\networkbuster-optimizations\git")
$TargetDirs = @()
$Excludes = @("S:\")

foreach ($Path in $SearchPaths) {
    if ($Excludes -contains $Path) {
        Write-Host "Skipping excluded legacy path: $Path"
        continue
    }
    if (Test-Path $Path) {
        Write-Host "Searching $Path for repositories..."
        $Found = Get-ChildItem -Path $Path -Recurse -Filter "package.json" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty DirectoryName
        $TargetDirs += $Found
    }
}

Write-Host "Found $($TargetDirs.Count) potential app repositories."

# Update a configuration file (mocking the update)
$ConfigFile = Join-Path -Path $PSScriptRoot -ChildPath "..\config\app_repos.json"
if (-not (Test-Path (Split-Path $ConfigFile))) { New-Item -ItemType Directory -Path (Split-Path $ConfigFile) -Force }

$Config = @{
    last_search  = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    repositories = $TargetDirs
}

$Config | ConvertTo-Json | Set-Content -Path $ConfigFile
Write-Host "Updated configuration at $ConfigFile"
Write-Host "App repository search job finished."
