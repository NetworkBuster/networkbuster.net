#!/usr/bin/env bash
set -euo pipefail

USAGE="Usage: $0 --id ID --model MODEL --technician NAME [--location LOC] [--notes TEXT] [--commit] [--dry-run]"

ID=''
MODEL=''
TECH=''
LOC=''
NOTES=''
COMMIT=0
DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) ID="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --technician) TECH="$2"; shift 2;;
    --location) LOC="$2"; shift 2;;
    --notes) NOTES="$2"; shift 2;;
    --commit) COMMIT=1; shift;;
    --dry-run) DRY=1; shift;;
    -h|--help) echo "$USAGE"; exit 0;;
    *) echo "Unknown: $1"; echo "$USAGE"; exit 1;;
  esac
done

if [[ -z "$ID" || -z "$MODEL" || -z "$TECH" ]]; then echo "$USAGE"; exit 1; fi

RECORDS_DIR="/mnt/s/NetworkBuster_Production/data/sterilization-records"
mkdir -p "$RECORDS_DIR"
TS=$(date -u +%Y-%m-%dT%H-%M-%SZ)
FILE="$RECORDS_DIR/sterilization_${TS}_${ID//[^a-zA-Z0-9_-]/_}.md"

cat > "$FILE" <<EOF
# Sterilization Record

date: $TS
technician: $TECH
instrument_id: $ID
instrument_model: $MODEL
location: $LOC
notes: "$NOTES"

checklist:
  pre_clean: false
  mechanical_clean: false
  disinfection: false
  uvc_used: false
  functional_check: false
EOF

if [[ "$DRY" -eq 1 ]]; then
  echo "DRYRUN: would write $FILE"
  exit 0
fi

echo "Wrote $FILE"
if [[ "$COMMIT" -eq 1 ]]; then
  git add "$FILE"
  git commit -m "chore: add sterilization record for $ID by $TECH" || true
  git push origin HEAD || echo "Push failed"
fi
