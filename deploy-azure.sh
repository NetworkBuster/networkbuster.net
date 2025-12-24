#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 NetworkBuster Azure Deployment${NC}"
echo "=================================="

# Configuration
RESOURCE_GROUP="networkbuster-rg"
REGISTRY_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name main --query 'properties.outputs.containerRegistryLoginServer.value' -o tsv | cut -d'.' -f1)
REGISTRY_URL=$(az deployment group show --resource-group $RESOURCE_GROUP --name main --query 'properties.outputs.containerRegistryLoginServer.value' -o tsv)

echo -e "${GREEN}✓ Resource Group: $RESOURCE_GROUP${NC}"
echo -e "${GREEN}✓ Registry: $REGISTRY_URL${NC}"

# Login to Azure Container Registry
echo -e "${YELLOW}📦 Logging into Container Registry...${NC}"
az acr login --name $REGISTRY_NAME

# Build and push Main Server image
echo -e "${YELLOW}🔨 Building Main Server image...${NC}"
az acr build --registry $REGISTRY_NAME --image networkbuster-server:latest --image networkbuster-server:$(git rev-parse --short HEAD) .

# Build and push Overlay image
echo -e "${YELLOW}🔨 Building Overlay UI image...${NC}"
az acr build --registry $REGISTRY_NAME --image networkbuster-overlay:latest --image networkbuster-overlay:$(git rev-parse --short HEAD) challengerepo/real-time-overlay

# Optional: Build & push a .NET image if DOTNET_PROJECT is provided
if [ -n "$DOTNET_PROJECT" ]; then
  echo -e "${YELLOW}🔨 Building DotNet image from $DOTNET_PROJECT...${NC}"
  az acr build --registry $REGISTRY_NAME --image ${DOTNET_IMAGE:-networkbuster-dotnet-server}:latest $DOTNET_PROJECT
  echo -e "${GREEN}✓ DotNet image built and pushed: $REGISTRY_URL/${DOTNET_IMAGE:-networkbuster-dotnet-server}:latest${NC}"

  # Deploy or update dotnet container app
  DOTNET_APP_NAME="networkbuster-dotnet"
  if az containerapp show --name $DOTNET_APP_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    echo -e "${YELLOW}🔁 Updating Container App '$DOTNET_APP_NAME' with new image...${NC}"
    az containerapp update --name $DOTNET_APP_NAME --resource-group $RESOURCE_GROUP --image $REGISTRY_URL/${DOTNET_IMAGE:-networkbuster-dotnet-server}:latest
  else
    echo -e "${YELLOW}✨ Creating Container App '$DOTNET_APP_NAME' (ingress enabled)...${NC}"
    az containerapp create --name $DOTNET_APP_NAME --resource-group $RESOURCE_GROUP --environment networkbuster-env --image $REGISTRY_URL/${DOTNET_IMAGE:-networkbuster-dotnet-server}:latest --ingress 'external' --target-port 80
  fi

  DOTNET_FQDN=$(az containerapp show --name $DOTNET_APP_NAME --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)
  echo -e "${GREEN}✓ DotNet Container App: $DOTNET_FQDN${NC}"
  if [ -n "$MAP_DOMAIN" ] && [ -n "$DOMAIN" ]; then
    echo -e "\n${YELLOW}⚠️ DNS NOTE: Create a CNAME record 'www' -> $DOTNET_FQDN (or your desired host) and then follow Azure Container Apps docs to bind a custom domain and certificate.${NC}"
    echo "Docs: https://learn.microsoft.com/azure/container-apps/custom-domains"
  else
    echo -e "\nCreate CNAME 'www' -> $DOTNET_FQDN to expose the dotnet app via your DNS provider." 
  fi
fi

# Update Container Apps
echo -e "${YELLOW}🚀 Updating Container Apps...${NC}"
az containerapp update \
  --name networkbuster-server \
  --resource-group $RESOURCE_GROUP \
  --image $REGISTRY_URL/networkbuster-server:latest

az containerapp update \
  --name networkbuster-overlay \
  --resource-group $RESOURCE_GROUP \
  --image $REGISTRY_URL/networkbuster-overlay:latest

# Output URLs
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}📊 Deployment URLs:${NC}"
echo "Main Server: $(az containerapp show --name networkbuster-server --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)"
echo "Overlay UI: $(az containerapp show --name networkbuster-overlay --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)"
