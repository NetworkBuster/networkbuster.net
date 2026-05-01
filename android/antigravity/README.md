Antigravity Android module

- Kotlin app module under `app/`
- Updated to latest stable versions (Kotlin 2.0.21, AGP 8.7.3, Android SDK 35)
- Add `google-services.json` to `app/` if integrating Firebase (do not commit it; see `.gitignore`)
- Build using Android Studio or Gradle CLI (this repo does not include Android SDK tooling)

## Version Information
- Android Gradle Plugin: 8.7.3
- Kotlin: 2.0.21
- Compile SDK: 35
- Target SDK: 35
- Min SDK: 21
- Java Version: 17

To connect to Google Cloud services from this module, use a service account and the
`gcloud` or `firebase` CLIs; see `scripts/setup-gcloud-sdk.ps1` and `scripts/gcloud-auth.ps1`.