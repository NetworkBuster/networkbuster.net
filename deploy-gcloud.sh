#!/bin/bash
# NetworkBuster Google Cloud Deployment Script

echo "════════════════════════════════════════════════════════════"
echo "  NetworkBuster - Google Cloud Deployment"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found!"
    echo ""
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ Google Cloud SDK found"
echo ""

# Set project
echo "📋 Setting Google Cloud project..."
PROJECT_ID="cosmic-howl-47d8f"
gcloud config set project $PROJECT_ID

echo ""
echo "🚀 Choose deployment method:"
echo "  1. App Engine (Managed, Auto-scaling)"
echo "  2. Cloud Run (Containerized, Serverless)"
echo "  3. Compute Engine (VM Instance)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
  1)
    echo ""
    echo "🌐 Deploying to App Engine..."
    echo "────────────────────────────────────────"
    
    # Create app if not exists
    gcloud app describe 2>/dev/null || gcloud app create --region=us-central
    
    # Deploy
    gcloud app deploy app.yaml --quiet
    
    echo ""
    echo "✅ Deployment Complete!"
    echo ""
    echo "🌍 Your app is live at:"
    gcloud app browse --no-launch-browser
    ;;
    
  2)
    echo ""
    echo "🐳 Deploying to Cloud Run..."
    echo "────────────────────────────────────────"
    
    # Enable required APIs
    echo "Enabling Cloud Run API..."
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    
    # Build and deploy
    echo ""
    echo "Building container..."
    gcloud builds submit --tag gcr.io/$PROJECT_ID/networkbuster
    
    echo ""
    echo "Deploying to Cloud Run..."
    gcloud run deploy networkbuster \
      --image gcr.io/$PROJECT_ID/networkbuster \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --port 8080
    
    echo ""
    echo "✅ Deployment Complete!"
    echo ""
    echo "🌍 Your app URL:"
    gcloud run services describe networkbuster --region us-central1 --format="value(status.url)"
    ;;
    
  3)
    echo ""
    echo "💻 Compute Engine Deployment"
    echo "────────────────────────────────────────"
    echo ""
    echo "Creating VM instance..."
    
    gcloud compute instances create networkbuster-vm \
      --zone=us-central1-a \
      --machine-type=e2-medium \
      --image-family=ubuntu-2004-lts \
      --image-project=ubuntu-os-cloud \
      --boot-disk-size=20GB \
      --tags=http-server,https-server
    
    echo ""
    echo "✅ VM Created!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. SSH into VM: gcloud compute ssh networkbuster-vm --zone=us-central1-a"
    echo "  2. Clone repo: git clone https://github.com/NetworkBuster/networkbuster.net.git"
    echo "  3. Install Python: sudo apt install python3-pip python3-venv"
    echo "  4. Setup and run: cd networkbuster.net && python3 -m venv .venv && source .venv/bin/activate"
    echo "  5. Install deps: pip install -r requirements.txt"
    echo "  6. Run: python network_map_viewer.py"
    ;;
    
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🎉 Deployment Complete!"
echo "════════════════════════════════════════════════════════════"
