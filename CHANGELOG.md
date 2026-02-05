# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- **NEW**: Mercedes-NVIDIA AI Drive Platform project added
  - Complete autonomous driving system documentation
  - Integration of NVIDIA Drive Thor/Orin platforms
  - Cloud infrastructure for fleet management
  - Comprehensive API documentation
  - Deployment guides and technical specifications
- Updated Android `antigravity` module to latest stable versions:
  - Android Gradle Plugin: 8.7.3 (from 8.1.0)
  - Kotlin: 2.0.21 (from 1.8.0)
  - Android SDK: 35 (from 34)
  - AndroidX Core KTX: 1.15.0 (from 1.9.0)
  - AppCompat: 1.7.0 (from 1.6.1)
  - Material Components: 1.12.0 (from 1.8.0)
  - Java compatibility: 17
  - Added namespace declaration in build.gradle
  - Added android:exported attribute to MainActivity
- Packaging scripts added: `scripts/make-release.js` and `scripts/create-shortcut.ps1`
- Added `start-desktop.bat` and `npm` scripts: `dist:zip`, `release:create-shortcut`, `start:desktop`

## [1.0.1] - YYYY-MM-DD
- Initial production release
