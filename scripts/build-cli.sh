#!/usr/bin/env bash
set -euo pipefail

# Usage:
# REGISTRY=networkbuster.org IMAGE_NAME=networkbuster-optimizations TAG=v7.5.0 ./scripts/build-cli.sh [--push]

REGISTRY="${REGISTRY:-networkbuster.org}"
IMAGE_NAME="${IMAGE_NAME:-networkbuster-optimizations}"
TAG="${TAG:-v7.5.0}"

PUSH=0
if [[ "${1:-}" == "--push" ]]; then
  PUSH=1
fi

FULL_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "Building ${FULL_NAME}..."
docker build -t "${FULL_NAME}" -f Dockerfile .

echo "Built ${FULL_NAME}"
if [[ "${PUSH}" == "1" ]]; then
  echo "Pushing ${FULL_NAME}..."
  docker push "${FULL_NAME}"
  echo "Pushed ${FULL_NAME}"
else
  echo "Skipping push. To push, run: REGISTRY=${REGISTRY} IMAGE_NAME=${IMAGE_NAME} TAG=${TAG} ./scripts/build-cli.sh --push"
fi
