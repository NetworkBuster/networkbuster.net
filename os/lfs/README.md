# LFS Scaffold - x86_64 rootfs (PoC)

This folder contains a minimal, reproducible scaffold to build a tiny "LFS-like" root filesystem (rootfs) for x86_64 and produce a tarball artifact. This is a practical starting point for a full Linux From Scratch (LFS) workflow.

Overview
- The build produces a BusyBox-based rootfs and a compressed cpio initramfs, and optionally compiles an x86_64 Linux kernel (controlled by the `KERNEL_VERSION` and `SKIP_KERNEL` environment variables).
- A basic GitHub Actions workflow (`.github/workflows/lfs-build.yml`) will run the build inside a Docker container, upload the `rootfs.tar.gz` artifact and attempt a quick QEMU smoke test (if a kernel is available on the runner or the pipeline is configured to build the kernel).

Notes & caveats
- A full LFS build (toolchain + all packages + kernel) is large and may take many hours. This scaffold produces a working minimal rootfs suitable for booting with an initramfs and a kernel.
- CI runners have limits (time, CPU). The CI is configured for a quick smoke test; expand it locally for full LFS.
- The scripts are opinionated and intended to be extended. Use them as a reproducible starting point.

Quick local usage
1. Build with Docker (recommended):
   docker build -t lfs-build -f os/lfs/Dockerfile .
   docker run --rm -v "$PWD/os/lfs/output:/output" lfs-build

2. On success artifacts are placed in `os/lfs/output/`:
   - `rootfs.tar.gz` (tarball of the root filesystem)
   - `rootfs.cpio.gz` (compressed initramfs for quick QEMU boot)

CI
- The workflow supports manual dispatch with kernel build enabled. To trigger a kernel build from the GitHub UI go to **Actions → Build LFS rootfs (PoC)** → **Run workflow**, then set `build_kernel=true` and optionally specify `kernel_version` (default: `6.8.13`).
- For ordinary pushes the CI will skip kernel building to avoid long jobs; artifacts are still produced and uploaded.

Contributing
- To extend toward a full LFS build: add package recipes, a toolchain phase, and a kernel build step.
- File issues or PRs to discuss further changes.
