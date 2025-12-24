# Secure / local files not tracked

The following files contain sensitive or local configuration and are explicitly ignored in `.gitignore`:

- `scripts/dummy-sa.json` (service account / credentials placeholder)
- `scripts/gcloud-startup.ps1` (local startup script)

If you need to keep a local copy, store it outside the repository or in a secure vault.
