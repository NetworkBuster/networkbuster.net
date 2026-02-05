# Deployment Guide
## Mercedes-NVIDIA AI Drive Platform

---

## Overview

This guide covers the deployment process for the Mercedes-NVIDIA AI Drive platform, from development to production.

---

## Prerequisites

### Hardware Requirements

- **Development**: NVIDIA Drive Developer Kit or cloud instance
- **Production**: Mercedes-Benz EQ platform vehicle (2024+)
- **Network**: 5G/LTE connectivity

### Software Requirements

- NVIDIA DriveWorks SDK 5.0+
- CUDA 12.0+
- Python 3.10+
- Docker 24.0+
- Kubernetes 1.28+ (for cloud)

### Access Requirements

- NetworkBuster Cloud account
- Mercedes-Benz Developer Portal access
- NVIDIA Developer Program membership

---

## Development Environment Setup

### 1. Install NVIDIA Drive SDK

```bash
# Download Drive SDK
wget https://developer.nvidia.com/drive/downloads/drive-sdk-5.0

# Extract and install
tar -xzf drive-sdk-5.0.tar.gz
cd drive-sdk-5.0
./install.sh

# Verify installation
drive-verify --version
```

### 2. Clone Repository

```bash
git clone https://github.com/NetworkBuster/networkbuster.net.git
cd networkbuster.net/mercedes-nvidia-ai-drive
```

### 3. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Cloud Credentials

```bash
# Copy example config
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:
```bash
NETWORKBUSTER_API_KEY=your_key_here
NVIDIA_LICENSE_KEY=your_key_here
MERCEDES_DEVELOPER_KEY=your_key_here
```

---

## Building AI Models

### 1. Prepare Training Data

```bash
# Download dataset
./scripts/download-dataset.sh --type perception

# Preprocess data
python scripts/preprocess.py --config configs/perception.yaml
```

### 2. Train Models

```bash
# Train perception model
python train.py \
  --model yolov8 \
  --config configs/perception.yaml \
  --gpus 8 \
  --epochs 100

# Train prediction model
python train.py \
  --model transformer \
  --config configs/prediction.yaml \
  --gpus 4 \
  --epochs 50
```

### 3. Convert to TensorRT

```bash
# Convert PyTorch to ONNX
python convert_to_onnx.py \
  --model checkpoints/perception_best.pth \
  --output models/perception.onnx

# Convert ONNX to TensorRT
trtexec \
  --onnx=models/perception.onnx \
  --saveEngine=models/perception.trt \
  --fp16
```

---

## Testing

### 1. Unit Tests

```bash
pytest tests/unit/ -v
```

### 2. Integration Tests

```bash
pytest tests/integration/ -v --vehicle simulator
```

### 3. Simulation Testing

```bash
# Start NVIDIA Drive Sim
drive-sim --config sim-config.yaml

# Run test scenarios
python run_sim_tests.py --scenarios all
```

---

## Deployment to Vehicle

### 1. Build Deployment Package

```bash
./scripts/build-deployment.sh \
  --target drive-orin \
  --config production
```

### 2. Flash to Vehicle

```bash
# Connect via USB or network
./scripts/connect-vehicle.sh --vin WDD1234567890

# Upload package
./scripts/deploy-to-vehicle.sh \
  --package builds/mercedes-nvidia-v2.0.tar.gz \
  --target /opt/mercedes-nvidia/

# Verify installation
./scripts/verify-deployment.sh
```

### 3. Activate System

```bash
# Enable autonomous mode
./scripts/enable-autonomy.sh --level 3

# Run system checks
./scripts/system-check.sh --verbose
```

---

## Cloud Deployment

### 1. Deploy to Kubernetes

```bash
# Build container images
docker build -t mercedes-nvidia/api:v2.0 .

# Push to registry
docker push networkbuster.azurecr.io/mercedes-nvidia/api:v2.0

# Deploy to K8s
kubectl apply -f k8s/production/
```

### 2. Configure Load Balancer

```bash
# Setup Azure Load Balancer
az network lb create \
  --resource-group mercedes-nvidia-rg \
  --name mercedes-nvidia-lb \
  --sku Standard

# Configure health probes
kubectl apply -f k8s/health-probes.yaml
```

---

## Monitoring & Maintenance

### 1. Setup Monitoring

```bash
# Deploy Prometheus
helm install prometheus prometheus-community/prometheus

# Deploy Grafana
helm install grafana grafana/grafana

# Import dashboards
./scripts/import-dashboards.sh
```

### 2. Configure Alerts

```yaml
# alerts.yaml
alerts:
  - name: high_disengagement_rate
    condition: disengagement_rate > 0.1
    action: notify_team
  
  - name: low_perception_confidence
    condition: confidence < 0.90
    action: reduce_autonomy_level
```

### 3. OTA Update Process

```bash
# Prepare update
./scripts/prepare-ota.sh --version 2.1.0

# Test in shadow mode
./scripts/shadow-test.sh --duration 7d

# Deploy to fleet (phased)
./scripts/deploy-ota.sh \
  --version 2.1.0 \
  --phase 1 \
  --percentage 5
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Failed

```bash
# Check network connectivity
ping vehicle.local

# Verify credentials
./scripts/check-credentials.sh
```

#### 2. Model Loading Error

```bash
# Verify model integrity
sha256sum models/perception.trt

# Check CUDA availability
nvidia-smi
```

#### 3. High Latency

```bash
# Profile system
nsys profile ./bin/mercedes-nvidia

# Check resource usage
top -p $(pgrep mercedes-nvidia)
```

---

## Rollback Procedure

```bash
# Identify last stable version
./scripts/list-versions.sh

# Rollback to previous version
./scripts/rollback.sh --version 2.0.0 --vin WDD1234567890

# Verify rollback
./scripts/verify-version.sh
```

---

## Security Considerations

### 1. Secure Boot

- Verify signed binaries
- Enable secure boot in vehicle
- Use TPM for key storage

### 2. Network Security

- Use VPN for development access
- Enable TLS 1.3 for all communications
- Implement certificate pinning

### 3. Data Privacy

- Anonymize all telemetry data
- Encrypt data at rest and in transit
- Follow GDPR and local regulations

---

## Production Checklist

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Simulation testing complete (10M miles)
- [ ] Real-world testing complete (500K miles)
- [ ] Security audit completed
- [ ] Regulatory approval obtained
- [ ] Documentation updated
- [ ] Training completed for support team
- [ ] Monitoring and alerts configured
- [ ] Rollback plan tested
- [ ] Emergency contact list updated

---

**Version**: 2.0  
**Last Updated**: February 5, 2026  
**Contact**: deployment@networkbuster.net
