param(
  [string]$KernelVersion = '6.8.13'
)

$cacheDir = Join-Path -Path (Get-Location) -ChildPath ".cache/linux-$KernelVersion"
if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir | Out-Null }

Write-Host "Building lfs-build container..."
docker build -t lfs-build -f os/lfs/Dockerfile .

Write-Host "First run: building kernel and populating cache"
docker run --rm -e SKIP_KERNEL=false -e KERNEL_VERSION=$KernelVersion -e KERNEL_CACHE_DIR=/workspace/kernel-cache -v "${cacheDir}:/workspace/kernel-cache" -v "${PWD}/os/lfs/output:/workspace/output" lfs-build

if (Test-Path (Join-Path $cacheDir "vmlinuz-$KernelVersion")) {
  Write-Host "vmlinuz-$KernelVersion found in cache"
} else {
  Write-Error "vmlinuz-$KernelVersion not found in cache"
  exit 1
}

Write-Host "Second run: expecting to use cached tarball or built kernel"
docker run --rm -e SKIP_KERNEL=false -e KERNEL_VERSION=$KernelVersion -e KERNEL_CACHE_DIR=/workspace/kernel-cache -v "${cacheDir}:/workspace/kernel-cache" -v "${PWD}/os/lfs/output:/workspace/output" lfs-build | Tee-Object -FilePath "$env:TEMP\lfs-second-run.log"

$log = Get-Content "$env:TEMP\lfs-second-run.log"
if ($log -match 'Using cached kernel tarball' -or $log -match 'Using cached built kernel') {
  Write-Host "Cache was used on second run"
} else {
  Write-Error "Cache was NOT used on second run (check logs)"
  exit 1
}

Write-Host "Cache verification complete: SUCCESS"