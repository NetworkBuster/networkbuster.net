#!/usr/bin/env python3
"""
NetworkBuster Cloud Device Manager
Manage 3 cloud platforms: Azure Container Apps, Azure Blob Storage, Vercel Edge
"""

import subprocess
import sys
import os
import json
import platform
from pathlib import Path
from datetime import datetime

PROJECT_PATH = Path(__file__).parent.resolve()
IS_WINDOWS = platform.system() == "Windows"

# Cloud Device Configuration
CLOUD_DEVICES = {
    "azure_containers": {
        "name": "Azure Container Apps",
        "type": "compute",
        "purpose": "Hosted Processes (Web, API, Audio servers)",
        "status": "configured",
        "region": "eastus",
        "resources": {
            "registry": "networkbusterlo25gft5nqwzg.azurecr.io",
            "resource_group": "networkbuster-rg",
            "environment": "networkbuster-env"
        },
        "services": [
            {"name": "networkbuster-server", "port": 3000, "replicas": 1},
            {"name": "networkbuster-api", "port": 3001, "replicas": 1},
            {"name": "networkbuster-audio", "port": 3002, "replicas": 1}
        ]
    },
    "azure_storage": {
        "name": "Azure Blob Storage",
        "type": "storage",
        "purpose": "Cloud Storage & Backups",
        "status": "pending",
        "region": "eastus",
        "resources": {
            "account_name": "networkbusterstorage",
            "containers": ["backups", "exports", "imports", "media"]
        },
        "local_mount": "D:\\networkbuster-cloud"
    },
    "vercel_edge": {
        "name": "Vercel Edge Network",
        "type": "cdn_serverless",
        "purpose": "CDN + Serverless API Functions",
        "status": "configured",
        "region": "global",
        "resources": {
            "project": "networkbuster",
            "domain": "networkbuster.net",
            "functions": ["/api/*"]
        }
    }
}


