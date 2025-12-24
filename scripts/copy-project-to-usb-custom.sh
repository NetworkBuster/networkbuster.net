#!/usr/bin/env bash
# copy-project-to-usb-custom.sh - Wrapper that defaults to the repo root as SOURCE
# Usage: copy-project-to-usb-custom.sh [DEST]
# Default DEST: /Volumes/FLASHDRIVE/NetworkBuster

set -euo pipefail
IFS=$'\n\t'

# Determine repo root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DEST="${1:-/Volumes/FLASHDRIVE/NetworkBuster}"

# If destination does not exist, attempt auto-detect using the generic script
if [ ! -d "$DEST" ]; then
  echo "Destination '$DEST' does not exist. Attempting to auto-detect removable mount points..."
  # forward to generic script which supports -a (prompt) and -A (auto-accept)
  "$GENERIC" "$REPO_ROOT" "$DEST" -a "$@"
  exit $?
fi

echo "Repo root detected: $REPO_ROOT"
echo "Destination: $DEST"

# Call the generic script in the same directory
SCRIPTDIR="$SCRIPT_DIR"
GENERIC="$SCRIPTDIR/copy-project-to-usb.sh"

if [ ! -f "$GENERIC" ]; then
  echo "Error: generic script not found at $GENERIC" >&2
  exit 2
fi

# Forward all remaining args to generic script
"$GENERIC" "$REPO_ROOT" "$DEST" "$@"
