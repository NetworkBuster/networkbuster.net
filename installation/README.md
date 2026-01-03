# NetworkBuster Installation Guide

Central hub for all installation scripts, setup guides, and deployment documentation.

## 📁 Contents

### Installation Scripts (.ps1)
| Script | Description |
|--------|-------------|
| `install-node-msi.ps1` | Install Node.js via MSI |
| `install-nvm.ps1` | Install Node Version Manager |
| `install-service-nssm.ps1` | Install as Windows service via NSSM |
| `install-nbapp-service.ps1` | Install NetworkBuster app service |
| `install-watchdog-task.ps1` | Install watchdog scheduled task |
| `install-datacentra.ps1` | Install Datacentra components |
| `install-context-menu.ps1` | Add context menu entries |

### Windows Installer
- `installer/networkbuster-installer.nsi` - NSIS installer script

### Setup Documentation
| Guide | Purpose |
|-------|---------|
| `AI_TRAINING_PIPELINE_SETUP.md` | AI/ML pipeline configuration |
| `AZURE_STORAGE_SETUP_cleanskiier27.md` | Azure storage setup |
| `CUSTOM-DOMAIN-SETUP.md` | Custom domain configuration |
| `DNS-A-RECORD-SETUP.md` | DNS record setup |
| `DOMAIN-SETUP-SUMMARY.md` | Domain setup overview |
| `HYPERV-LINUX-SETUP.md` | Hyper-V Linux VM setup |
| `PROXY_SETUP_COMPLETE.md` | Proxy configuration |
| `SETUP_COMPLETE_STATUS.md` | Setup checklist |
| `SSH_KEY_SETUP.md` | SSH key generation |
| `SSH_SETUP_GUIDE.md` | SSH configuration guide |
| `VERCEL-DOMAIN-SETUP-GUIDE.md` | Vercel deployment |

## 🚀 Quick Start

### 1. Install Node.js
```powershell
.\install-nvm.ps1
# or
.\install-node-msi.ps1
```

### 2. Install as Windows Service
```powershell
.\install-service-nssm.ps1
```

### 3. Install NetworkBuster App
```powershell
.\install-nbapp-service.ps1
```

## 📋 Prerequisites
- Windows 10/11 or Windows Server 2019+
- PowerShell 5.1+ (run as Administrator)
- Internet connection for downloads

## 🔧 Running Scripts as Admin
```powershell
Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File .\install-*.ps1"
```

---
*Generated: January 2026*
