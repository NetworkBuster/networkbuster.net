# NetworkBuster Azure Deployment Script
# This script deploys the Azure runtime infrastructure

param(
    [string]$ResourceGroup = "networkbuster-rg",
    [string]$Location = "eastus",
    [string]$RegistryName = "networkbusterlo25gft5nqwzg",
    [string]$DotNetProject = '',        # Path to dotnet project folder containing Dockerfile (optional)
    [string]$DotNetImage = 'networkbuster-dotnet-server',
    [string]$Domain = 'www.networkbuster.org',
    [switch]$MapDomain,                    # If supplied, attempt to map $Domain to resulting Container App (prints instructions if not possible)
    [switch]$SetupServiceBus               # If supplied, create Azure Service Bus namespace and topic for device registrations
) 

Write-Host "🚀 NetworkBuster Azure Deployment" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if logged in to Azure
Write-Host "📍 Checking Azure login..." -ForegroundColor Yellow
$account = az account show --output json | ConvertFrom-Json
if (-not $account) {
    Write-Host "❌ Not logged into Azure. Running 'az login'..." -ForegroundColor Red
    az login
}

Write-Host "✓ Logged in as: $($account.user.name)" -ForegroundColor Green
Write-Host ""

# Get Registry Details
Write-Host "🔍 Getting Container Registry details..." -ForegroundColor Yellow
$registry = az acr show --resource-group $ResourceGroup --name $RegistryName --output json | ConvertFrom-Json
$registryUrl = $registry.loginServer
Write-Host "✓ Registry: $registryUrl" -ForegroundColor Green
Write-Host ""

# Setup Azure Service Bus if requested
if ($SetupServiceBus) {
    Write-Host "🚌 Setting up Azure Service Bus..." -ForegroundColor Yellow
    $sbNamespace = "networkbuster-sb"
    $topicName = "device-registrations.v1"
    
    # Check if namespace exists
    $sbExists = az servicebus namespace show --resource-group $ResourceGroup --name $sbNamespace --query name -o tsv 2>$null
    if (-not $sbExists) {
        Write-Host "✨ Creating Service Bus namespace '$sbNamespace'..." -ForegroundColor Yellow
        az servicebus namespace create --resource-group $ResourceGroup --name $sbNamespace --location $Location --sku Standard
        Write-Host "✓ Service Bus namespace created" -ForegroundColor Green
    } else {
        Write-Host "✓ Service Bus namespace '$sbNamespace' already exists" -ForegroundColor Green
    }
    
    # Create topic
    $topicExists = az servicebus topic show --resource-group $ResourceGroup --namespace-name $sbNamespace --name $topicName --query name -o tsv 2>$null
    if (-not $topicExists) {
        Write-Host "✨ Creating topic '$topicName'..." -ForegroundColor Yellow
        az servicebus topic create --resource-group $ResourceGroup --namespace-name $sbNamespace --name $topicName
        Write-Host "✓ Topic created" -ForegroundColor Green
    } else {
        Write-Host "✓ Topic '$topicName' already exists" -ForegroundColor Green
    }
    
    # Get connection string
    $sbConnectionString = az servicebus namespace authorization-rule keys list --resource-group $ResourceGroup --namespace-name $sbNamespace --name RootManageSharedAccessKey --query primaryConnectionString -o tsv
    Write-Host "✓ Service Bus connection string retrieved" -ForegroundColor Green
    Write-Host "   (Set as env var: AZURE_SERVICEBUS_CONNECTION_STRING)" -ForegroundColor Cyan
    Write-Host ""
}

