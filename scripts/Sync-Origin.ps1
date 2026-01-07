# Sync Origin Script
# Origin: https://networkbuster.net/scripts/Sync-Origin.ps1
Write-Host "Initializing GitHub synchronization..."

$ProjectRoot = "C:\Users\preci\.gemini\antigravity\scratch\networkbuster-optimizations"
$RemoteUrl = "https://github.com/networkbuster.net/networkbuster.net.git"

if (-not (Test-Path (Join-Path $ProjectRoot ".git"))) {
    Write-Host "Initializing git repository..."
    git init $ProjectRoot
}

Set-Location $ProjectRoot

# Add remote if not exists
$Remotes = git remote
if ($Remotes -notcontains "origin") {
    Write-Host "Adding remote origin: $RemoteUrl"
    git remote add origin $RemoteUrl
}
else {
    Write-Host "Remote origin already exists. Updating URL..."
    git remote set-url origin $RemoteUrl
}

# Pull from main
Write-Host "Pulling from main..."
git pull origin main --allow-unrelated-histories

# Commit local changes
Write-Host "Committing local changes..."
git add .
git commit -m "Auto-sync from NetworkBuster AI pipeline"

# Push to new origin
Write-Host "Pushing to new origin..."
git push origin main

Write-Host "Synchronization complete."
