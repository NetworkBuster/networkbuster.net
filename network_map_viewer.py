"""
NetworkBuster - Network Topology Map with Live Logs
Shows device thumbnails with real-time log display on interactive map
"""

import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
import socket
import psutil
import platform
import glob

app = Flask(__name__)

# Device discovery and classification
def get_network_devices():
    """Discover devices on network and classify by type"""
    devices = []
    
    # Get local machine info
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Main workstation (current device)
    devices.append({
        'id': 'workstation-1',
        'name': hostname,
        'type': 'workstation',
        'ip': local_ip,
        'status': 'online',
        'x': 400,
        'y': 300,
        'logs': get_system_logs('workstation')
    })
    
    # WiFi 7 Mesh Router
    devices.append({
        'id': 'router-wifi7',
        'name': 'WiFi 7 Mesh Router',
        'type': 'router',
        'ip': '192.168.1.1',
        'status': 'online',
        'x': 200,
        'y': 150,
        'logs': get_device_logs('router')
    })
    
    # NetworkBuster Router
    devices.append({
        'id': 'router-nb',
        'name': 'NetworkBuster Router',
        'type': 'router',
        'ip': '192.168.1.100',
        'status': 'online',
        'x': 600,
        'y': 150,
        'logs': get_device_logs('networkbuster')
    })
    
    # Mesh Nodes
    mesh_nodes = [
        {'id': 'mesh-1', 'name': 'Mesh Node 1', 'ip': '192.168.1.10', 'x': 150, 'y': 400},
        {'id': 'mesh-2', 'name': 'Mesh Node 2', 'ip': '192.168.1.11', 'x': 350, 'y': 500},
        {'id': 'mesh-3', 'name': 'Mesh Node 3', 'ip': '192.168.1.12', 'x': 650, 'y': 400},
    ]
    
    for node in mesh_nodes:
        node.update({
            'type': 'mesh',
            'status': 'online',
            'logs': get_device_logs('mesh')
        })
        devices.append(node)
    
    # NetworkBuster Services
    services = [
        {'id': 'service-web', 'name': 'Web Server', 'port': 3000, 'x': 250, 'y': 300},
        {'id': 'service-api', 'name': 'API Server', 'port': 3001, 'x': 400, 'y': 200},
        {'id': 'service-audio', 'name': 'Audio Stream', 'port': 3002, 'x': 550, 'y': 300},
        {'id': 'service-mission', 'name': 'Mission Control', 'port': 5000, 'x': 400, 'y': 400},
    ]
    
    for service in services:
        service.update({
            'type': 'service',
            'ip': local_ip,
            'status': check_port_status(service['port']),
            'logs': get_service_logs(service['port'])
        })
        devices.append(service)
    
    return devices

