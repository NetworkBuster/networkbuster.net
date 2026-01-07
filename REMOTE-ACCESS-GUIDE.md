# NetworkBuster Remote Access Guide

## 🌐 Secure Remote Access Options

Your ISP blocks port 6000 (X11 security risk). We've moved to safer ports and here's how to access remotely:

### ✅ New Safe Ports
- **NetworkBuster AI**: `http://localhost:8000` (was 4000)
- **Network Map Viewer**: `http://localhost:8080` (was 6000)

---

## 🚀 Option 1: Cloudflare Tunnel (Recommended - FREE)

**Advantages**: Free, secure HTTPS, no port forwarding, works with any ISP

### Setup Steps:

1. **Install Cloudflare Tunnel**:
   ```powershell
   # Download cloudflared
   Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
   ```

2. **Login to Cloudflare**:
   ```powershell
   .\cloudflared.exe tunnel login
   ```

3. **Create Tunnel**:
   ```powershell
   .\cloudflared.exe tunnel create networkbuster
   ```

4. **Route Traffic**:
   ```powershell
   # For Network Map
   .\cloudflared.exe tunnel route dns networkbuster map.yourdomain.com
   
   # For NetworkBuster AI
   .\cloudflared.exe tunnel route dns networkbuster ai.yourdomain.com
   ```

5. **Create config.yml**:
   ```yaml
   tunnel: <your-tunnel-id>
   credentials-file: C:\Users\daypi\.cloudflared\<tunnel-id>.json
   
   ingress:
     - hostname: map.yourdomain.com
       service: http://localhost:8080
     - hostname: ai.yourdomain.com
       service: http://localhost:8000
     - service: http_status:404
   ```

6. **Run Tunnel**:
   ```powershell
   .\cloudflared.exe tunnel run networkbuster
   ```

**Access from anywhere**: `https://map.yourdomain.com` and `https://ai.yourdomain.com`

---

## 🔒 Option 2: ngrok (Quick Testing - FREE Tier)

**Advantages**: Instant setup, no configuration, temporary URLs

### Setup Steps:

1. **Download ngrok**:
   ```powershell
   # Visit https://ngrok.com/download
   # Extract ngrok.exe to your project folder
   ```

2. **Sign up & Get Auth Token**:
   - Create free account at https://dashboard.ngrok.com
   - Copy your auth token

3. **Configure**:
   ```powershell
   .\ngrok.exe authtoken YOUR_AUTH_TOKEN
   ```

4. **Start Tunnels**:
   ```powershell
   # Terminal 1 - Network Map
   .\ngrok.exe http 8080 --region us
   
   # Terminal 2 - NetworkBuster AI
   .\ngrok.exe http 8000 --region us
   ```

5. **Get URLs**:
   - ngrok displays URLs like: `https://abc123.ngrok-free.app`
   - Share these URLs for remote access

**Limitations**: 
- Free tier: URLs change each restart
- 40 connections/minute limit
- ngrok branding banner

**Upgrade**: $8/month for permanent URLs

---

## 🔐 Option 3: Tailscale VPN (Most Secure)

**Advantages**: Encrypted VPN, works everywhere, free for personal use

### Setup Steps:

1. **Install Tailscale**:
   ```powershell
   # Download from https://tailscale.com/download/windows
   # Run installer
   ```

2. **Login**:
   - Tailscale icon appears in system tray
   - Click and login with Google/Microsoft/GitHub

3. **Install on Remote Device**:
   - Install Tailscale on phone/laptop/tablet
   - Login with same account

4. **Access Services**:
   - Your PC gets a Tailscale IP like `100.64.0.1`
   - From remote device: `http://100.64.0.1:8080` (Network Map)
   - From remote device: `http://100.64.0.1:8000` (AI Dashboard)

**Best for**: Personal use, multiple devices, maximum security

---

## 🏠 Option 4: Port Forwarding (If ISP Allows)

**Only if you own your router and ISP doesn't block ports**

### Steps:

1. **Router Settings**:
   - Login to router (usually `192.168.1.1`)
   - Find "Port Forwarding" or "NAT" settings

2. **Add Rules**:
   ```
   External Port: 8080 → Internal IP: 192.168.1.X → Internal Port: 8080
   External Port: 8000 → Internal IP: 192.168.1.X → Internal Port: 8000
   ```

3. **Find Public IP**:
   ```powershell
   Invoke-RestMethod -Uri "https://api.ipify.org"
   ```

4. **Access**:
   - `http://YOUR_PUBLIC_IP:8080`
   - `http://YOUR_PUBLIC_IP:8000`

**⚠️ Security Risks**:
- Services exposed to entire internet
- No encryption (use HTTPS certificate)
- DDoS risk
- IP changes if not static

**Recommended**: Use with Cloudflare or reverse proxy

---

## 🎯 Quick Comparison

| Solution | Cost | Setup Time | Security | Permanent |
|----------|------|------------|----------|-----------|
| **Cloudflare Tunnel** | Free | 10 min | ⭐⭐⭐⭐⭐ | Yes |
| **ngrok** | Free* | 2 min | ⭐⭐⭐⭐ | No* |
| **Tailscale VPN** | Free | 5 min | ⭐⭐⭐⭐⭐ | Yes |
| **Port Forwarding** | Free | 15 min | ⭐⭐ | Yes |

*ngrok free URLs change each restart; $8/month for permanent

---

## 🚀 Recommended Setup

**For You (Remote Internet Access)**:

1. **Immediate**: Use **ngrok** for testing today
2. **Production**: Set up **Cloudflare Tunnel** for permanent access
3. **Mobile**: Add **Tailscale** for secure on-the-go access

### Quick Start Script:

```powershell
# Start services on safe ports
Start-Process powershell -ArgumentList "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python networkbuster_ai.py"
Start-Process powershell -ArgumentList "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python network_map_viewer.py"

# Start ngrok tunnels (if installed)
Start-Process powershell -ArgumentList "cd '$PWD'; .\ngrok.exe http 8000 --region us"
Start-Process powershell -ArgumentList "cd '$PWD'; .\ngrok.exe http 8080 --region us"
```

---

## 📱 Access URLs

**Local**:
- Network Map: http://localhost:8080
- AI Dashboard: http://localhost:8000

**Remote** (depends on solution):
- Cloudflare: https://map.yourdomain.com
- ngrok: https://abc123.ngrok-free.app
- Tailscale: http://100.64.0.x:8080
- Port Forward: http://YOUR_IP:8080

---

## 🆘 Troubleshooting

### Can't access locally?
```powershell
# Check if services are running
Get-NetTCPConnection -LocalPort 8000,8080 -State Listen -ErrorAction SilentlyContinue
```

### Cloudflare tunnel won't start?
- Check credentials file path in config.yml
- Verify tunnel is created: `cloudflared tunnel list`

### ngrok says "tunnel session limit"?
- Free tier: 1 agent = max 2 tunnels simultaneously
- Upgrade or use separate accounts

### Tailscale can't connect?
- Check Windows Firewall
- Allow Tailscale in firewall settings
- Restart Tailscale service

---

## 🔗 Additional Resources

- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [ngrok Documentation](https://ngrok.com/docs)
- [Tailscale Getting Started](https://tailscale.com/kb/1017/install/)
- [NetworkBuster GitHub](https://github.com/NetworkBuster/networkbuster.net)

---

**Next Steps**: Choose a solution above and follow the setup steps. Need help? The AI dashboard at port 8000 can guide you through setup!
