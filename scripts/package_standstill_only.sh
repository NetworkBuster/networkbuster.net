#!/usr/bin/env bash
VERSION=${1:-1.0.0}
TAG=${2:-test-standstill-v${VERSION}}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

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

# Tag if not exists
if ! git tag --list | grep -q "$TAG"; then
  git add "$RELEASE_DIR" "$ZIP_FILE" || true
  git commit -m "chore(release): standstill test release $TAG" --allow-empty || true
  git tag -a "$TAG" -m "Standstill release of integration test $VERSION"
fi

echo "Packaged $ZIP_FILE and tag $TAG (local)"