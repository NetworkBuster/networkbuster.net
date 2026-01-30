@echo off
REM NetworkBuster Google Cloud Deployment (Windows)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   NetworkBuster - Google Cloud Deployment
echo ═══════════════════════════════════════════════════════════════
echo.

REM Check gcloud installation
where gcloud >nul 2>nul
if errorlevel 1 (
    echo ❌ Google Cloud SDK not found!
    echo.
    echo Download from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo ✅ Google Cloud SDK found
echo.

REM Set project
echo 📋 Setting Google Cloud project...
set PROJECT_ID=networkbuster-6152
gcloud config set project %PROJECT_ID%

echo.
echo 🚀 Choose deployment method:
echo   1. App Engine (Managed, Auto-scaling)
echo   2. Cloud Run (Containerized, Serverless)
echo   3. Compute Engine (VM Instance)
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto appengine
if "%choice%"=="2" goto cloudrun
if "%choice%"=="3" goto compute
goto invalid

:appengine
echo.
echo 🌐 Deploying to App Engine...
echo ────────────────────────────────────────

REM Create app if not exists
gcloud app describe >nul 2>&1 || gcloud app create --region=us-central

REM Deploy
gcloud app deploy app.yaml --quiet

echo.
echo ✅ Deployment Complete!
echo.
echo 🌍 Your app is live at:
gcloud app browse --no-launch-browser
goto end

:cloudrun
echo.
echo 🐳 Deploying to Cloud Run...
echo ────────────────────────────────────────

REM Enable required APIs
echo Enabling Cloud Run API...
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

REM Build and deploy
echo.
echo Building container...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/networkbuster

echo.
echo Deploying to Cloud Run...
gcloud run deploy networkbuster ^
  --image gcr.io/%PROJECT_ID%/networkbuster ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --port 8080

echo.
echo ✅ Deployment Complete!
echo.
echo 🌍 Your app URL:
gcloud run services describe networkbuster --region us-central1 --format="value(status.url)"
goto end

:compute
echo.
echo 💻 Compute Engine Deployment
echo ────────────────────────────────────────
echo.
echo Creating VM instance...

gcloud compute instances create networkbuster-vm ^
  --zone=us-central1-a ^
  --machine-type=e2-medium ^
  --image-family=ubuntu-2004-lts ^
  --image-project=ubuntu-os-cloud ^
  --boot-disk-size=20GB ^
  --tags=http-server,https-server

echo.
echo ✅ VM Created!
echo.
echo 📋 Next steps:
echo   1. SSH: gcloud compute ssh networkbuster-vm --zone=us-central1-a
echo   2. Clone: git clone https://github.com/NetworkBuster/networkbuster.net.git
echo   3. Install Python: sudo apt install python3-pip python3-venv
echo   4. Setup: cd networkbuster.net ^&^& python3 -m venv .venv
echo   5. Activate: source .venv/bin/activate
echo   6. Install: pip install -r requirements.txt
echo   7. Run: python network_map_viewer.py
goto end

:invalid
echo ❌ Invalid choice
pause
exit /b 1

:end
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🎉 Deployment Complete!
echo ═══════════════════════════════════════════════════════════════
pause
