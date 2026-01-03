Antigravity Android module (placeholder)

- Kotlin app module under `app/`
- Add `google-services.json` to `app/` if integrating Firebase (do not commit it; see `.gitignore`)
- Build using Android Studio or Gradle CLI (this repo does not include Android SDK tooling)

To connect to Google Cloud services from this module, use a service account and the
`gcloud` or `firebase` CLIs; see `scripts/setup-gcloud-sdk.ps1` and `scripts/gcloud-auth.ps1`.