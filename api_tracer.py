"""
NetworkBuster - API Endpoint Tracer Module
Monitors and traces all API endpoints across services
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import time
from datetime import datetime
from collections import defaultdict
import threading

app = Flask(__name__)

# Define all API endpoints to trace
API_ENDPOINTS = {
    'web_server': {
        'base_url': 'http://localhost:3000',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Main landing page'},
            {'path': '/control-panel', 'method': 'GET', 'description': 'Control panel interface'},
            {'path': '/dashboard-control.html', 'method': 'GET', 'description': 'Dashboard control'},
            {'path': '/wifi7-mesh-overlay.html', 'method': 'GET', 'description': 'WiFi 7 mesh visualization'},
            {'path': '/api/*', 'method': 'GET', 'description': 'API routes'}
        ]
    },
    'api_server': {
        'base_url': 'http://localhost:3001',
        'endpoints': [
            {'path': '/health', 'method': 'GET', 'description': 'Health check endpoint'},
            {'path': '/api/health/detailed', 'method': 'GET', 'description': 'Detailed health status'},
            {'path': '/api/specs', 'method': 'GET', 'description': 'System specifications'},
            {'path': '/api/system/info', 'method': 'GET', 'description': 'System information'},
        ]
    },
    'audio_server': {
        'base_url': 'http://localhost:3002',
        'endpoints': [
            {'path': '/api/audio/stream/*', 'method': 'GET', 'description': 'Audio streaming'},
            {'path': '/api/audio/synthesize', 'method': 'GET', 'description': 'Frequency synthesis'},
            {'path': '/api/audio/detect-frequency', 'method': 'GET', 'description': 'Frequency detection'},
            {'path': '/audio-lab', 'method': 'GET', 'description': 'Audio lab interface'},
        ]
    },
    'mission_control': {
        'base_url': 'http://localhost:5000',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Mission control dashboard'},
            {'path': '/api/status', 'method': 'GET', 'description': 'Service status'},
            {'path': '/api/services', 'method': 'GET', 'description': 'Service list'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
        ]
    },
    'network_map': {
        'base_url': 'http://localhost:6000',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Network topology map'},
            {'path': '/api/devices', 'method': 'GET', 'description': 'Device listing'},
            {'path': '/api/docs', 'method': 'GET', 'description': 'Documentation files'},
            {'path': '/api/logs/*', 'method': 'GET', 'description': 'Device logs'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
        ]
    },
    'universal_launcher': {
        'base_url': 'http://localhost:7000',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Universal launcher dashboard'},
            {'path': '/api/status', 'method': 'GET', 'description': 'All services status'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
        ]
    },
    'api_tracer': {
        'base_url': 'http://localhost:8000',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'API Tracer dashboard'},
            {'path': '/api/trace', 'method': 'GET', 'description': 'Get all traces'},
            {'path': '/api/trace/service/<service>', 'method': 'GET', 'description': 'Traces by service'},
            {'path': '/api/endpoints', 'method': 'GET', 'description': 'All registered endpoints'},
            {'path': '/api/stats', 'method': 'GET', 'description': 'API call statistics'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
        ]
    }
}

# Store traces in memory
traces = []
stats = defaultdict(lambda: {'calls': 0, 'success': 0, 'failure': 0, 'avg_time': 0, 'total_time': 0})

def trace_endpoint(service, endpoint, base_url):
    """Trace a single endpoint"""
    start_time = time.time()
    trace_entry = {
        'timestamp': datetime.now().isoformat(),
        'service': service,
        'endpoint': endpoint['path'],
        'method': endpoint['method'],
        'url': base_url + endpoint['path'].replace('*', ''),
        'status': None,
        'response_time': None,
        'error': None
    }
    
    try:
        response = requests.request(
            endpoint['method'],
            base_url + endpoint['path'].replace('*', ''),
            timeout=3
        )
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        trace_entry['status'] = response.status_code
        trace_entry['response_time'] = round(response_time, 2)
        trace_entry['success'] = 200 <= response.status_code < 300
        
        # Update stats
        key = f"{service}:{endpoint['path']}"
        stats[key]['calls'] += 1
        if trace_entry['success']:
            stats[key]['success'] += 1
        else:
            stats[key]['failure'] += 1
        stats[key]['total_time'] += response_time
        stats[key]['avg_time'] = round(stats[key]['total_time'] / stats[key]['calls'], 2)
        
    except Exception as e:
        trace_entry['error'] = str(e)
        trace_entry['success'] = False
        key = f"{service}:{endpoint['path']}"
        stats[key]['calls'] += 1
        stats[key]['failure'] += 1
    
    traces.append(trace_entry)
    
    # Keep only last 1000 traces
    if len(traces) > 1000:
        traces.pop(0)
    
    return trace_entry

def auto_trace_loop():
    """Continuously trace all endpoints"""
    while True:
        for service, config in API_ENDPOINTS.items():
            if service == 'api_tracer':  # Don't trace ourselves
                continue
            
            for endpoint in config['endpoints']:
                if '*' not in endpoint['path']:  # Skip wildcard endpoints
                    trace_endpoint(service, endpoint, config['base_url'])
        
        time.sleep(10)  # Trace every 10 seconds

# HTML Dashboard
TRACER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster :: API Tracer</title>
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
            padding: 20px;
        }
        
        .header {
            border: 2px solid #0f0;
            padding: 20px;
            margin-bottom: 20px;
            background: #001100;
            box-shadow: 0 0 20px #0f0;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            text-shadow: 0 0 10px #0f0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            border: 1px solid #0f0;
            padding: 15px;
            background: #001100;
            text-align: center;
        }
        
        .stat-value {
            font-size: 32px;
            color: #0f0;
            text-shadow: 0 0 10px #0f0;
        }
        
        .stat-label {
            font-size: 12px;
            color: #0a0;
            margin-top: 5px;
        }
        
        .section {
            border: 2px solid #0a0;
            margin-bottom: 20px;
            background: #001100;
        }
        
        .section-header {
            background: #003300;
            padding: 10px 15px;
            border-bottom: 1px solid #0f0;
            font-weight: bold;
        }
        
        .section-content {
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .trace-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .trace-table th {
            background: #003300;
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #0f0;
            position: sticky;
            top: 0;
        }
        
        .trace-table td {
            padding: 8px;
            border-bottom: 1px solid #0a0;
        }
        
        .trace-table tr:hover {
            background: #002200;
        }
        
        .status-success {
            color: #0f0;
        }
        
        .status-error {
            color: #f00;
        }
        
        .endpoint-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 15px;
        }
        
        .endpoint-card {
            border: 1px solid #0a0;
            padding: 15px;
            background: #000;
        }
        
        .endpoint-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #0a0;
        }
        
        .method-badge {
            padding: 3px 10px;
            border: 1px solid #0f0;
            font-size: 11px;
        }
        
        .service-badge {
            padding: 3px 10px;
            background: #003300;
            border: 1px solid #0f0;
            font-size: 11px;
        }
        
        .cursor {
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .controls {
            padding: 15px;
            background: #002200;
            border: 1px solid #0f0;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 8px 15px;
            border: 1px solid #0f0;
            background: #000;
            color: #0f0;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: all 0.2s;
        }
        
        .btn:hover {
            background: #0f0;
            color: #000;
            box-shadow: 0 0 10px #0f0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>═══ API ENDPOINT TRACER ═══</h1>
        <p>Real-time monitoring of all NetworkBuster API endpoints</p>
        <p style="font-size: 12px; margin-top: 10px;">
            [root@networkbuster ~]$ tracer --monitor --realtime<span class="cursor">_</span>
        </p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="totalCalls">0</div>
            <div class="stat-label">TOTAL API CALLS</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="successRate">0%</div>
            <div class="stat-label">SUCCESS RATE</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="avgResponseTime">0ms</div>
            <div class="stat-label">AVG RESPONSE TIME</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="activeServices">0</div>
            <div class="stat-label">ACTIVE SERVICES</div>
        </div>
    </div>
    
    <div class="controls">
        <button class="btn" onclick="loadTraces()">[ REFRESH TRACES ]</button>
        <button class="btn" onclick="loadEndpoints()">[ REFRESH ENDPOINTS ]</button>
        <button class="btn" onclick="clearTraces()">[ CLEAR TRACES ]</button>
        <button class="btn" onclick="location.href='/api/trace'">[ EXPORT JSON ]</button>
    </div>
    
    <div class="section">
        <div class="section-header">═══ RECENT API TRACES (Last 50) ═══</div>
        <div class="section-content">
            <table class="trace-table">
                <thead>
                    <tr>
                        <th>TIMESTAMP</th>
                        <th>SERVICE</th>
                        <th>METHOD</th>
                        <th>ENDPOINT</th>
                        <th>STATUS</th>
                        <th>TIME</th>
                    </tr>
                </thead>
                <tbody id="tracesTable"></tbody>
            </table>
        </div>
    </div>
    
    <div class="section">
        <div class="section-header">═══ REGISTERED API ENDPOINTS ═══</div>
        <div class="section-content">
            <div class="endpoint-list" id="endpointsList"></div>
        </div>
    </div>
    
    <script>
        async function loadTraces() {
            try {
                const response = await fetch('/api/trace');
                const data = await response.json();
                
                const tbody = document.getElementById('tracesTable');
                tbody.innerHTML = data.traces.slice(-50).reverse().map(trace => `
                    <tr>
                        <td>${new Date(trace.timestamp).toLocaleTimeString()}</td>
                        <td><span class="service-badge">${trace.service}</span></td>
                        <td><span class="method-badge">${trace.method}</span></td>
                        <td>${trace.endpoint}</td>
                        <td class="${trace.success ? 'status-success' : 'status-error'}">
                            ${trace.status || 'ERROR'}
                        </td>
                        <td>${trace.response_time ? trace.response_time + 'ms' : 'N/A'}</td>
                    </tr>
                `).join('');
                
                updateStats(data.traces);
            } catch (error) {
                console.error('Failed to load traces:', error);
            }
        }
        
        async function loadEndpoints() {
            try {
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                const container = document.getElementById('endpointsList');
                let html = '';
                
                for (const [service, config] of Object.entries(data.endpoints)) {
                    config.endpoints.forEach(endpoint => {
                        html += `
                            <div class="endpoint-card">
                                <div class="endpoint-header">
                                    <span class="service-badge">${service}</span>
                                    <span class="method-badge">${endpoint.method}</span>
                                </div>
                                <div style="margin: 5px 0; color: #0f0;">${endpoint.path}</div>
                                <div style="font-size: 11px; color: #0a0;">${endpoint.description}</div>
                                <div style="font-size: 10px; color: #0a0; margin-top: 5px;">
                                    ${config.base_url}${endpoint.path}
                                </div>
                            </div>
                        `;
                    });
                }
                
                container.innerHTML = html;
            } catch (error) {
                console.error('Failed to load endpoints:', error);
            }
        }
        
        function updateStats(traces) {
            const totalCalls = traces.length;
            const successfulCalls = traces.filter(t => t.success).length;
            const successRate = totalCalls > 0 ? ((successfulCalls / totalCalls) * 100).toFixed(1) : 0;
            
            const responseTimes = traces.filter(t => t.response_time).map(t => t.response_time);
            const avgResponseTime = responseTimes.length > 0 
                ? (responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length).toFixed(2)
                : 0;
            
            const activeServices = new Set(traces.filter(t => t.success).map(t => t.service)).size;
            
            document.getElementById('totalCalls').textContent = totalCalls;
            document.getElementById('successRate').textContent = successRate + '%';
            document.getElementById('avgResponseTime').textContent = avgResponseTime + 'ms';
            document.getElementById('activeServices').textContent = activeServices;
        }
        
        function clearTraces() {
            if (confirm('Clear all traces?')) {
                fetch('/api/trace/clear', {method: 'POST'}).then(() => loadTraces());
            }
        }
        
        // Auto-refresh every 5 seconds
        loadTraces();
        loadEndpoints();
        setInterval(loadTraces, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TRACER_HTML)

@app.route('/api/trace')
def get_traces():
    return jsonify({
        'traces': traces,
        'count': len(traces),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trace/service/<service>')
def get_service_traces(service):
    service_traces = [t for t in traces if t['service'] == service]
    return jsonify({
        'service': service,
        'traces': service_traces,
        'count': len(service_traces)
    })

@app.route('/api/endpoints')
def get_endpoints():
    return jsonify({
        'endpoints': API_ENDPOINTS,
        'total': sum(len(config['endpoints']) for config in API_ENDPOINTS.values())
    })

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'stats': dict(stats),
        'total_traces': len(traces),
        'services': len(API_ENDPOINTS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trace/clear', methods=['POST'])
def clear_traces():
    global traces, stats
    traces = []
    stats = defaultdict(lambda: {'calls': 0, 'success': 0, 'failure': 0, 'avg_time': 0, 'total_time': 0})
    return jsonify({'success': True, 'message': 'Traces cleared'})

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'api-tracer',
        'traces': len(traces),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - API Endpoint Tracer Module              ║
║  Real-time API monitoring and tracing                     ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Start auto-trace thread
    trace_thread = threading.Thread(target=auto_trace_loop, daemon=True)
    trace_thread.start()
    print("🔍 Auto-trace thread started (10s interval)")
    
    print("🚀 Starting API Tracer on http://localhost:8000")
    print("⚡ Monitoring all NetworkBuster API endpoints")
    print("")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
