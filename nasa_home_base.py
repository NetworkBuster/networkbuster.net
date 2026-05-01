#!/usr/bin/env python3
"""
NASA Home Base Mission Control
NetworkBuster Integration Package
"""

import sys
import time
import json
import requests
import subprocess
import webbrowser
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Check for required packages
try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available. Install with: pip install flask")

class NASAHomeBase:
    """NASA Home Base Mission Control System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ports = {
            'web': {'port': 3000, 'name': 'Web Server', 'status': 'offline'},
            'api': {'port': 3001, 'name': 'API Server', 'status': 'offline'},
            'audio': {'port': 3002, 'name': 'Audio Stream', 'status': 'offline'}
        }
        self.mission_start_time = datetime.now()
        self.mission_log = []
        
    def log_event(self, event, level='INFO'):
        """Log mission event"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {event}"
        self.mission_log.append(log_entry)
        print(f"  {log_entry}")
        
    def check_port_status(self, port):
        """Check if a port is active"""
        try:
            response = requests.get(f'http://localhost:{port}/api/health', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def check_all_ports(self):
        """Check status of all NetworkBuster ports"""
        for service, info in self.ports.items():
            is_active = self.check_port_status(info['port'])
            info['status'] = 'online' if is_active else 'offline'
            
    def start_service(self, service_name):
        """Start a NetworkBuster service"""
        self.log_event(f"Starting {service_name}...", 'COMMAND')
        # Services should already be running via start-servers.js
        
    def open_dashboard(self, service='web'):
        """Open service dashboard in browser"""
        port = self.ports[service]['port']
        url = f'http://localhost:{port}'
        self.log_event(f"Opening {service} dashboard: {url}", 'ACTION')
        webbrowser.open(url)
        
    def get_system_status(self):
        """Get comprehensive system status"""
        self.check_all_ports()
        
        online_count = sum(1 for p in self.ports.values() if p['status'] == 'online')
        uptime = (datetime.now() - self.mission_start_time).total_seconds()
        
        return {
            'mission_time': uptime,
            'ports': self.ports,
            'online_services': online_count,
            'total_services': len(self.ports),
            'status': 'NOMINAL' if online_count == len(self.ports) else 'DEGRADED'
        }

# Flask web interface for Mission Control
if FLASK_AVAILABLE:
    app = Flask(__name__)
    home_base = NASAHomeBase()
    
    MISSION_CONTROL_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NASA Home Base - Mission Control</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Courier New', monospace;
                background: #000;
                color: #0f0;
                overflow: hidden;
            }
            
            .container {
                height: 100vh;
                display: flex;
                flex-direction: column;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(90deg, #001a33, #003366, #001a33);
                border: 2px solid #0f0;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
            }
            
            .header h1 {
                font-size: 2.5em;
                color: #00ff00;
                text-shadow: 0 0 10px #0f0, 0 0 20px #0f0;
                letter-spacing: 5px;
            }
            
            .header .subtitle {
                color: #00aaff;
                font-size: 1.2em;
                margin-top: 10px;
                letter-spacing: 2px;
            }
            
            .main-grid {
                display: grid;
                grid-template-columns: 1fr 2fr 1fr;
                gap: 20px;
                flex: 1;
            }
            
            .panel {
                background: rgba(0, 26, 51, 0.9);
                border: 2px solid #0f0;
                border-radius: 10px;
                padding: 20px;
                overflow-y: auto;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
            }
            
            .panel-title {
                font-size: 1.3em;
                color: #00ff00;
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #0f0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            
            .service-item {
                background: rgba(0, 51, 102, 0.5);
                border-left: 4px solid #00aaff;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
                transition: all 0.3s;
            }
            
            .service-item:hover {
                background: rgba(0, 51, 102, 0.8);
                border-left-color: #00ff00;
                transform: translateX(5px);
            }
            
            .service-item.online {
                border-left-color: #00ff00;
            }
            
            .service-item.offline {
                border-left-color: #ff4444;
            }
            
            .service-name {
                font-size: 1.2em;
                font-weight: bold;
                color: #00ffff;
                margin-bottom: 8px;
            }
            
            .service-port {
                color: #00aaff;
                font-size: 0.9em;
            }
            
            .service-status {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 0.85em;
                font-weight: bold;
                margin-top: 8px;
            }
            
            .service-status.online {
                background: rgba(0, 255, 0, 0.2);
                color: #00ff00;
                border: 1px solid #00ff00;
            }
            
            .service-status.offline {
                background: rgba(255, 68, 68, 0.2);
                color: #ff4444;
                border: 1px solid #ff4444;
            }
            
            .btn {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                background: #003366;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                font-weight: bold;
                transition: all 0.3s;
                font-family: 'Courier New', monospace;
            }
            
            .btn:hover {
                background: #00ff00;
                color: #000;
                box-shadow: 0 0 15px #0f0;
            }
            
            .mission-stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .stat-box {
                background: rgba(0, 51, 102, 0.5);
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                border: 1px solid #00aaff;
            }
            
            .stat-label {
                color: #00aaff;
                font-size: 0.85em;
                margin-bottom: 5px;
                text-transform: uppercase;
            }
            
            .stat-value {
                color: #00ff00;
                font-size: 1.8em;
                font-weight: bold;
                text-shadow: 0 0 5px #0f0;
            }
            
            .log-container {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid #00aaff;
                border-radius: 5px;
                padding: 15px;
                max-height: 300px;
                overflow-y: auto;
                font-size: 0.9em;
            }
            
            .log-entry {
                color: #00ff00;
                margin-bottom: 5px;
                padding: 5px;
                border-left: 2px solid #00aaff;
                padding-left: 10px;
            }
            
            .status-indicator {
                display: inline-block;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                margin-right: 10px;
                animation: pulse 2s infinite;
            }
            
            .status-indicator.online {
                background: #00ff00;
                box-shadow: 0 0 10px #0f0;
            }
            
            .status-indicator.offline {
                background: #ff4444;
                animation: none;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .mission-status {
                text-align: center;
                padding: 15px;
                background: rgba(0, 51, 102, 0.5);
                border: 2px solid #00ff00;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            
            .mission-status.nominal {
                border-color: #00ff00;
            }
            
            .mission-status.degraded {
                border-color: #ffaa00;
            }
            
            .mission-status-text {
                font-size: 1.5em;
                font-weight: bold;
                color: #00ff00;
                text-shadow: 0 0 10px #0f0;
            }
            
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(0, 255, 0, 0.1);
            }
            
            ::-webkit-scrollbar-thumb {
                background: #00ff00;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 NASA HOME BASE</h1>
                <div class="subtitle">NETWORKBUSTER MISSION CONTROL</div>
            </div>
            
            <div class="main-grid">
                <!-- Left Panel: Services -->
                <div class="panel">
                    <div class="panel-title">🛰️ Services</div>
                    <div id="servicesList"></div>
                </div>
                
                <!-- Center Panel: Mission Control -->
                <div class="panel">
                    <div class="panel-title">📡 Mission Control</div>
                    
                    <div id="missionStatus" class="mission-status nominal">
                        <div class="mission-status-text">MISSION STATUS: <span id="statusText">NOMINAL</span></div>
                    </div>
                    
                    <div class="mission-stats">
                        <div class="stat-box">
                            <div class="stat-label">Mission Time</div>
                            <div class="stat-value" id="missionTime">0:00:00</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Services Online</div>
                            <div class="stat-value" id="servicesOnline">0/3</div>
                        </div>
                    </div>
                    
                    <div class="panel-title" style="margin-top: 20px;">🎮 Quick Actions</div>
                    <button class="btn" onclick="openAllDashboards()">🚀 Launch All Dashboards</button>
                    <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                    <button class="btn" onclick="openMasterControl()">🎛️ Master Control Panel</button>
                    <button class="btn" onclick="openWiFiMesh()">📡 WiFi 7 Mesh Overlay</button>
                </div>
                
                <!-- Right Panel: Mission Log -->
                <div class="panel">
                    <div class="panel-title">📝 Mission Log</div>
                    <div class="log-container" id="missionLog"></div>
                </div>
            </div>
        </div>
        
        <script>
            let missionStartTime = Date.now();
            
            function updateMissionTime() {
                const elapsed = Math.floor((Date.now() - missionStartTime) / 1000);
                const hours = Math.floor(elapsed / 3600);
                const minutes = Math.floor((elapsed % 3600) / 60);
                const seconds = elapsed % 60;
                document.getElementById('missionTime').textContent = 
                    `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
            
            async function refreshStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    // Update services list
                    const servicesList = document.getElementById('servicesList');
                    servicesList.innerHTML = Object.entries(data.ports).map(([key, service]) => `
                        <div class="service-item ${service.status}">
                            <div class="service-name">
                                <span class="status-indicator ${service.status}"></span>
                                ${service.name}
                            </div>
                            <div class="service-port">Port: ${service.port}</div>
                            <div class="service-status ${service.status}">${service.status.toUpperCase()}</div>
                            <button class="btn" onclick="openService('${key}', ${service.port})">Open Dashboard</button>
                        </div>
                    `).join('');
                    
                    // Update stats
                    document.getElementById('servicesOnline').textContent = 
                        `${data.online_services}/${data.total_services}`;
                    
                    document.getElementById('statusText').textContent = data.status;
                    document.getElementById('missionStatus').className = 
                        `mission-status ${data.status.toLowerCase()}`;
                    
                    addLog(`Status updated: ${data.online_services}/${data.total_services} services online`);
                } catch (error) {
                    addLog('Error updating status: ' + error.message, 'ERROR');
                }
            }
            
            function addLog(message, level = 'INFO') {
                const logContainer = document.getElementById('missionLog');
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.textContent = `[${timestamp}] ${level}: ${message}`;
                logContainer.insertBefore(logEntry, logContainer.firstChild);
                
                // Keep only last 50 entries
                while (logContainer.children.length > 50) {
                    logContainer.removeChild(logContainer.lastChild);
                }
            }
            
            function openService(service, port) {
                window.open(`http://localhost:${port}`, '_blank');
                addLog(`Opened ${service} dashboard`);
            }
            
            function openAllDashboards() {
                window.open('http://localhost:3000', '_blank');
                window.open('http://localhost:3001/api/specs', '_blank');
                window.open('http://localhost:3002/audio-lab', '_blank');
                addLog('All dashboards launched');
            }
            
            function openMasterControl() {
                window.open('http://localhost:3000/dashboard-control.html', '_blank');
                addLog('Master control panel opened');
            }
            
            function openWiFiMesh() {
                window.open('http://localhost:3000/wifi7-mesh-overlay.html', '_blank');
                addLog('WiFi 7 mesh overlay opened');
            }
            
            // Initialize
            refreshStatus();
            setInterval(updateMissionTime, 1000);
            setInterval(refreshStatus, 5000);
            addLog('NASA Home Base Mission Control initialized');
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(MISSION_CONTROL_HTML)
    
    @app.route('/api/status')
    def api_status():
        return jsonify(home_base.get_system_status())
    
    @app.route('/api/open/<service>')
    def api_open_service(service):
        if service in home_base.ports:
            home_base.open_dashboard(service)
            return jsonify({'success': True, 'message': f'Opened {service} dashboard'})
        return jsonify({'success': False, 'message': 'Service not found'}), 404

def run_mission_control(port=5000):
    """Run the NASA Home Base Mission Control interface"""
    if not FLASK_AVAILABLE:
        print("❌ Flask is required to run Mission Control")
        print("   Install with: pip install flask")
        return
    
    print("\n" + "="*60)
    print("🚀 NASA HOME BASE MISSION CONTROL")
    print("="*60)
    print(f"\n🌐 Mission Control Interface: http://localhost:{port}")
    print("\nChecking NetworkBuster services...")
    
    home_base.check_all_ports()
    for service, info in home_base.ports.items():
        status_icon = "✅" if info['status'] == 'online' else "⚠️"
        print(f"  {status_icon} {info['name']} (Port {info['port']}): {info['status'].upper()}")
    
    print(f"\n🎯 Opening Mission Control in browser...")
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    
    print(f"\n📡 Mission Control Active - Press Ctrl+C to abort mission\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Mission Control shutdown initiated")
        print("✅ All systems secured")

def main():
    """Main entry point"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " NASA HOME BASE - NetworkBuster Integration".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("\nUsage: python nasa_home_base.py [options]")
        print("\nOptions:")
        print("  --help          Show this help message")
        print("  --port PORT     Set Mission Control port (default: 5000)")
        print("  --check         Check service status only")
        print("\nExample:")
        print("  python nasa_home_base.py")
        print("  python nasa_home_base.py --port 5001")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        base = NASAHomeBase()
        base.check_all_ports()
        print("\n📊 Service Status:")
        for service, info in base.ports.items():
            print(f"  • {info['name']}: {info['status'].upper()}")
        return
    
    port = 5000
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    
    run_mission_control(port)

if __name__ == "__main__":
    main()
