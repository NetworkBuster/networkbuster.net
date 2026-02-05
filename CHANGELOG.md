# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2.0.0] - 2026-02-05
- **MAJOR RELEASE**: Complete data package with all projects and documentation
- **NEW**: Mercedes-NVIDIA AI Drive Platform project added
  - Complete autonomous driving system documentation
  - Integration of NVIDIA Drive Thor/Orin platforms (2000 TOPS)
  - Cloud infrastructure for fleet management
  - Comprehensive API documentation
  - Deployment guides and technical specifications
- **UPDATED**: Android `antigravity` module to latest stable versions:
  - Android Gradle Plugin: 8.7.3 (from 8.1.0)
  - Kotlin: 2.0.21 (from 1.8.0)
  - Android SDK: 35 (from 34)
  - AndroidX Core KTX: 1.15.0 (from 1.9.0)
  - AppCompat: 1.7.0 (from 1.6.1)
  - Material Components: 1.12.0 (from 1.8.0)
  - Java compatibility: 17
  - Added namespace declaration in build.gradle
  - Added android:exported attribute to MainActivity
- **NEW**: Comprehensive release system with full data packaging
  - Created `scripts/create-full-release.js` for complete releases
  - Includes all source code, documentation, and data files
  - Release manifest and installation guides
  - All major projects bundled (Space Infrastructure, Mercedes-NVIDIA, Android)
- Packaging scripts added: `scripts/make-release.js` and `scripts/create-shortcut.ps1`
- Added `start-desktop.bat` and `npm` scripts: `dist:zip`, `release:create-shortcut`, `start:desktop`

## [1.0.1] - YYYY-MM-DD
- Initial production release
