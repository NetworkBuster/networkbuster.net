#!/usr/bin/env bash
set -euo pipefail

OUTDIR="$(pwd)/output"
BUILD_DIR="$(pwd)/build"
BUSYBOX_VERSION="1_36_1"
BUSYBOX_URL="https://busybox.net/downloads/busybox-${BUSYBOX_VERSION}.tar.bz2"

mkdir -p "$OUTDIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "==> Build workspace: $BUILD_DIR"
cd "$BUILD_DIR"

# Download and extract BusyBox
if [ ! -f "busybox-${BUSYBOX_VERSION}.tar.bz2" ]; then
  wget -q "$BUSYBOX_URL" -O "busybox-${BUSYBOX_VERSION}.tar.bz2"
fi
rm -rf busybox-${BUSYBOX_VERSION}
tar xjf busybox-${BUSYBOX_VERSION}.tar.bz2
cd busybox-${BUSYBOX_VERSION}

# Configure BusyBox for a static build and minimal busybox install
make defconfig >/dev/null
# Enable static build
scripts/config --enable STATIC
make -j"$(nproc)" >/dev/null
make CONFIG_PREFIX="$BUILD_DIR/rootfs" install >/dev/null

# Create minimal filesystem structure
ROOTFS="$BUILD_DIR/rootfs"
mkdir -p "$ROOTFS"/{proc,sys,dev,run,etc,mnt,tmp}
chmod 1777 "$ROOTFS/tmp"

# Create a simple init
cat > "$ROOTFS/init" <<'EOF'
#!/bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
echo "Booted minimal rootfs"
exec /bin/sh
EOF
chmod +x "$ROOTFS/init"

# Fix necessary symlinks
ln -sf /bin/busybox "$ROOTFS/bin/sh"

# Create device nodes
sudo rm -f "$ROOTFS/dev/console"
sudo mknod -m 622 "$ROOTFS/dev/console" c 5 1 || true
sudo mknod -m 666 "$ROOTFS/dev/null" c 1 3 || true

# Create /etc/passwd and /etc/group
cat > "$ROOTFS/etc/passwd" <<EOF
root:x:0:0:root:/root:/bin/sh
EOF
cat > "$ROOTFS/etc/group" <<EOF
root:x:0:
EOF

# Create compressed cpio initramfs
pushd "$ROOTFS" >/dev/null
find . | cpio -H newc -o | gzip -9 > "$OUTDIR/rootfs.cpio.gz"
popd >/dev/null

# Create tarball of rootfs
tar -C "$ROOTFS" -czf "$OUTDIR/rootfs.tar.gz" .

# List artifacts
ls -lh "$OUTDIR"

echo "==> Build complete: artifacts in $OUTDIR"

# Basic smoke check: ensure /bin/sh exists in tarball
if tar tzf "$OUTDIR/rootfs.tar.gz" | grep -q "bin/sh"; then
  echo "rootfs tar contains /bin/sh"
else
  echo "Warning: /bin/sh not found in rootfs tar" >&2
  exit 1
fi

# Build Linux kernel (optional)
KERNEL_VERSION="${KERNEL_VERSION:-6.8.13}"
SKIP_KERNEL="${SKIP_KERNEL:-false}"
if [ "$SKIP_KERNEL" != "true" ]; then
  echo "==> Building Linux kernel $KERNEL_VERSION (this may take a while)"
  cd "$BUILD_DIR"
  if [ ! -f "linux-$KERNEL_VERSION.tar.xz" ]; then
    wget -q "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$KERNEL_VERSION.tar.xz"
  fi
  rm -rf linux-$KERNEL_VERSION
  tar xf linux-$KERNEL_VERSION.tar.xz
  cd linux-$KERNEL_VERSION

  # Use a default x86_64 defconfig and build
  make defconfig

  # Prefer enabling initrd support and common virtualization drivers
  # (scripts/config may or may not be available depending on kernel version)
  if [ -f scripts/config ]; then
    scripts/config --enable CONFIG_BLK_DEV_INITRD || true
    scripts/config --module CONFIG_VIRTIO_NET || true
    scripts/config --module CONFIG_VIRTIO_PCI || true
    scripts/config --module CONFIG_VIRTIO_BALLOON || true
  fi

  make -j"$(nproc)"

  if [ -f "arch/x86/boot/bzImage" ]; then
    cp "arch/x86/boot/bzImage" "$OUTDIR/vmlinuz-$KERNEL_VERSION"
    echo "Kernel built: $OUTDIR/vmlinuz-$KERNEL_VERSION"
  else
    echo "Kernel build failed: no bzImage found" >&2
  fi
else
  echo "SKIP_KERNEL=true — skipping kernel build"
fi

# Run a best-effort QEMU boot test using the built kernel if available, else a host kernel
if command -v qemu-system-x86_64 >/dev/null 2>&1; then
  if [ -f "$OUTDIR/vmlinuz-$KERNEL_VERSION" ]; then
    KERNEL="$OUTDIR/vmlinuz-$KERNEL_VERSION"
  elif ls /boot/vmlinuz-* 2>/dev/null | head -n1 >/dev/null 2>&1; then
    KERNEL="$(ls -1 /boot/vmlinuz-* | tail -n1)"
  else
    KERNEL=""
  fi

  if [ -n "$KERNEL" ]; then
    echo "Attempting QEMU boot test with kernel: $KERNEL (20s)"
    qemu-system-x86_64 -kernel "$KERNEL" -initrd "$OUTDIR/rootfs.cpio.gz" -nographic -append "console=ttyS0 root=/dev/ram0 rw init=/init" -m 512 -no-reboot -display none &
    QEMU_PID=$!
    sleep 20
    if ps -p $QEMU_PID >/dev/null 2>&1; then
      echo "QEMU running — killing after smoke test"
      kill $QEMU_PID || true
    fi
  else
    echo "No kernel available for QEMU boot test; skipping"
  fi
else
  echo "QEMU is not installed — skipping boot test"
fi
