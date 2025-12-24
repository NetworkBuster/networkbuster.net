#!/usr/bin/env bash
# copy-project-to-usb.sh - Generic macOS / Linux helper to copy a project to a USB drive
# Usage: copy-project-to-usb.sh [SOURCE] [DEST] [options]
# Defaults: SOURCE='.' (current directory) DEST='/Volumes/FLASHDRIVE/project'
# Options:
#   -z           : create a zip archive on the destination instead of rsync
#   -e PATTERN   : add an exclude pattern (can be used multiple times)
#   -n           : dry-run (rsync --dry-run)
#   -c           : checksum verification for a created archive
#   -h           : show help

set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<EOF
Usage: $0 [SOURCE] [DEST] [options]
Defaults: SOURCE='.' DEST='/Volumes/FLASHDRIVE/project'
Options:
  -z           Create zip archive at DEST (DEST should be a directory)
  -e PATTERN   Add exclude pattern (multiple allowed)
  -n           Dry run (rsync)
  -c           Verify checksum (sha256) for created archive
  -h           Show this help
EOF
}

SOURCE="${1:-.}"
DEST="${2:-/Volumes/FLASHDRIVE/project}"
shift 2 || true

ZIP=false
DRY_RUN=false
VERIFY=false
EXCLUDES=(--exclude 'node_modules' --exclude '.git' --exclude 'dist')

while getopts ":ze:ncahA" opt; do
  case ${opt} in
    z ) ZIP=true ;;
    e ) EXCLUDES+=(--exclude "${OPTARG}") ;;
    n ) DRY_RUN=true ;;
    c ) VERIFY=true ;;
    a ) AUTO=true ;;            # auto-detect mounts and prompt
    A ) AUTO_ACCEPT=true ;;     # auto-accept first detected mount
    h ) usage; exit 0 ;;
    \? ) echo "Invalid option: -${OPTARG}" >&2 ; usage; exit 2 ;;
  esac
done

# Mount detection helpers
AUTO=${AUTO:-false}
AUTO_ACCEPT=${AUTO_ACCEPT:-false}

detect_mounts() {
  CANDIDATES=()
  # macOS
  if [ -d /Volumes ]; then
    for d in /Volumes/*; do
      [ -d "$d" ] || continue
      # Skip system/hidden mounts
      base="$(basename "$d")"
      if [ "$base" = "Macintosh HD" ] || [ "$base" = "VMware Shared Folders" ]; then
        continue
      fi
      CANDIDATES+=("$d")
    done
  fi

  # Common Linux mount points
  if [ -n "${USER:-}" ]; then
    if [ -d "/media/$USER" ]; then
      for d in /media/$USER/*; do [ -d "$d" ] && CANDIDATES+=("$d"); done
    fi
    if [ -d "/run/media/$USER" ]; then
      for d in /run/media/$USER/*; do [ -d "$d" ] && CANDIDATES+=("$d"); done
    fi
  fi
  if [ -d /media ]; then
    for d in /media/*; do [ -d "$d" ] && CANDIDATES+=("$d"); done
  fi
  if [ -d /mnt ]; then
    for d in /mnt/*; do [ -d "$d" ] && CANDIDATES+=("$d"); done
  fi

  # Remove duplicates
  uniq_candidates=()
  for x in "${CANDIDATES[@]}"; do
    skip=false
    for y in "${uniq_candidates[@]}"; do [ "$x" = "$y" ] && skip=true; done
    $skip || uniq_candidates+=("$x")
  done
  CANDIDATES=("${uniq_candidates[@]}")
}

choose_mount() {
  detect_mounts
  if [ ${#CANDIDATES[@]} -eq 0 ]; then
    echo "No removable or external mount points were detected."
    return 1
  fi

  if [ "$AUTO_ACCEPT" = true ]; then
    CHOICE="${CANDIDATES[0]}"
    echo "Auto-selected: $CHOICE"
    echo "$CHOICE"
    return 0
  fi

  echo "Detected candidate mounts:"
  i=0
  for m in "${CANDIDATES[@]}"; do
    i=$((i+1))
    echo "[$i] $m"
  done
  read -p "Choose a mount by number (or press Enter to cancel): " sel
  if [ -z "$sel" ]; then
    return 1
  fi
  if ! [[ "$sel" =~ ^[0-9]+$ ]] || [ "$sel" -lt 1 ] || [ "$sel" -gt ${#CANDIDATES[@]} ]; then
    echo "Invalid selection"
    return 1
  fi
  CHOICE="${CANDIDATES[$((sel-1))]}"
  echo "$CHOICE"
  return 0
}

# Resolve SOURCE and DEST
SOURCE_ABS="$(cd "$SOURCE" && pwd)"
DEST_DIR="${DEST%/}"

echo "Source: $SOURCE_ABS"
echo "Destination: $DEST_DIR"

if [ "$ZIP" = true ]; then
  # Make sure destination exists
  mkdir -p "$DEST_DIR"
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  ARCHIVE_NAME="project-$TIMESTAMP.zip"
  ARCHIVE_PATH="$DEST_DIR/$ARCHIVE_NAME"

  echo "Creating zip archive: $ARCHIVE_PATH"
  # Build the exclude args for zip: zip does not support array excludes easily, so use -x patterns
  CD_DIR="$(dirname "$SOURCE_ABS")"
  BASE_NAME="$(basename "$SOURCE_ABS")"
  pushd "$CD_DIR" >/dev/null

  ZIP_EXCLUDES=()
  for ex in "${EXCLUDES[@]}"; do
    # convert --exclude pattern to zip -x pattern (relative to base)
    pat="${ex#--exclude }"
    ZIP_EXCLUDES+=("$BASE_NAME/$pat")
  done

  # Use zip -r with excludes
  if [ ${#ZIP_EXCLUDES[@]} -gt 0 ]; then
    zip -r -q "$ARCHIVE_PATH" "$BASE_NAME" "${ZIP_EXCLUDES[@]}"
  else
    zip -r -q "$ARCHIVE_PATH" "$BASE_NAME"
  fi

  popd >/dev/null
  echo "Archive created: $ARCHIVE_PATH"

  if [ "$VERIFY" = true ]; then
    echo "Verifying archive checksum (sha256)"
    sha256sum "$ARCHIVE_PATH"
  fi
else
  # Use rsync to copy contents
  echo "Using rsync to copy files (excludes: ${EXCLUDES[*]})"
  mkdir -p "$DEST_DIR"
  RSYNC_CMD=(rsync -av --progress)

  if [ "$DRY_RUN" = true ]; then
    RSYNC_CMD+=(--dry-run)
  fi

  RSYNC_CMD+=("${EXCLUDES[@]}" "$SOURCE_ABS/" "$DEST_DIR/")

  echo "+ ${RSYNC_CMD[*]}"
  "${RSYNC_CMD[@]}"

  echo "Sync complete."
fi

# Final summary
echo "Done. Verify with: du -sh \"$SOURCE_ABS\" \"$DEST_DIR\""
if [ "$ZIP" = false ]; then
  echo "Eject the drive when ready (macOS: diskutil eject /Volumes/FLASHDRIVE; Linux: umount /media/<you>/FLASHDRIVE)"
fi

echo "Finished."
