# NetworkBuster - Quick Command Reference
# Simple commands to make everything easier

## Batch Files (Double-click or run from CMD)

```cmd
start.bat       - Start all NetworkBuster services
stop.bat        - Stop all services
status.bat      - Show current status
map.bat         - Open network map
tracer.bat      - Open API tracer
backup.bat      - Backup git to D: and K: drives
thumbnails.bat  - Extract and view thumbnails
```

## PowerShell Functions (Load with: . .\nb.ps1)

```powershell
nb-start        - Start all services
nb-stop         - Stop all services
nb-status       - Show status
nb-map          - Open network map
nb-tracer       - Open API tracer
nb-mission      - Open mission control
nb-backup       - Run git backup
nb-thumbs       - Extract thumbnails
nb-all          - Open all dashboards at once
nb-help         - Show help
```

## Python Direct Commands

```powershell
python networkbuster_launcher.py --start     # Start everything
python networkbuster_launcher.py --stop      # Stop everything
python networkbuster_launcher.py --status    # Check status
python network_map_viewer.py                 # Run map
python api_tracer.py                         # Run tracer
python flash_git_backup.py                   # Backup git
python extract_thumbnails.py                 # Extract thumbnails
```

## One-Line Quick Starts

```powershell
# Start and open Universal Launcher
python networkbuster_launcher.py --start; start http://localhost:7000

# Quick map view
python network_map_viewer.py; start http://localhost:6000

# Quick API trace
python api_tracer.py; start http://localhost:8000

# All dashboards
start http://localhost:3000,http://localhost:5000,http://localhost:6000,http://localhost:7000,http://localhost:8000
```

## URL Shortcuts

- Main Dashboard: http://localhost:7000
- Network Map: http://localhost:6000
- API Tracer: http://localhost:8000
- Mission Control: http://localhost:5000
- Web Server: http://localhost:3000
- API Server: http://localhost:3001
- Audio Stream: http://localhost:3002

## Desktop Shortcuts (Already Created)

- NetworkBuster.lnk - Main launcher
- NetworkBuster Map.lnk - Network map viewer

## Start Menu Programs

- Start → Programs → NetworkBuster → (Choose any tool)

## Simplest Usage

**Just double-click: `start.bat`**

That's it! Everything launches automatically.
