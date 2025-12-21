FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV KERNEL_VERSION=6.8.13
ENV SKIP_KERNEL=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    make \
    bc \
    bison \
    flex \
    libelf-dev \
    libncurses-dev \
    wget \
    ca-certificates \
    git \
    bzip2 \
    gzip \
    cpio \
    sudo \
    qemu-system-x86 \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY build-lfs.sh /workspace/build-lfs.sh
RUN chmod +x /workspace/build-lfs.sh

# Default entrypoint runs the build and places artifacts under /workspace/output
ENTRYPOINT ["/workspace/build-lfs.sh"]
