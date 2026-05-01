#!/usr/bin/env bash
set -euo pipefail

KERNEL_VERSION="${1:-6.8.13}"
CACHE_DIR="$(pwd)/.cache/linux-${KERNEL_VERSION}"
mkdir -p "$CACHE_DIR"

# Build container
echo "==> Building lfs-build container"
docker build -t lfs-build -f os/lfs/Dockerfile .

# First run: build kernel and populate cache
echo "==> First run: building kernel and populating cache"
docker run --rm -e SKIP_KERNEL=false -e KERNEL_VERSION="$KERNEL_VERSION" -e KERNEL_CACHE_DIR=/workspace/kernel-cache -v "$CACHE_DIR:/workspace/kernel-cache" -v "$(pwd)/os/lfs/output:/workspace/output" lfs-build

if [ -f "$CACHE_DIR/vmlinuz-$KERNEL_VERSION" ]; then
  echo "vmlinuz-$KERNEL_VERSION is present in cache"
else
  echo "ERROR: vmlinuz-$KERNEL_VERSION not found in cache" >&2
  exit 1
fi

# Second run: should use cache
echo "==> Second run: expecting to use cached tarball or built kernel"
docker run --rm -e SKIP_KERNEL=false -e KERNEL_VERSION="$KERNEL_VERSION" -e KERNEL_CACHE_DIR=/workspace/kernel-cache -v "$CACHE_DIR:/workspace/kernel-cache" -v "$(pwd)/os/lfs/output:/workspace/output" lfs-build | tee /tmp/lfs-second-run.log

if grep -q "Using cached kernel tarball" /tmp/lfs-second-run.log || grep -q "Using cached built kernel" /tmp/lfs-second-run.log; then
  echo "Cache was used on second run"
else
  echo "Cache was NOT used on second run (check logs)" >&2
  exit 1
fi

echo "Cache verification complete: SUCCESS"