# Check Docker
Write-Host "🐳 Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green

    # Login to ACR
    Write-Host "📋 Logging into Azure Container Registry..." -ForegroundColor Yellow
    az acr login --name $RegistryName

    # Build Main Server image
    Write-Host "🔨 Building Main Server image..." -ForegroundColor Yellow
    docker build -t "$registryUrl/networkbuster-server:latest" -f Dockerfile .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Main Server image built successfully" -ForegroundColor Green

        # Push Main Server image
        Write-Host "📤 Pushing Main Server image..." -ForegroundColor Yellow
        docker push "$registryUrl/networkbuster-server:latest"
        Write-Host "✓ Main Server image pushed" -ForegroundColor Green
    }

    # Build Overlay UI image
    Write-Host "🔨 Building Overlay UI image..." -ForegroundColor Yellow
    docker build -t "$registryUrl/networkbuster-overlay:latest" -f challengerepo\real-time-overlay\Dockerfile .\challengerepo\real-time-overlay
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Overlay UI image built successfully" -ForegroundColor Green

        # Push Overlay UI image
        Write-Host "📤 Pushing Overlay UI image..." -ForegroundColor Yellow
        docker push "$registryUrl/networkbuster-overlay:latest"
        Write-Host "✓ Overlay UI image pushed" -ForegroundColor Green
    }

    # Optional: build/push DotNet image if requested
    if ($DotNetProject -and (Test-Path -Path $DotNetProject)) {
        Write-Host ""; Write-Host "🔨 Building DotNet image from: $DotNetProject" -ForegroundColor Yellow
        try {
            az acr build --registry $RegistryName --image $DotNetImage:latest $DotNetProject
            Write-Host "✓ DotNet image built and pushed to: $registryUrl/$DotNetImage:latest" -ForegroundColor Green

            # Deploy or update Container App for DotNet
            $dotnetAppName = 'networkbuster-dotnet'
            $exists = az containerapp show --name $dotnetAppName --resource-group $ResourceGroup --query name -o tsv 2>$null
            if ($exists) {
                Write-Host "🔁 Updating Container App '$dotnetAppName' with new image..." -ForegroundColor Yellow
                az containerapp update --name $dotnetAppName --resource-group $ResourceGroup --image "$registryUrl/$DotNetImage:latest"
            } else {
                Write-Host "✨ Creating Container App '$dotnetAppName' (ingress enabled) ..." -ForegroundColor Yellow
                az containerapp create --name $dotnetAppName --resource-group $ResourceGroup --environment networkbuster-env --image "$registryUrl/$DotNetImage:latest" --ingress 'external' --target-port 80
            }

            $dotnetFqdn = az containerapp show --name $dotnetAppName --resource-group $ResourceGroup --query 'properties.configuration.ingress.fqdn' -o tsv
            Write-Host "✓ DotNet Container App: $dotnetFqdn" -ForegroundColor Green

            if ($MapDomain) {
                Write-Host ""; Write-Host "⚠️ Attempting to map domain '$Domain' to $dotnetAppName" -ForegroundColor Yellow
                Write-Host "Please ensure DNS: create a CNAME record 'www' pointing to: $dotnetFqdn" -ForegroundColor Cyan
                Write-Host "After DNS propagates, follow Azure docs to bind the custom domain and issue a certificate for the Container App." -ForegroundColor Cyan
                Write-Host "Docs: https://learn.microsoft.com/azure/container-apps/custom-domains" -ForegroundColor Cyan
            } else {
                Write-Host "To expose via custom domain: Create CNAME 'www' -> $dotnetFqdn and then bind certificate per Azure docs." -ForegroundColor Cyan
            }
        } catch {
            Write-Warning "DotNet build or Container App update failed: $($_.Exception.Message)"
        }
    } else {
        Write-Host "No DotNet project supplied or path not found; skipping DotNet build." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "✅ Docker images built and pushed successfully" -ForegroundColor Green
} 
catch {
    Write-Host "⚠️  Docker is not running or not installed" -ForegroundColor Yellow
    Write-Host "📝 Skip local Docker builds" -ForegroundColor Yellow
    Write-Host "   Images can be pushed later when Docker is available" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Azure Deployment Summary" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroup"  
Write-Host "Container Registry: $registryUrl"
Write-Host "Location: $Location"
if ($SetupServiceBus) {
    Write-Host "Service Bus Namespace: $sbNamespace"
    Write-Host "Topic: $topicName"
    Write-Host "Connection String: [hidden - set AZURE_SERVICEBUS_CONNECTION_STRING]"
}
Write-Host ""
Write-Host "✅ Base infrastructure is ready for deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Build and push Docker images (or use the script with Docker running)"
Write-Host "2. Update Container Apps with the new images using:"
Write-Host "   az containerapp create --name networkbuster-server ..."
Write-Host "   az containerapp create --name networkbuster-overlay ..."
if ($SetupServiceBus) {
    Write-Host "3. Set environment variable: `$env:AZURE_SERVICEBUS_CONNECTION_STRING = '$sbConnectionString'"
    Write-Host "4. Deploy consumer worker as Container App or Function App"
}
Write-Host ""
