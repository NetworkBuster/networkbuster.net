<#
PowerShell helper: build-and-install.ps1
- Run as Administrator
- What it does (interactive):
  1. Optionally installs Chocolatey (if missing)
  2. Optionally installs Azul Zulu (Zulu17), Gradle and Platform-Tools via Chocolatey
  3. Generates a Gradle wrapper (if missing and gradle is available)
  4. Runs the wrapper to build a Debug APK
  5. Installs the APK on a connected device via adb (if present)

Usage:
  Open PowerShell as Administrator and run:
    cd C:\path\to\antigravity
    .\scripts\build-and-install.ps1
#>

function Assert-Admin {
    $isAdmin = ([Security.Principal.WindowsIdentity]::GetCurrent()).Groups -match "S-1-5-32-544"
    if (-not $isAdmin) {
        Write-Host "ERROR: This script must be run as Administrator.`nRight-click PowerShell and 'Run as Administrator'." -ForegroundColor Red
        exit 1
    }
}

function Confirm-Or-Exit($message) {
    $r = Read-Host "$message (Y/n)"
    if ($r -and ($r -notmatch '^[Yy]')) { Write-Host "Aborted."; exit 0 }
}

Assert-Admin

$projectRoot = Resolve-Path ".." -Relative | Split-Path -Parent  # assume script runs from scripts\
$projectRoot = (Get-Location).Path
Write-Host "Project root: $projectRoot"

# Confirm user wants to proceed
Confirm-Or-Exit "Proceed with installing prerequisites and building the debug APK?"

# Install Chocolatey if missing
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Confirm-Or-Exit "Chocolatey not found. Install Chocolatey now?"
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    iex ((New-Object Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
}

# Ask which packages to install
$installZulu = Read-Host "Install Azul Zulu 17 JDK via Chocolatey? (Y/n)"; if ($installZulu -and $installZulu -notmatch '^[Yy]') { $installZulu = $false } else { $installZulu = $true }
$installGradle = Read-Host "Install Gradle via Chocolatey? (Y/n)"; if ($installGradle -and $installGradle -notmatch '^[Yy]') { $installGradle = $false } else { $installGradle = $true }
$installPlatformTools = Read-Host "Install Android platform-tools (adb) via Chocolatey? (Y/n)"; if ($installPlatformTools -and $installPlatformTools -notmatch '^[Yy]') { $installPlatformTools = $false } else { $installPlatformTools = $true }

if ($installZulu) { choco install zulu17 -y }
if ($installGradle) { choco install gradle -y }
if ($installPlatformTools) { choco install platform-tools -y }

# Refresh environment and verify
refreshenv
Write-Host "Verifying installations..."
java -version 2>$null; if ($LASTEXITCODE -ne 0) { Write-Warning "java not found or not configured." } else { java -version }
if ($installGradle) { gradle --version 2>$null; if ($LASTEXITCODE -ne 0) { Write-Warning "gradle not found." } }
adb version 2>$null; if ($LASTEXITCODE -ne 0) { Write-Warning "adb not found." } else { adb version }

# Move to project root
Set-Location $projectRoot

# Generate Gradle wrapper if missing
if (-not (Test-Path .\gradlew) -and (Get-Command gradle -ErrorAction SilentlyContinue)) {
    Write-Host "Generating Gradle wrapper..."
    gradle wrapper
}
elseif (-not (Test-Path .\gradlew)) {
    Write-Warning "gradlew not found and gradle not installed. You can generate the wrapper by installing Gradle or by opening the project in Android Studio."
    $continue = Read-Host "Continue and attempt to build with 'gradle' if present? (Y/n)"; if ($continue -and $continue -notmatch '^[Yy]') { Write-Host "Aborted."; exit 0 }
}

# Build debug APK
if (Test-Path .\gradlew) {
    Write-Host "Building Debug APK with wrapper (this can take a few minutes)..."
    & .\gradlew assembleDebug --console=plain
    $buildExit = $LASTEXITCODE
} else {
    Write-Host "No wrapper found. Attempting 'gradle assembleDebug'..."
    & gradle assembleDebug --console=plain
    $buildExit = $LASTEXITCODE
}

if ($buildExit -ne 0) {
    Write-Error "Build failed (exit code $buildExit). Re-run with --stacktrace for details or open the project in Android Studio."; exit $buildExit
}

# Find APK
$apkPath = Join-Path -Path $projectRoot -ChildPath "app\build\outputs\apk\debug\app-debug.apk"
if (-not (Test-Path $apkPath)) {
    Write-Error "APK not found at expected location: $apkPath"; exit 1
}
Write-Host "APK built: $apkPath"

# Install to device
$devices = & adb devices | Select-Object -Skip 1 | Where-Object { $_ -match '\w' }
if (-not $devices) {
    Write-Warning "No connected devices found via adb. Connect a device and authorize USB debugging, then run:\nadb install -r `"$apkPath`""
    exit 0
}
Write-Host "Device(s) detected. Installing APK..."
& adb install -r $apkPath
if ($LASTEXITCODE -eq 0) { Write-Host "APK installed successfully." } else { Write-Error "adb install failed (code $LASTEXITCODE)" }

Write-Host "Done." -ForegroundColor Green
