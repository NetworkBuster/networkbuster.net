#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 [--url URL] [--mock] [--prompt "text"]

Options:
  --url URL        Base API URL (default: http://localhost:3001/api/robot)
  --mock           Run in mock mode (simulate responses locally)
  --prompt TEXT    Single prompt to test (can be quoted). Can be supplied multiple times.
  --concurrency N  Run N requests concurrently for a basic load check (default: 1)
EOF
}

URL="http://localhost:3001/api/robot"
MOCK=0
CONCURRENCY=1
PROMPTS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) URL="$2"; shift 2 ;;
    --mock) MOCK=1; shift ;;
    --prompt) PROMPTS+=("$2"); shift 2 ;;
    --concurrency) CONCURRENCY="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

# Default prompts if none provided
if [ ${#PROMPTS[@]} -eq 0 ]; then
  PROMPTS=(
    "Summarize lunar recycling best practices in one paragraph."
    "List three risks of regolith processing on the Moon and one mitigation for each."
    "Generate an example test query for the NetworkBuster AI robot that checks audio synthesis." 
  )
fi

echo "AI Robot Test — URL: $URL  mock=$MOCK  concurrency=$CONCURRENCY"

run_one(){
  local prompt="$1"
  if [ "$MOCK" -eq 1 ]; then
    # Simulated response
    echo "{\"message\": \"MOCK RESPONSE for prompt: $(echo "$prompt" | sed 's/"/\\\"/g')\" }"
    return 0
  fi

  # Send request
  local tmp=$(mktemp)
  local status
  status=$(curl -sS -X POST -H "Content-Type: application/json" -d "{\"prompt\": \"${prompt//"/\"}\"}" "$URL" -o "$tmp" -w "%{http_code}") || return 1
  local body
  body=$(cat "$tmp")
  rm -f "$tmp"

  # Validate response
  if [ "$status" != "200" ]; then
    echo "FAIL: HTTP $status for prompt: $prompt"
    echo "Body: $body"
    return 2
  fi
  if echo "$body" | grep -q '"message"'; then
    echo "OK: $(echo "$prompt" | cut -c-80) -> message present"
    return 0
  else
    echo "FAIL: no 'message' field in response for prompt: $prompt"
    echo "Body: $body"
    return 3
  fi
}

# Run tests
failures=0
for p in "${PROMPTS[@]}"; do
  echo "\n== Prompt: ${p} =="

  # concurrency support
  if [ "$CONCURRENCY" -gt 1 ]; then
    for i in $(seq 1 $CONCURRENCY); do
      run_one "$p" &
    done
    wait
    rc=$?
    if [ $rc -ne 0 ]; then failures=$((failures+1)); fi
  else
    run_one "$p" || failures=$((failures+1))
  fi

done

if [ "$failures" -eq 0 ]; then
  echo "\nAll tests passed!"
  exit 0
else
  echo "\nSome tests failed: $failures" >&2
  exit 1
fi