def run_cmd(cmd, capture=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result


def check_azure_cli():
    """Check if Azure CLI is installed and logged in."""
    result = run_cmd("az account show")
    if result.returncode == 0:
        account = json.loads(result.stdout)
        return {"logged_in": True, "user": account.get("user", {}).get("name", "unknown")}
    return {"logged_in": False}


def check_vercel_cli():
    """Check if Vercel CLI is installed."""
    result = run_cmd("vercel --version")
    return result.returncode == 0


def check_docker():
    """Check if Docker is running."""
    result = run_cmd("docker version")
    return result.returncode == 0


class CloudDeviceManager:
    """Manage cloud devices for NetworkBuster."""
    
    def __init__(self):
        self.devices = CLOUD_DEVICES.copy()
        self.check_prerequisites()
    
    def check_prerequisites(self):
        """Check required CLI tools."""
        self.prereqs = {
            "azure_cli": check_azure_cli(),
            "vercel_cli": check_vercel_cli(),
            "docker": check_docker()
        }
    
    def show_status(self):
        """Show status of all cloud devices."""
        print("\n" + "=" * 70)
        print("  ☁️  CLOUD DEVICES STATUS")
        print("=" * 70)
        
        # Prerequisites
        print("\n  📦 Prerequisites:")
        az = self.prereqs["azure_cli"]
        print(f"     Azure CLI: {'✓ Logged in as ' + az['user'] if az['logged_in'] else '✗ Not logged in'}")
        print(f"     Vercel CLI: {'✓ Installed' if self.prereqs['vercel_cli'] else '✗ Not found'}")
        print(f"     Docker: {'✓ Running' if self.prereqs['docker'] else '✗ Not running'}")
        
        print("\n" + "-" * 70)
        
        for i, (key, device) in enumerate(self.devices.items(), 1):
            status_icon = "🟢" if device["status"] == "configured" else "🟡" if device["status"] == "pending" else "🔴"
            
            print(f"\n  [{i}] {status_icon} {device['name']}")
            print(f"      Type: {device['type']}")
            print(f"      Purpose: {device['purpose']}")
            print(f"      Region: {device['region']}")
            print(f"      Status: {device['status'].upper()}")
            
            if device["type"] == "compute" and "services" in device:
                print("      Services:")
                for svc in device["services"]:
                    print(f"        - {svc['name']} (port {svc['port']})")
        
        print("\n" + "=" * 70)
    
    def deploy_azure_containers(self):
        """Deploy to Azure Container Apps."""
        print("\n🚀 Deploying to Azure Container Apps...")
        
        if not self.prereqs["azure_cli"]["logged_in"]:
            print("✗ Azure CLI not logged in. Run: az login")
            return False
        
        if not self.prereqs["docker"]:
            print("✗ Docker not running")
            return False
        
        # Run the deployment script
        deploy_script = PROJECT_PATH / "deploy-azure.ps1"
        if deploy_script.exists():
            if IS_WINDOWS:
                result = run_cmd(f'powershell -ExecutionPolicy Bypass -File "{deploy_script}"', capture=False)
            else:
                result = run_cmd(f'pwsh -File "{deploy_script}"', capture=False)
            return result.returncode == 0
        else:
            print("✗ deploy-azure.ps1 not found")
            return False
    
    def setup_azure_storage(self):
        """Setup Azure Blob Storage account."""
        print("\n📦 Setting up Azure Blob Storage...")
        
        if not self.prereqs["azure_cli"]["logged_in"]:
            print("✗ Azure CLI not logged in. Run: az login")
            return False
        
        device = self.devices["azure_storage"]
        account_name = device["resources"]["account_name"]
        rg = self.devices["azure_containers"]["resources"]["resource_group"]
        location = device["region"]
        
        # Create storage account
        print(f"  Creating storage account: {account_name}")
        result = run_cmd(f'az storage account create --name {account_name} --resource-group {rg} --location {location} --sku Standard_LRS')
        
        if result.returncode == 0:
            print(f"  ✓ Storage account created")
            
            # Create containers
            for container in device["resources"]["containers"]:
                print(f"  Creating container: {container}")
                run_cmd(f'az storage container create --name {container} --account-name {account_name}')
            
            self.devices["azure_storage"]["status"] = "configured"
            print("✓ Azure Blob Storage configured")
            return True
        else:
            print(f"✗ Failed: {result.stderr}")
            return False
    
    def deploy_vercel(self):
        """Deploy to Vercel."""
        print("\n🔺 Deploying to Vercel Edge...")
        
        if not self.prereqs["vercel_cli"]:
            print("✗ Vercel CLI not found. Install: npm i -g vercel")
            return False
        
        os.chdir(PROJECT_PATH)
        result = run_cmd("vercel --prod", capture=False)
        return result.returncode == 0
    
    def sync_local_to_cloud(self):
        """Sync local D: drive to Azure Blob Storage."""
        print("\n🔄 Syncing local storage to Azure Blob...")
        
        local_path = self.devices["azure_storage"]["local_mount"]
        account_name = self.devices["azure_storage"]["resources"]["account_name"]
        
        if not os.path.exists(local_path):
            print(f"✗ Local path not found: {local_path}")
            return False
        
        # Use azcopy for sync
        result = run_cmd("azcopy --version")
        if result.returncode != 0:
            print("⚠ azcopy not found. Using az storage blob upload-batch...")
            
            for container in ["backups", "exports"]:
                source = os.path.join(local_path, container)
                if os.path.exists(source):
                    print(f"  Uploading {container}...")
                    run_cmd(f'az storage blob upload-batch --account-name {account_name} --destination {container} --source "{source}"')
        else:
            # Use azcopy for faster sync
            print("  Using azcopy for sync...")
            run_cmd(f'azcopy sync "{local_path}" "https://{account_name}.blob.core.windows.net/backups" --recursive')
        
        print("✓ Sync complete")
        return True
    
    def download_from_cloud(self, container="backups"):
        """Download files from Azure Blob to local."""
        print(f"\n⬇️  Downloading from Azure Blob ({container})...")
        
        local_path = self.devices["azure_storage"]["local_mount"]
        account_name = self.devices["azure_storage"]["resources"]["account_name"]
        dest = os.path.join(local_path, container)
        
        os.makedirs(dest, exist_ok=True)
        
        result = run_cmd(f'az storage blob download-batch --account-name {account_name} --source {container} --destination "{dest}"')
        
        if result.returncode == 0:
            print(f"✓ Downloaded to {dest}")
            return True
        else:
            print(f"✗ Download failed")
            return False
    
    def scale_container(self, service_name, replicas):
        """Scale a container app."""
        print(f"\n📈 Scaling {service_name} to {replicas} replicas...")
        
        rg = self.devices["azure_containers"]["resources"]["resource_group"]
        
        result = run_cmd(f'az containerapp update --name {service_name} --resource-group {rg} --min-replicas {replicas} --max-replicas {replicas * 2}')
        
        if result.returncode == 0:
            print(f"✓ {service_name} scaled to {replicas} replicas")
            return True
        else:
            print(f"✗ Scaling failed")
            return False
    
    def get_logs(self, service_name):
        """Get logs from container app."""
        print(f"\n📋 Fetching logs for {service_name}...")
        
        rg = self.devices["azure_containers"]["resources"]["resource_group"]
        
        run_cmd(f'az containerapp logs show --name {service_name} --resource-group {rg} --follow', capture=False)
    
    def generate_cost_estimate(self):
        """Estimate monthly cloud costs."""
        print("\n" + "=" * 70)
        print("  💰 ESTIMATED MONTHLY COSTS")
        print("=" * 70)
        
        costs = {
            "Azure Container Apps": {
                "compute": "$0 - $50 (consumption tier)",
                "notes": "Free tier: 2M requests/month, 180K vCPU-sec"
            },
            "Azure Blob Storage": {
                "storage": "$0.018/GB (Hot tier)",
                "operations": "$0.004/10K operations",
                "estimate": "~$5/month for 100GB"
            },
            "Vercel Edge": {
                "hosting": "$0 (Hobby tier)",
                "bandwidth": "100GB free",
                "functions": "100K invocations free"
            }
        }
        
        total_low = 0
        total_high = 55
        
        for service, pricing in costs.items():
            print(f"\n  {service}:")
            for key, value in pricing.items():
                print(f"    {key}: {value}")
        
        print(f"\n  📊 Estimated Total: ${total_low} - ${total_high}/month")
        print("=" * 70)


def show_menu():
    """Display cloud management menu."""
    print("\n" + "─" * 60)
    print("  ☁️  CLOUD DEVICE MANAGER")
    print("─" * 60)
    print("  [1] 📊 Show Status (all devices)")
    print("  [2] 🚀 Deploy to Azure Container Apps")
    print("  [3] 📦 Setup Azure Blob Storage")
    print("  [4] 🔺 Deploy to Vercel Edge")
    print("  [5] 🔄 Sync Local → Cloud Storage")
    print("  [6] ⬇️  Download from Cloud Storage")
    print("  [7] 📈 Scale Container")
    print("  [8] 📋 View Logs")
    print("  [9] 💰 Cost Estimate")
    print("  [0] ❌ Exit")
    print("─" * 60)


def main():
    """Main entry point."""
    manager = CloudDeviceManager()
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  NetworkBuster Cloud Device Manager".center(58) + "║")
    print("║" + "  Azure Containers | Azure Storage | Vercel Edge".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    while True:
        show_menu()
        choice = input("\n  Select option [0-9]: ").strip()
        
        if choice == "1":
            manager.show_status()
        elif choice == "2":
            manager.deploy_azure_containers()
        elif choice == "3":
            manager.setup_azure_storage()
        elif choice == "4":
            manager.deploy_vercel()
        elif choice == "5":
            manager.sync_local_to_cloud()
        elif choice == "6":
            container = input("  Container (backups/exports/imports): ").strip() or "backups"
            manager.download_from_cloud(container)
        elif choice == "7":
            print("  Services: networkbuster-server, networkbuster-api, networkbuster-audio")
            service = input("  Service name: ").strip()
            replicas = int(input("  Replicas: ").strip() or "1")
            manager.scale_container(service, replicas)
        elif choice == "8":
            print("  Services: networkbuster-server, networkbuster-api, networkbuster-audio")
            service = input("  Service name: ").strip()
            manager.get_logs(service)
        elif choice == "9":
            manager.generate_cost_estimate()
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n⚠ Invalid option.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
