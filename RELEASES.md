# Releases

## test-standstill-v1.0.0
- Date: 2026-01-08
- Contents: integration test, device simulator, CI workflow for local Mosquitto, release scripts
- How to use:
  - Run `scripts/make_standstill_release.ps1 -Version "1.0.0"` on Windows (requires Docker)
  - Or `scripts/make_standstill_release.sh 1.0.0` on Linux (requires Docker)
  - The script will run the integration test with a local Mosquitto broker and package `test-standstill-v1.0.0.zip` in repo root

Notes:
- The git tag `test-standstill-v1.0.0` will be created locally. Push tags to remote when ready: `git push origin test-standstill-v1.0.0`.