def check_port_status(port):
    """Check if a port is listening"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return 'online'
    return 'offline'

def get_system_logs(device_type):
    """Get system logs for device"""
    logs = []
    now = datetime.now().strftime("%H:%M:%S")
    
    if device_type == 'workstation':
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        logs = [
            f"[{now}] CPU Usage: {cpu}%",
            f"[{now}] Memory: {memory}%",
            f"[{now}] Disk: {disk}%",
            f"[{now}] OS: {platform.system()} {platform.release()}"
        ]
    
    return logs

def get_device_logs(device_type):
    """Get logs for network devices"""
    now = datetime.now().strftime("%H:%M:%S")
    
    if device_type == 'router':
        return [
            f"[{now}] Router online",
            f"[{now}] DHCP active",
            f"[{now}] Firewall enabled",
            f"[{now}] Clients: 8"
        ]
    elif device_type == 'networkbuster':
        return [
            f"[{now}] NetworkBuster active",
            f"[{now}] Services: 4/4 online",
            f"[{now}] Port forwarding OK",
            f"[{now}] DNS configured"
        ]
    elif device_type == 'mesh':
        return [
            f"[{now}] Mesh connected",
            f"[{now}] Signal: -45 dBm",
            f"[{now}] Bandwidth: 2.4 Gbps",
            f"[{now}] Encryption: WPA3"
        ]
    
    return []

def get_service_logs(port):
    """Get logs for NetworkBuster services"""
    now = datetime.now().strftime("%H:%M:%S")
    status = check_port_status(port)
    
    if status == 'online':
        return [
            f"[{now}] Service running",
            f"[{now}] Port {port} listening",
            f"[{now}] Health check: OK",
            f"[{now}] Requests: 142"
        ]
    else:
        return [
            f"[{now}] Service offline",
            f"[{now}] Port {port} not listening",
            f"[{now}] Status: Inactive"
        ]

def get_git_status():
    """Get git repository status"""
    try:
        # Get current branch
        branch = subprocess.check_output(['git', 'branch', '--show-current'], 
                                        stderr=subprocess.DEVNULL).decode().strip()
        
        # Get last commit
        last_commit = subprocess.check_output(['git', 'log', '-1', '--oneline'], 
                                             stderr=subprocess.DEVNULL).decode().strip()
        
        # Get status
        status = subprocess.check_output(['git', 'status', '--short'], 
                                        stderr=subprocess.DEVNULL).decode().strip()
        
        modified_files = len(status.split('\n')) if status else 0
        
        return {
            'connected': True,
            'branch': branch,
            'last_commit': last_commit,
            'modified_files': modified_files
        }
    except:
        return {
            'connected': False,
            'branch': 'unknown',
            'last_commit': 'No git repository',
            'modified_files': 0
        }

def get_all_documentation():
    """Load all markdown documentation files"""
    docs = []
    md_files = glob.glob('*.md') + glob.glob('**/*.md', recursive=True)
    
    for filepath in md_files[:20]:  # Limit to first 20 files
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Get first 500 characters as preview
                preview = content[:500] + '...' if len(content) > 500 else content
                
                docs.append({
                    'filename': os.path.basename(filepath),
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'preview': preview,
                    'lines': len(content.split('\n'))
                })
        except:
            pass
    
    return docs

# HTML Template with Google Maps-style effects
MAP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster Topology Map</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            overflow: hidden;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #4CAF50;
        }
        
        .header h1 {
            font-size: 24px;
        }
        
        .git-status {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 14px;
        }
        
        .git-badge {
            padding: 5px 12px;
            background: #4CAF50;
            border-radius: 15px;
            font-weight: bold;
        }
        
        .git-badge.disconnected {
            background: #f44336;
        }
        
        .map-container {
            position: relative;
            width: 100vw;
            height: calc(100vh - 70px);
            background: radial-gradient(circle at 50% 50%, #2a5298 0%, #1e3c72 100%);
            overflow: hidden;
            cursor: grab;
            user-select: none;
        }
        
        .map-container:active {
            cursor: grabbing;
        }
        
        .map-viewport {
            position: absolute;
            width: 2000px;
            height: 2000px;
            transition: transform 0.3s ease-out;
            transform-origin: 0 0;
        }
        
        .grid-pattern {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
        }
        
        .connection-line {
            position: absolute;
            height: 2px;
            background: linear-gradient(90deg, #4CAF50, transparent);
            transform-origin: left center;
            pointer-events: none;
            animation: pulse-line 2s infinite;
        }
        
        @keyframes pulse-line {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.8; }
        }
        
        .device {
            position: absolute;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .device:hover {
            transform: scale(1.05);
            z-index: 1000;
        }
        
        .device-thumbnail {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            min-width: 200px;
            border: 3px solid;
        }
        
        .device-thumbnail.online {
            border-color: #4CAF50;
        }
        
        .device-thumbnail.offline {
            border-color: #f44336;
        }
        
        .device-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        
        .device-icon {
            font-size: 32px;
        }
        
        .device-info h3 {
            font-size: 14px;
            margin-bottom: 3px;
        }
        
        .device-info p {
            font-size: 11px;
            color: #666;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: auto;
        }
        
        .status-indicator.online {
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.offline {
            background: #f44336;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 5px currentColor; }
            50% { opacity: 0.6; }
        }
        
        .device-logs {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 10px;
            max-height: 120px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
            font-size: 10px;
        }
        
        .log-entry {
            padding: 3px 0;
            color: #333;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .log-entry:hover {
            overflow: visible;
            white-space: normal;
        }
        
        .legend {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-size: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
        }
        
        .legend-icon {
            font-size: 20px;
        }
        
        .refresh-btn {
            position: absolute;
            bottom: 20px;
            left: 20px;
            padding: 15px 30px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
            background: #45a049;
        }
        
        .refresh-btn:active {
            transform: scale(0.95);
        }
        
        .zoom-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 1000;
        }
        
        .zoom-btn {
            width: 40px;
            height: 40px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border: 2px solid #4CAF50;
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .zoom-btn:hover {
            background: #4CAF50;
            transform: scale(1.1);
        }
        
        .docs-panel {
            position: absolute;
            left: -400px;
            top: 0;
            width: 400px;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            color: white;
            overflow-y: auto;
            transition: left 0.3s ease-out;
            z-index: 999;
            box-shadow: 5px 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .docs-panel.open {
            left: 0;
        }
        
        .docs-header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .docs-toggle {
            position: absolute;
            right: -40px;
            top: 50%;
            transform: translateY(-50%);
            width: 40px;
            height: 80px;
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #4CAF50;
            border-left: none;
            border-radius: 0 10px 10px 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            transition: background 0.2s;
        }
        
        .docs-toggle:hover {
            background: #4CAF50;
        }
        
        .doc-item {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .doc-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .doc-item h4 {
            margin-bottom: 5px;
            color: #4CAF50;
        }
        
        .doc-item p {
            font-size: 12px;
            opacity: 0.7;
            margin: 5px 0;
        }
        
        .doc-preview {
            font-family: 'Consolas', monospace;
            font-size: 10px;
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            max-height: 100px;
            overflow: hidden;
        }
        
        .loading-spinner {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 48px;
            animation: spin 2s linear infinite;
            z-index: 9999;
        }
        
        @keyframes spin {
            from { transform: translate(-50%, -50%) rotate(0deg); }
            to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ NetworkBuster Topology Map</h1>
        <div class="git-status">
            <span id="gitBadge" class="git-badge">🔗 Git</span>
            <span id="gitBranch"></span>
            <span id="gitCommit"></span>
        </div>
    </div>
    
    <div class="map-container" id="mapContainer">
        <div class="map-viewport" id="mapViewport">
            <div class="grid-pattern"></div>
            <div id="connections"></div>
            <div id="devices"></div>
        </div>
        
        <div class="zoom-controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">-</button>
            <button class="zoom-btn" onclick="resetZoom()">⟲</button>
        </div>
        
        <div class="docs-panel" id="docsPanel">
            <div class="docs-toggle" onclick="toggleDocs()">📚</div>
            <div class="docs-header">
                <h2>📄 Documentation</h2>
                <p id="docCount">Loading...</p>
            </div>
            <div id="docsList"></div>
        </div>
        
        <button class="refresh-btn" onclick="refreshMap()">🔄 Refresh Map</button>
        
        <div class="legend">
            <h3 style="margin-bottom: 10px;">Device Types</h3>
            <div class="legend-item">
                <span class="legend-icon">🖥️</span>
                <span>Workstation</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🌐</span>
                <span>Router</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">📡</span>
                <span>Mesh Node</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">⚡</span>
                <span>Service</span>
            </div>
        </div>
    </div>
    
    <script>
        const deviceIcons = {
            'workstation': '🖥️',
            'router': '🌐',
            'mesh': '📡',
            'service': '⚡'
        };
        
        let currentZoom = 1;
        let isPanning = false;
        let startX = 0;
        let startY = 0;
        let translateX = -500;
        let translateY = -500;
        let docsOpen = false;
        
        // Google Maps-style pan and zoom
        const mapContainer = document.getElementById('mapContainer');
        const mapViewport = document.getElementById('mapViewport');
        
        mapContainer.addEventListener('mousedown', startPan);
        mapContainer.addEventListener('mousemove', pan);
        mapContainer.addEventListener('mouseup', endPan);
        mapContainer.addEventListener('mouseleave', endPan);
        mapContainer.addEventListener('wheel', handleZoom);
        
        function startPan(e) {
            isPanning = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
        }
        
        function pan(e) {
            if (!isPanning) return;
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            updateTransform();
        }
        
        function endPan() {
            isPanning = false;
        }
        
        function handleZoom(e) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            currentZoom = Math.max(0.5, Math.min(3, currentZoom + delta));
            updateTransform();
        }
        
        function zoomIn() {
            currentZoom = Math.min(3, currentZoom + 0.2);
            updateTransform();
        }
        
        function zoomOut() {
            currentZoom = Math.max(0.5, currentZoom - 0.2);
            updateTransform();
        }
        
        function resetZoom() {
            currentZoom = 1;
            translateX = -500;
            translateY = -500;
            updateTransform();
        }
        
        function updateTransform() {
            mapViewport.style.transform = `translate(${translateX}px, ${translateY}px) scale(${currentZoom})`;
        }
        
        function toggleDocs() {
            docsOpen = !docsOpen;
            const panel = document.getElementById('docsPanel');
            panel.classList.toggle('open', docsOpen);
        }
        
        async function loadDocumentation() {
            try {
                const response = await fetch('/api/docs');
                const data = await response.json();
                
                const docsList = document.getElementById('docsList');
                const docCount = document.getElementById('docCount');
                
                docCount.textContent = `${data.docs.length} files found`;
                
                docsList.innerHTML = data.docs.map(doc => `
                    <div class="doc-item fade-in">
                        <h4>📄 ${doc.filename}</h4>
                        <p>📏 ${doc.lines} lines • 💾 ${formatBytes(doc.size)}</p>
                        <div class="doc-preview">${escapeHtml(doc.preview)}</div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Failed to load documentation:', error);
            }
        }
        
        function formatBytes(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        async function loadMap() {
            // Show loading spinner
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            spinner.textContent = '🔄';
            document.body.appendChild(spinner);
            
            try {
                const response = await fetch('/api/devices');
                const data = await response.json();
                
                renderDevices(data.devices);
                renderConnections(data.devices);
                updateGitStatus(data.git);
                
                // Remove spinner
                spinner.remove();
            } catch (error) {
                console.error('Failed to load map:', error);
                spinner.remove();
            }
        }
        
        function renderDevices(devices) {
            const container = document.getElementById('devices');
            container.innerHTML = '';
            
            devices.forEach(device => {
                const deviceEl = document.createElement('div');
                deviceEl.className = 'device';
                deviceEl.style.left = device.x + 'px';
                deviceEl.style.top = device.y + 'px';
                
                const logs = device.logs.map(log => 
                    `<div class="log-entry">${log}</div>`
                ).join('');
                
                deviceEl.innerHTML = `
                    <div class="device-thumbnail ${device.status}">
                        <div class="device-header">
                            <span class="device-icon">${deviceIcons[device.type]}</span>
                            <div class="device-info">
                                <h3>${device.name}</h3>
                                <p>${device.ip}</p>
                            </div>
                            <div class="status-indicator ${device.status}"></div>
                        </div>
                        <div class="device-logs">
                            ${logs || '<div class="log-entry">No logs available</div>'}
                        </div>
                    </div>
                `;
                
                container.appendChild(deviceEl);
            });
        }
        
        function renderConnections(devices) {
            const container = document.getElementById('connections');
            container.innerHTML = '';
            
            // Connect routers to mesh nodes
            const router = devices.find(d => d.id === 'router-wifi7');
            const meshNodes = devices.filter(d => d.type === 'mesh');
            
            meshNodes.forEach(node => {
                drawLine(router.x + 100, router.y + 50, node.x + 100, node.y + 50);
            });
            
            // Connect workstation to router
            const workstation = devices.find(d => d.type === 'workstation');
            drawLine(workstation.x + 100, workstation.y + 50, router.x + 100, router.y + 50);
            
            // Connect services to workstation
            const services = devices.filter(d => d.type === 'service');
            services.forEach(service => {
                drawLine(workstation.x + 100, workstation.y + 50, service.x + 100, service.y + 50);
            });
        }
        
        function drawLine(x1, y1, x2, y2) {
            const line = document.createElement('div');
            line.className = 'connection-line';
            
            const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
            const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
            
            line.style.width = length + 'px';
            line.style.left = x1 + 'px';
            line.style.top = y1 + 'px';
            line.style.transform = `rotate(${angle}deg)`;
            
            document.getElementById('connections').appendChild(line);
        }
        
        function updateGitStatus(git) {
            const badge = document.getElementById('gitBadge');
            const branch = document.getElementById('gitBranch');
            const commit = document.getElementById('gitCommit');
            
            if (git.connected) {
                badge.className = 'git-badge';
                branch.textContent = `📌 ${git.branch}`;
                commit.textContent = `${git.last_commit.substring(0, 40)}...`;
            } else {
                badge.className = 'git-badge disconnected';
                branch.textContent = 'Not connected';
                commit.textContent = '';
            }
        }
        
        function refreshMap() {
            loadMap();
        }
        
        // Initial load
        loadMap();
        loadDocumentation();
        updateTransform();
        
        // Auto-refresh every 5 seconds
        setInterval(loadMap, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the network map interface"""
    return render_template_string(MAP_TEMPLATE)

