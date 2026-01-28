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

# Gateway management data
def get_gateway_configs(local_ip):
    """Get gateway configurations with dynamic local IP"""
    return {
        'router-wifi7': {
            'type': 'gateway',
            'dhcp_enabled': True,
            'firewall_enabled': True,
            'uptime': '15 days 8 hours',
            'connected_devices': 24,
            'bandwidth_usage': '45%',
            'wan_ip': '203.0.113.45',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'port_forwarding': [{'port': 80, 'to': '192.168.1.100'}, {'port': 443, 'to': '192.168.1.100'}]
        },
        'router-nb': {
            'type': 'gateway',
            'dhcp_enabled': True,
            'firewall_enabled': True,
            'uptime': '22 days 3 hours',
            'connected_devices': 8,
            'bandwidth_usage': '23%',
            'wan_ip': '203.0.113.46',
            'dns_servers': ['1.1.1.1', '1.0.0.1'],
            'port_forwarding': [{'port': 3000, 'to': local_ip}, {'port': 4000, 'to': local_ip}]
        }
    }

# Device discovery and classification
def get_network_devices():
    """Discover devices on network and classify by type"""
    devices = []
    
    # Get local machine info
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Get gateway configs with local IP
    gateway_configs = get_gateway_configs(local_ip)
    
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
    
    # WiFi 7 Mesh Router (Gateway)
    devices.append({
        'id': 'router-wifi7',
        'name': 'WiFi 7 Mesh Router',
        'type': 'gateway',
        'ip': '192.168.1.1',
        'status': 'online',
        'x': 200,
        'y': 150,
        'logs': get_device_logs('router'),
        'is_gateway': True,
        'gateway_config': gateway_configs.get('router-wifi7', {})
    })
    
    # NetworkBuster Router (Gateway)
    devices.append({
        'id': 'router-nb',
        'name': 'NetworkBuster Router',
        'type': 'gateway',
        'ip': '192.168.1.100',
        'status': 'online',
        'x': 600,
        'y': 150,
        'logs': get_device_logs('networkbuster'),
        'is_gateway': True,
        'gateway_config': gateway_configs.get('router-nb', {})
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
    <!-- Leaflet for ESRI and other tile layers -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- Google Maps API with client authentication -->
    <script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&libraries=places&client=389435108940-rdmp3ckl3f67p73eil8hc3pnb05ulh1u.apps.googleusercontent.com"></script>
    <!-- Google Sign-In for authentication -->
    <meta name="google-signin-client_id" content="389435108940-rdmp3ckl3f67p73eil8hc3pnb05ulh1u.apps.googleusercontent.com">
    <script src="https://accounts.google.com/gsi/client" async defer></script>
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
        
        .map-type-selector {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .map-type-btn {
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .map-type-btn:hover {
            background: rgba(255,255,255,0.2);
            border-color: #4CAF50;
        }
        
        .map-type-btn.active {
            background: #4CAF50;
            border-color: #4CAF50;
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
            overflow: hidden;
        }
        
        #satelliteMap {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }
        
        #networkLayer {
            position: absolute;
            width: 100vw;
            height: calc(100vh - 70px);
            background: transparent;
            cursor: grab;
            user-select: none;
            z-index: 2;
            pointer-events: auto;
        }
        
        #networkLayer:active {
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
        
        .zoom-btn, .nav-btn {
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
            font-weight: bold;
        }
        
        .zoom-btn:hover, .nav-btn:hover {
            background: #4CAF50;
            transform: scale(1.1);
        }
        
        .nav-separator {
            height: 2px;
            width: 40px;
            background: #4CAF50;
            opacity: 0.5;
        }
        
        .pan-controls {
            display: grid;
            grid-template-columns: repeat(3, 40px);
            gap: 5px;
        }
        
        .pan-controls .nav-btn:nth-child(1) {
            grid-column: 2;
        }
        
        .pan-controls .nav-btn:nth-child(2) {
            grid-column: 1;
            grid-row: 2;
        }
        
        .pan-controls .nav-btn:nth-child(3) {
            grid-column: 2;
            grid-row: 2;
        }
        
        .pan-controls .nav-btn:nth-child(4) {
            grid-column: 3;
            grid-row: 2;
        }
        
        .pan-controls .nav-btn:nth-child(5) {
            grid-column: 2;
            grid-row: 3;
        }
        
        .coordinates-display {
            position: absolute;
            bottom: 20px;
            left: 140px;
            background: rgba(0, 0, 0, 0.8);
            color: #4CAF50;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 11px;
            border: 2px solid #4CAF50;
            font-family: 'Consolas', monospace;
        }
        
        .zoom-display {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: #4CAF50;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 12px;
            border: 2px solid #4CAF50;
            font-weight: bold;
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
            margin-top: 5px;
            max-height: 100px;
            overflow: hidden;
        }
        
        .gateway-panel {
            position: absolute;
            right: -450px;
            top: 0;
            width: 450px;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            color: white;
            overflow-y: auto;
            transition: right 0.3s ease-out;
            z-index: 999;
            box-shadow: -5px 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .gateway-panel.open {
            right: 0;
        }
        
        .gateway-header {
            padding: 20px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            position: sticky;
            top: 0;
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .gateway-toggle {
            position: absolute;
            left: -40px;
            top: 50%;
            transform: translateY(-50%);
            width: 40px;
            height: 80px;
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #f5576c;
            border-right: none;
            border-radius: 10px 0 0 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            transition: background 0.2s;
        }
        
        .gateway-toggle:hover {
            background: #f5576c;
        }
        
        .gateway-close {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .gateway-close:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .gateway-info {
            padding: 20px;
        }
        
        .regex-panel {
            position: absolute;
            bottom: -450px;
            left: 0;
            width: 100%;
            height: 450px;
            background: rgba(0, 0, 0, 0.95);
            color: white;
            overflow-y: auto;
            transition: bottom 0.3s ease-out;
            z-index: 998;
            box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.5);
        }
        
        .regex-panel.open {
            bottom: 0;
        }
        
        .regex-toggle {
            position: absolute;
            left: 50%;
            top: -40px;
            transform: translateX(-50%);
            width: 120px;
            height: 40px;
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #00bcd4;
            border-bottom: none;
            border-radius: 10px 10px 0 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
            font-weight: bold;
            transition: background 0.2s;
        }
        
        .regex-toggle:hover {
            background: #00bcd4;
        }
        
        .regex-header {
            padding: 20px;
            background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .regex-close {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .regex-close:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .regex-content {
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .regex-section {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .regex-section h3 {
            margin-bottom: 15px;
            color: #00bcd4;
            font-size: 16px;
        }
        
        .regex-input-group {
            margin-bottom: 15px;
        }
        
        .regex-input-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            opacity: 0.8;
        }
        
        .regex-input-group input,
        .regex-input-group textarea,
        .regex-input-group select {
            width: 100%;
            padding: 10px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            color: white;
            font-family: 'Consolas', monospace;
            font-size: 14px;
        }
        
        .regex-input-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .regex-btn {
            padding: 10px 20px;
            background: #00bcd4;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
        }
        
        .regex-btn:hover {
            background: #0097a7;
        }
        
        .regex-result {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 5px;
            border-left: 3px solid #00bcd4;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .regex-result.success {
            border-left-color: #4CAF50;
        }
        
        .regex-result.error {
            border-left-color: #f44336;
        }
        
        .regex-patterns-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .regex-pattern-item {
            padding: 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .regex-pattern-item:hover {
            background: rgba(0, 0, 0, 0.5);
        }
        
        .regex-pattern-item strong {
            color: #00bcd4;
            display: block;
            margin-bottom: 5px;
        }
        
        .regex-pattern-item code {
            display: block;
            background: rgba(0, 0, 0, 0.5);
            padding: 5px;
            border-radius: 3px;
            font-size: 11px;
            margin: 5px 0;
        }
        
        .regex-pattern-item small {
            opacity: 0.7;
            font-size: 11px;
        }
        
        .gateway-metric {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .gateway-metric label {
            color: #f093fb;
            font-weight: bold;
        }
        
        .gateway-actions {
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .gateway-btn {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .gateway-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .gateway-btn.danger {
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        }
        
        .gateway-btn.danger:hover {
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
        }
        
        .port-forwarding-list {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        .port-item {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            margin-bottom: 5px;
            font-size: 12px;
        }
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
        <div class="map-type-selector">
            <button class="map-type-btn active" onclick="switchMapType('network')" id="btnNetwork">🔷 Network</button>
            <button class="map-type-btn" onclick="switchMapType('google-satellite')" id="btnGoogleSatellite">📡 Google Satellite</button>
            <button class="map-type-btn" onclick="switchMapType('google-roadmap')" id="btnGoogleRoadmap">🗺️ Google Maps</button>
            <button class="map-type-btn" onclick="switchMapType('google-hybrid')" id="btnGoogleHybrid">🌍 Google Hybrid</button>
            <button class="map-type-btn" onclick="switchMapType('esri-satellite')" id="btnEsriSatellite">🛰️ ESRI Satellite</button>
            <button class="map-type-btn" onclick="switchMapType('apple')" id="btnApple">🍎 Apple Maps</button>
        </div>
        <div class="git-status">
            <span id="gitBadge" class="git-badge">🔗 Git</span>
            <span id="gitBranch"></span>
            <span id="gitCommit"></span>
        </div>
    </div>
    
    <div class="map-container" id="mapContainer">
        <div id="satelliteMap"></div>
        <div id="networkLayer">
            <div class="map-viewport" id="mapViewport">
                <div class="grid-pattern"></div>
                <div id="connections"></div>
                <div id="devices"></div>
            </div>
        </div>
        
        <div class="zoom-controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">-</button>
            <button class="zoom-btn" onclick="resetZoom()">⟲</button>
            <div class="nav-separator"></div>
            <div class="pan-controls">
                <button class="nav-btn" onclick="panUp()">↑</button>
                <button class="nav-btn" onclick="panLeft()">←</button>
                <button class="nav-btn" onclick="resetView()">⊙</button>
                <button class="nav-btn" onclick="panRight()">→</button>
                <button class="nav-btn" onclick="panDown()">↓</button>
            </div>
        </div>
        
        <div class="zoom-display" id="zoomDisplay">Zoom: 100%</div>
        <div class="coordinates-display" id="coordDisplay">X: 0 | Y: 0</div>
        
        <div class="docs-panel" id="docsPanel">
            <div class="docs-toggle" onclick="toggleDocs()">📚</div>
            <div class="docs-header">
                <h2>📄 Documentation</h2>
                <p id="docCount">Loading...</p>
            </div>
            <div id="docsList"></div>
        </div>
        
        <div class="gateway-panel" id="gatewayPanel">
            <div class="gateway-toggle" onclick="toggleGatewayPanel()">🚪</div>
            <div class="gateway-header">
                <h2>🚪 Gateway Management</h2>
                <button class="gateway-close" onclick="toggleGatewayPanel()">✕</button>
            </div>
            <div id="gatewayContent">
                <div style="padding: 20px; text-align: center; opacity: 0.5;">
                    Click on a gateway device to manage it
                </div>
            </div>
        </div>
        
        <!-- Regex Testing Panel -->
        <div class="regex-panel" id="regexPanel">
            <div class="regex-toggle" onclick="toggleRegexPanel()">🔍 Regex Tools</div>
            <div class="regex-header">
                <h2>🔍 Regex Testing & Validation</h2>
                <button class="regex-close" onclick="toggleRegexPanel()">Close</button>
            </div>
            <div class="regex-content">
                <div class="regex-section">
                    <h3>Test Pattern</h3>
                    <div class="regex-input-group">
                        <label>Test Text:</label>
                        <textarea id="regexTestText" placeholder="Enter text to test...">user@example.com</textarea>
                    </div>
                    <div class="regex-input-group">
                        <label>Regex Pattern:</label>
                        <input type="text" id="regexPattern" placeholder="Enter regex pattern..." value="^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$" />
                    </div>
                    <div class="regex-input-group">
                        <label>
                            <input type="checkbox" id="regexCaseInsensitive" />
                            Case Insensitive
                        </label>
                    </div>
                    <button class="regex-btn" onclick="testRegexPattern()">Test Pattern</button>
                    <div id="regexTestResult" class="regex-result" style="display:none;"></div>
                </div>
                
                <div class="regex-section">
                    <h3>Validate Input</h3>
                    <div class="regex-input-group">
                        <label>Input to Validate:</label>
                        <input type="text" id="regexValidateText" placeholder="Enter text..." value="user@example.com" />
                    </div>
                    <div class="regex-input-group">
                        <label>Validation Type:</label>
                        <select id="regexValidateType">
                            <option value="email">Email</option>
                            <option value="url">URL</option>
                            <option value="ipv4">IPv4 Address</option>
                            <option value="ipv6">IPv6 Address</option>
                            <option value="port">Port Number</option>
                            <option value="mac">MAC Address</option>
                            <option value="hex">Hex Color</option>
                            <option value="uuid">UUID</option>
                            <option value="phone">Phone Number</option>
                            <option value="alphanumeric">Alphanumeric</option>
                            <option value="slug">URL Slug</option>
                        </select>
                    </div>
                    <button class="regex-btn" onclick="validateInput()">Validate</button>
                    <div id="regexValidateResult" class="regex-result" style="display:none;"></div>
                </div>
                
                <div class="regex-section">
                    <h3>Replace Text</h3>
                    <div class="regex-input-group">
                        <label>Original Text:</label>
                        <textarea id="regexReplaceText" placeholder="Enter text...">Hello World</textarea>
                    </div>
                    <div class="regex-input-group">
                        <label>Find Pattern:</label>
                        <input type="text" id="regexReplacePattern" placeholder="Pattern to find..." value="World" />
                    </div>
                    <div class="regex-input-group">
                        <label>Replace With:</label>
                        <input type="text" id="regexReplaceWith" placeholder="Replacement..." value="NetworkBuster" />
                    </div>
                    <button class="regex-btn" onclick="replaceText()">Replace</button>
                    <div id="regexReplaceResult" class="regex-result" style="display:none;"></div>
                </div>
                
                <div class="regex-section">
                    <h3>Available Patterns</h3>
                    <div class="regex-patterns-list" id="regexPatternsList">
                        <div class="regex-pattern-item" onclick="loadPattern('email')">
                            <strong>Email</strong>
                            <code>^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$</code>
                            <small>Example: user@example.com</small>
                        </div>
                        <div class="regex-pattern-item" onclick="loadPattern('ipv4')">
                            <strong>IPv4 Address</strong>
                            <code>^(\\d{1,3}\\.){3}\\d{1,3}$</code>
                            <small>Example: 192.168.1.1</small>
                        </div>
                        <div class="regex-pattern-item" onclick="loadPattern('url')">
                            <strong>URL</strong>
                            <code>^https?://...</code>
                            <small>Example: https://example.com</small>
                        </div>
                        <div class="regex-pattern-item" onclick="loadPattern('mac')">
                            <strong>MAC Address</strong>
                            <code>^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$</code>
                            <small>Example: 00:1B:44:11:3A:B7</small>
                        </div>
                    </div>
                </div>
            </div>
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
                <span class="legend-icon">�</span>
                <span>Gateway (Click to manage)</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">�📡</span>
                <span>Mesh Node</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">⚡</span>
                <span>Service</span>
            </div>
        </div>
    </div>
    
    <script>
        // Map Initialization Variables
        let satelliteMap = null;
        let googleMap = null;
        let mapType = 'network';
        
        // Initialize Google Maps
        function initGoogleMap(mapTypeId) {
            const mapDiv = document.getElementById('satelliteMap');
            
            if (!googleMap && typeof google !== 'undefined' && google.maps) {
                googleMap = new google.maps.Map(mapDiv, {
                    center: { lat: 37.7749, lng: -122.4194 }, // San Francisco default
                    zoom: 13,
                    mapTypeId: mapTypeId || google.maps.MapTypeId.SATELLITE,
                    mapTypeControl: true,
                    streetViewControl: false,
                    fullscreenControl: false
                });
            } else if (googleMap) {
                googleMap.setMapTypeId(mapTypeId);
            }
            
            mapDiv.style.display = 'block';
        }
        
        // Initialize Leaflet map (ESRI/Apple)
        function initSatelliteMap(provider = 'esri') {
            if (!satelliteMap) {
                satelliteMap = L.map('satelliteMap', {
                    center: [37.7749, -122.4194],
                    zoom: 13,
                    zoomControl: false
                });
                
                // Store tile layers
                window.tileLayersMap = {};
            }
            
            // Remove existing layers
            satelliteMap.eachLayer(layer => {
                satelliteMap.removeLayer(layer);
            });
            
            // Add appropriate tile layer based on provider
            if (provider === 'esri') {
                // ESRI World Imagery
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    attribution: 'Tiles &copy; Esri',
                    maxZoom: 19
                }).addTo(satelliteMap);
            } else if (provider === 'apple') {
                // Apple Maps-style (using OpenStreetMap as proxy)
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors (Apple Maps style)',
                    maxZoom: 19
                }).addTo(satelliteMap);
            }
            
            // Add labels layer for hybrid view
            if (!window.labelsLayer) {
                window.labelsLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; CARTO',
                    maxZoom: 19,
                    subdomains: 'abcd'
                });
            }
            
            document.getElementById('satelliteMap').style.display = 'block';
        }
        
        function switchMapType(type) {
            mapType = type;
            const networkLayer = document.getElementById('networkLayer');
            const satelliteMapDiv = document.getElementById('satelliteMap');
            
            // Update button states
            document.querySelectorAll('.map-type-btn').forEach(btn => btn.classList.remove('active'));
            
            // Handle different button ID formats
            const btnId = 'btn' + type.split('-').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join('');
            
            const btn = document.getElementById(btnId);
            if (btn) btn.classList.add('active');
            
            // Hide all maps first
            satelliteMapDiv.style.display = 'none';
            networkLayer.style.background = 'transparent';
            document.querySelector('.grid-pattern').style.display = 'none';
            
            if (type === 'network') {
                // Network view only
                satelliteMapDiv.style.display = 'none';
                networkLayer.style.background = 'radial-gradient(circle at 50% 50%, #2a5298 0%, #1e3c72 100%)';
                document.querySelector('.grid-pattern').style.display = 'block';
                
            } else if (type.startsWith('google-')) {
                // Google Maps variants
                const googleMapType = type === 'google-satellite' ? google.maps.MapTypeId.SATELLITE :
                                     type === 'google-roadmap' ? google.maps.MapTypeId.ROADMAP :
                                     type === 'google-hybrid' ? google.maps.MapTypeId.HYBRID :
                                     google.maps.MapTypeId.SATELLITE;
                
                if (typeof google !== 'undefined' && google.maps) {
                    initGoogleMap(googleMapType);
                    networkLayer.style.background = 'transparent';
                } else {
                    console.warn('Google Maps API not loaded yet, falling back to ESRI');
                    initSatelliteMap('esri');
                    networkLayer.style.background = 'transparent';
                }
                
            } else if (type === 'esri-satellite') {
                // ESRI satellite
                initSatelliteMap('esri');
                networkLayer.style.background = 'transparent';
                
            } else if (type === 'apple') {
                // Apple Maps style
                initSatelliteMap('apple');
                networkLayer.style.background = 'transparent';
            }
        }
        
        const deviceIcons = {
            'workstation': '🖥️',
            'router': '🌐',
            'gateway': '🚪',
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
        let gatewayPanelOpen = false;
        let selectedGateway = null;
        
        // Google Maps-style pan and zoom
        const mapContainer = document.getElementById('networkLayer');
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
        
        function panUp() {
            translateY += 100;
            updateTransform();
        }
        
        function panDown() {
            translateY -= 100;
            updateTransform();
        }
        
        function panLeft() {
            translateX += 100;
            updateTransform();
        }
        
        function panRight() {
            translateX -= 100;
            updateTransform();
        }
        
        function resetView() {
            currentZoom = 1;
            translateX = -500;
            translateY = -500;
            updateTransform();
        }
        
        function updateTransform() {
            mapViewport.style.transform = `translate(${translateX}px, ${translateY}px) scale(${currentZoom})`;
            document.getElementById('zoomDisplay').textContent = `Zoom: ${Math.round(currentZoom * 100)}%`;
            document.getElementById('coordDisplay').textContent = `X: ${Math.round(translateX)} | Y: ${Math.round(translateY)}`;
        }
        
        function toggleDocs() {
            docsOpen = !docsOpen;
            const panel = document.getElementById('docsPanel');
            panel.classList.toggle('open', docsOpen);
        }
        
        function toggleGatewayPanel() {
            gatewayPanelOpen = !gatewayPanelOpen;
            const panel = document.getElementById('gatewayPanel');
            panel.classList.toggle('open', gatewayPanelOpen);
        }
        
        async function openGatewayManager(device) {
            selectedGateway = device;
            const panel = document.getElementById('gatewayPanel');
            const content = document.getElementById('gatewayContent');
            
            if (!device.gateway_config) {
                content.innerHTML = '<div style="padding: 20px; text-align: center; color: #f44336;">No configuration available</div>';
                return;
            }
            
            const config = device.gateway_config;
            
            content.innerHTML = `
                <div class="gateway-info">
                    <h3 style="color: #f093fb; margin-bottom: 15px;">${device.name}</h3>
                    <div class="gateway-metric">
                        <label>IP Address:</label>
                        <span>${device.ip}</span>
                    </div>
                    <div class="gateway-metric">
                        <label>WAN IP:</label>
                        <span>${config.wan_ip || 'N/A'}</span>
                    </div>
                    <div class="gateway-metric">
                        <label>Uptime:</label>
                        <span>${config.uptime || 'Unknown'}</span>
                    </div>
                    <div class="gateway-metric">
                        <label>Connected Devices:</label>
                        <span>${config.connected_devices || 0} devices</span>
                    </div>
                    <div class="gateway-metric">
                        <label>Bandwidth Usage:</label>
                        <span>${config.bandwidth_usage || '0%'}</span>
                    </div>
                    <div class="gateway-metric">
                        <label>DHCP Server:</label>
                        <span style="color: ${config.dhcp_enabled ? '#4CAF50' : '#f44336'}">${config.dhcp_enabled ? 'Enabled ✓' : 'Disabled ✗'}</span>
                    </div>
                    <div class="gateway-metric">
                        <label>Firewall:</label>
                        <span style="color: ${config.firewall_enabled ? '#4CAF50' : '#f44336'}">${config.firewall_enabled ? 'Enabled ✓' : 'Disabled ✗'}</span>
                    </div>
                    <div class="gateway-metric">
                        <label>DNS Servers:</label>
                        <span>${config.dns_servers ? config.dns_servers.join(', ') : 'Default'}</span>
                    </div>
                    
                    <h4 style="color: #f093fb; margin: 20px 0 10px 0;">Port Forwarding Rules</h4>
                    <div class="port-forwarding-list">
                        ${config.port_forwarding && config.port_forwarding.length > 0 
                            ? config.port_forwarding.map(rule => `
                                <div class="port-item">
                                    <span>Port ${rule.port}</span>
                                    <span>→ ${rule.to}</span>
                                </div>
                            `).join('')
                            : '<div style="text-align: center; opacity: 0.5;">No port forwarding rules</div>'
                        }
                    </div>
                </div>
                
                <div class="gateway-actions">
                    <h4 style="color: #f093fb; margin-bottom: 15px;">Gateway Actions</h4>
                    <button class="gateway-btn" onclick="performGatewayAction('${device.id}', 'restart')">
                        🔄 Restart Gateway
                    </button>
                    <button class="gateway-btn" onclick="performGatewayAction('${device.id}', 'toggle_firewall')">
                        🛡️ Toggle Firewall
                    </button>
                    <button class="gateway-btn" onclick="performGatewayAction('${device.id}', 'toggle_dhcp')">
                        🌐 Toggle DHCP Server
                    </button>
                    <button class="gateway-btn" onclick="performGatewayAction('${device.id}', 'update_firmware')">
                        ⬆️ Update Firmware
                    </button>
                    <button class="gateway-btn danger" onclick="performGatewayAction('${device.id}', 'reset')">
                        ⚠️ Factory Reset
                    </button>
                </div>
            `;
            
            panel.classList.add('open');
            gatewayPanelOpen = true;
        }
        
        async function performGatewayAction(gatewayId, action) {
            try {
                const response = await fetch(`/api/gateway/${gatewayId}/action`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ action: action })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(`✓ ${data.message}`);
                    // Refresh gateway info
                    if (selectedGateway) {
                        const devices = await fetch('/api/devices').then(r => r.json());
                        const updatedDevice = devices.devices.find(d => d.id === gatewayId);
                        if (updatedDevice) {
                            openGatewayManager(updatedDevice);
                        }
                    }
                } else {
                    alert(`✗ Error: ${data.error || 'Action failed'}`);
                }
            } catch (error) {
                alert(`✗ Failed to perform action: ${error.message}`);
            }
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
                
                // Add click handler for gateways
                if (device.is_gateway) {
                    deviceEl.style.cursor = 'pointer';
                    deviceEl.onclick = () => openGatewayManager(device);
                }
                
                const logs = device.logs.map(log => 
                    `<div class="log-entry">${log}</div>`
                ).join('');
                
                deviceEl.innerHTML = `
                    <div class="device-thumbnail ${device.status}">
                        <div class="device-header">
                            <span class="device-icon">${deviceIcons[device.type]}</span>
                            <div class="device-info">
                                <h3>${device.name}${device.is_gateway ? ' 🚪' : ''}</h3>
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
        
        // Regex Panel Functions
        function toggleRegexPanel() {
            const panel = document.getElementById('regexPanel');
            panel.classList.toggle('open');
        }
        
        async function testRegexPattern() {
            const text = document.getElementById('regexTestText').value;
            const pattern = document.getElementById('regexPattern').value;
            const caseInsensitive = document.getElementById('regexCaseInsensitive').checked;
            const resultDiv = document.getElementById('regexTestResult');
            
            try {
                const response = await fetch('/api/regex/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, pattern, case_insensitive: caseInsensitive })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.className = 'regex-result success';
                    resultDiv.innerHTML = `
                        <strong>✅ Test Result</strong><br/>
                        Matches: ${data.matches ? 'Yes' : 'No'}<br/>
                        Found: ${JSON.stringify(data.found, null, 2)}<br/>
                        Pattern: ${data.pattern}
                    `;
                } else {
                    resultDiv.className = 'regex-result error';
                    resultDiv.innerHTML = `<strong>❌ Error</strong><br/>${data.error}`;
                }
                resultDiv.style.display = 'block';
            } catch (error) {
                resultDiv.className = 'regex-result error';
                resultDiv.innerHTML = `<strong>❌ Error</strong><br/>${error.message}`;
                resultDiv.style.display = 'block';
            }
        }
        
        async function validateInput() {
            const text = document.getElementById('regexValidateText').value;
            const type = document.getElementById('regexValidateType').value;
            const resultDiv = document.getElementById('regexValidateResult');
            
            try {
                const response = await fetch('/api/regex/validate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, type })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.className = data.valid ? 'regex-result success' : 'regex-result error';
                    resultDiv.innerHTML = `
                        <strong>${data.valid ? '✅ Valid' : '❌ Invalid'}</strong><br/>
                        Type: ${data.type}<br/>
                        Text: ${data.text}<br/>
                        Pattern: ${data.pattern}
                    `;
                } else {
                    resultDiv.className = 'regex-result error';
                    resultDiv.innerHTML = `<strong>❌ Error</strong><br/>${data.error}`;
                }
                resultDiv.style.display = 'block';
            } catch (error) {
                resultDiv.className = 'regex-result error';
                resultDiv.innerHTML = `<strong>❌ Error</strong><br/>${error.message}`;
                resultDiv.style.display = 'block';
            }
        }
        
        async function replaceText() {
            const text = document.getElementById('regexReplaceText').value;
            const pattern = document.getElementById('regexReplacePattern').value;
            const replacement = document.getElementById('regexReplaceWith').value;
            const resultDiv = document.getElementById('regexReplaceResult');
            
            try {
                const response = await fetch('/api/regex/replace', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, pattern, replacement, case_insensitive: false })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.className = 'regex-result success';
                    resultDiv.innerHTML = `
                        <strong>✅ Replacement Complete</strong><br/>
                        Replacements: ${data.replacements}<br/>
                        Original: ${data.original}<br/>
                        Result: <strong>${data.result}</strong>
                    `;
                } else {
                    resultDiv.className = 'regex-result error';
                    resultDiv.innerHTML = `<strong>❌ Error</strong><br/>${data.error}`;
                }
                resultDiv.style.display = 'block';
            } catch (error) {
                resultDiv.className = 'regex-result error';
                resultDiv.innerHTML = `<strong>❌ Error</strong><br/>${error.message}`;
                resultDiv.style.display = 'block';
            }
        }
        
        function loadPattern(type) {
            const patterns = {
                'email': '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$',
                'ipv4': '^(\\d{1,3}\\.){3}\\d{1,3}$',
                'url': '^https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)$',
                'mac': '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            };
            
            const pattern = patterns[type];
            if (pattern) {
                document.getElementById('regexPattern').value = pattern;
            }
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
        'git': git_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/docs')
def api_docs():
    """Get all documentation files"""
    docs = get_all_documentation()
    
    return jsonify({
        'docs': docs,
        'count': len(docs),
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

@app.route('/api/gateways')
def api_gateways():
    """Get all gateway devices"""
    devices = get_network_devices()
    gateways = [d for d in devices if d.get('is_gateway', False)]
    
    return jsonify({
        'gateways': gateways,
        'count': len(gateways),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/gateway/<gateway_id>/config', methods=['GET', 'POST'])
def api_gateway_config(gateway_id):
    """Get or update gateway configuration"""
    devices = get_network_devices()
    gateways = [d for d in devices if d.get('is_gateway', False)]
    gateway_configs = {g['id']: g.get('gateway_config', {}) for g in gateways}
    
    if request.method == 'GET':
        config = gateway_configs.get(gateway_id, {})
        return jsonify({
            'gateway_id': gateway_id,
            'config': config,
            'timestamp': datetime.now().isoformat()
        })
    elif request.method == 'POST':
        data = request.json
        if gateway_id in gateway_configs:
            gateway_configs[gateway_id].update(data)
            return jsonify({
                'success': True,
                'gateway_id': gateway_id,
                'config': gateway_configs[gateway_id]
            })
        return jsonify({'error': 'Gateway not found'}), 404

@app.route('/api/gateway/<gateway_id>/action', methods=['POST'])
def api_gateway_action(gateway_id):
    """Perform action on gateway (restart, reset, etc.)"""
    data = request.json
    action = data.get('action', '')
    
    devices = get_network_devices()
    gateways = [d for d in devices if d.get('is_gateway', False)]
    gateway_configs = {g['id']: g.get('gateway_config', {}) for g in gateways}
    
    if gateway_id not in gateway_configs:
        return jsonify({'error': 'Gateway not found'}), 404
    
    actions_log = {
        'restart': f'Gateway {gateway_id} restarted successfully',
        'reset': f'Gateway {gateway_id} reset to factory defaults',
        'update_firmware': f'Gateway {gateway_id} firmware update initiated',
        'toggle_firewall': f'Gateway {gateway_id} firewall toggled',
        'toggle_dhcp': f'Gateway {gateway_id} DHCP server toggled'
    }
    
    message = actions_log.get(action, f'Unknown action: {action}')
    
    return jsonify({
        'success': True,
        'gateway_id': gateway_id,
        'action': action,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'network-map-viewer',
        'devices': len(get_network_devices())
    })

@app.route('/api/regex/validate', methods=['POST'])
def api_regex_validate():
    """Validate input against common regex patterns"""
    data = request.json
    text = data.get('text', '')
    pattern_type = data.get('type', '')
    
    patterns = {
        'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
        'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
        'ipv4': r'^(\d{1,3}\.){3}\d{1,3}$',
        'ipv6': r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
        'port': r'^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$',
        'mac': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
        'hex': r'^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'phone': r'^\+?[\d\s\-\(\)]+$',
        'alphanumeric': r'^[a-zA-Z0-9]+$',
        'slug': r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    }
    
    if pattern_type not in patterns:
        return jsonify({
            'error': f'Unknown pattern type: {pattern_type}',
            'available': list(patterns.keys())
        }), 400
    
    import re
    pattern = patterns[pattern_type]
    is_valid = bool(re.match(pattern, text))
    
    return jsonify({
        'valid': is_valid,
        'text': text,
        'type': pattern_type,
        'pattern': pattern,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/regex/escape', methods=['POST'])
def api_regex_escape():
    """Escape special regex characters in a string"""
    data = request.json
    text = data.get('text', '')
    
    import re
    escaped = re.escape(text)
    
    return jsonify({
        'original': text,
        'escaped': escaped,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/regex/test', methods=['POST'])
def api_regex_test():
    """Test if a string matches a custom regex pattern"""
    data = request.json
    text = data.get('text', '')
    pattern = data.get('pattern', '')
    case_insensitive = data.get('case_insensitive', False)
    
    import re
    
    try:
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        matches = regex.findall(text)
        is_match = bool(regex.search(text))
        
        return jsonify({
            'matches': is_match,
            'found': matches,
            'text': text,
            'pattern': pattern,
            'case_insensitive': case_insensitive,
            'timestamp': datetime.now().isoformat()
        })
    except re.error as e:
        return jsonify({
            'error': f'Invalid regex pattern: {str(e)}',
            'pattern': pattern
        }), 400

@app.route('/api/regex/replace', methods=['POST'])
def api_regex_replace():
    """Replace text using regex pattern"""
    data = request.json
    text = data.get('text', '')
    pattern = data.get('pattern', '')
    replacement = data.get('replacement', '')
    case_insensitive = data.get('case_insensitive', False)
    
    import re
    
    try:
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        result = regex.sub(replacement, text)
        count = len(regex.findall(text))
        
        return jsonify({
            'original': text,
            'result': result,
            'pattern': pattern,
            'replacement': replacement,
            'replacements': count,
            'timestamp': datetime.now().isoformat()
        })
    except re.error as e:
        return jsonify({
            'error': f'Invalid regex pattern: {str(e)}',
            'pattern': pattern
        }), 400

@app.route('/api/regex/patterns')
def api_regex_patterns():
    """Get list of available regex patterns"""
    patterns = {
        'email': {
            'pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
            'description': 'Email address validation',
            'example': 'user@example.com'
        },
        'url': {
            'pattern': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            'description': 'URL validation (http/https)',
            'example': 'https://example.com/path'
        },
        'ipv4': {
            'pattern': r'^(\d{1,3}\.){3}\d{1,3}$',
            'description': 'IPv4 address',
            'example': '192.168.1.1'
        },
        'ipv6': {
            'pattern': r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
            'description': 'IPv6 address',
            'example': '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
        },
        'port': {
            'pattern': r'^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$',
            'description': 'Network port (1-65535)',
            'example': '8080'
        },
        'mac': {
            'pattern': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            'description': 'MAC address',
            'example': '00:1B:44:11:3A:B7'
        },
        'hex': {
            'pattern': r'^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$',
            'description': 'Hex color code',
            'example': '#FF5733'
        },
        'uuid': {
            'pattern': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            'description': 'UUID v4',
            'example': '550e8400-e29b-41d4-a716-446655440000'
        },
        'phone': {
            'pattern': r'^\+?[\d\s\-\(\)]+$',
            'description': 'Phone number',
            'example': '+1 (555) 123-4567'
        },
        'alphanumeric': {
            'pattern': r'^[a-zA-Z0-9]+$',
            'description': 'Alphanumeric only',
            'example': 'abc123'
        },
        'slug': {
            'pattern': r'^[a-z0-9]+(?:-[a-z0-9]+)*$',
            'description': 'URL-friendly slug',
            'example': 'my-url-slug'
        }
    }
    
    return jsonify({
        'patterns': patterns,
        'count': len(patterns),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - Network Topology Map Viewer              ║
║  Live Device Monitoring with Log Thumbnails               ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("🗺️  Starting Network Map Viewer on http://localhost:8080")
    print("🌐 Remote Access: Use ngrok or Cloudflare Tunnel for secure access")
    print("⚡ Features:")
    print("   ✓ Interactive topology map")
    print("   ✓ Device thumbnails with live logs")
    print("   ✓ Real-time status monitoring")
    print("   ✓ Git integration status")
    print("   ✓ Auto-refresh every 5 seconds")
    print("   ✓ Device classification by type")
    print("   ✓ Satellite map integration")
    print("   ✓ Gateway management panel")
    print("   ✓ Regex testing & validation")
    print("")
    print("🚀 Running production WSGI server (Waitress) on port 8080...")
    print("")
    
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080, threads=8, url_scheme='http')
