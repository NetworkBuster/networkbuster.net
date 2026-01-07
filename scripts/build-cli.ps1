param(
  [string]$Registry = "networkbuster.org",
  [string]$Image = "networkbuster-optimizations",
  [string]$Tag = "v7.5.0",
  [switch]$Push
)

$FullName = "$Registry/$Image:$Tag"
Write-Host "Building $FullName..."
docker build -t $FullName -f Dockerfile .
Write-Host "Built $FullName"
if ($Push) {
  Write-Host "Pushing $FullName..."
  docker push $FullName
  Write-Host "Pushed $FullName"
} else {
  Write-Host "Skipping push. To push, rerun with -Push"
}
