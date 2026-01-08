#!/usr/bin/env bash
# Make standstill release (Linux)
VERSION=${1:-1.0.0}
TAG=${2:-test-standstill-v${VERSION}}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

set -euo pipefail

echo "Installing python deps..."
python -m pip install --upgrade pip
pip install paho-mqtt prometheus_client websockets

CONTAINER_NAME="nb-mosquitto-release"
if docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  docker rm -f "$CONTAINER_NAME"
fi

echo "Starting Mosquitto..."
docker run -d --name "$CONTAINER_NAME" -p 1883:1883 eclipse-mosquitto:2.0.15

# wait for port
for i in {1..20}; do nc -z localhost 1883 && break || sleep 1; done
if ! nc -z localhost 1883; then
  echo "Broker did not start" >&2; docker rm -f "$CONTAINER_NAME"; exit 1
fi

echo "Running integration test"
python ci/integration_test.py --broker 127.0.0.1 --port 1883

# prepare release
RELEASE_DIR="releases/test-standstill-v${VERSION}"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"
cp ci/integration_test.py "$RELEASE_DIR/"
cp firmware/device_simulator.py "$RELEASE_DIR/"
cp firmware/README-SIMULATOR.md "$RELEASE_DIR/"
cp .github/workflows/integration.yml "$RELEASE_DIR/"
cp scripts/make_standstill_release.sh "$RELEASE_DIR/"

ZIP_FILE="test-standstill-v${VERSION}.zip"
rm -f "$ZIP_FILE"
zip -r "$ZIP_FILE" "$RELEASE_DIR"

echo "Tagging git repo $TAG"
git add "$RELEASE_DIR" "$ZIP_FILE" || true
git commit -m "chore(release): standstill test release $TAG" --allow-empty || true
git tag -a "$TAG" -m "Standstill release of integration test $VERSION"

echo "Stopping broker"
docker rm -f "$CONTAINER_NAME"

echo "Release created: $ZIP_FILE"