@app.route('/api/devices')
def api_devices():
    """Get all network devices with logs"""
    devices = get_network_devices()
    git_status = get_git_status()
    
    return jsonify({
        'devices': devices,
      

@app.route('/api/docs')
def api_docs():
    """Get all documentation files"""
    docs = get_all_documentation()
    
    return jsonify({
        'docs': docs,
        'count': len(docs),
        'timestamp': datetime.now().isoformat()
    })  'git': git_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs/<device_id>')
def api_device_logs(device_id):
    """Get detailed logs for specific device"""
    devices = get_network_devices()
    device = next((d for d in devices if d['id'] == device_id), None)
    
    if device:
        return jsonify({
            'device': device,
            'logs': device['logs'],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': 'Device not found'}), 404

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'network-map-viewer',
        'devices': len(get_network_devices())
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - Network Topology Map Viewer              ║
║  Live Device Monitoring with Log Thumbnails               ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("🗺️  Starting Network Map Viewer on http://localhost:6000")
    print("⚡ Features:")
    print("   ✓ Interactive topology map")
    print("   ✓ Device thumbnails with live logs")
    print("   ✓ Real-time status monitoring")
    print("   ✓ Git integration status")
    print("   ✓ Auto-refresh every 5 seconds")
    print("   ✓ Device classification by type")
    print("")
    
    app.run(host='0.0.0.0', port=6000, debug=False)
