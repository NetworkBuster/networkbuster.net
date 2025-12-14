import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

// Optional performance packages with fallbacks
let compression = null;
let helmet = null;

try {
  compression = (await import('compression')).default;
} catch {
  console.warn('⚠️  compression module not found - continuing without gzip');
}

try {
  helmet = (await import('helmet')).default;
} catch {
  console.warn('⚠️  helmet module not found - continuing without security headers');
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

// Performance: Apply optional middleware safely
if (compression) app.use(compression());
if (helmet) app.use(helmet());

// Middleware (always required)
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// Application state
const appState = {
  startTime: Date.now(),
  requestCount: 0,
  status: 'running',
  uptime: 0,
  lastAction: null,
  logs: []
};

// Helper function to add logs
function addLog(action, details = '') {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${action} ${details}`;
  appState.logs.push(logEntry);
  if (appState.logs.length > 50) {
    appState.logs.shift();
  }
  console.log(logEntry);
}

// Update uptime
setInterval(() => {
  appState.uptime = Math.floor((Date.now() - appState.startTime) / 1000);
}, 5000);

// Request counter middleware
let requestCount = 0;
app.use((req, res, next) => {
  requestCount++;
  appState.requestCount = requestCount;
  next();
});

// ============================================
// OPERATIONAL API ENDPOINTS
// ============================================

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.set('Cache-Control', 'public, max-age=5');
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: appState.uptime,
    requestCount: appState.requestCount,
    port: PORT
  });
});

// Get system status
app.get('/api/status', (req, res) => {
  res.set('Cache-Control', 'public, max-age=5');
  const memUsage = process.memoryUsage();
  res.json({
    status: appState.status,
    uptime: appState.uptime,
    requestCount: appState.requestCount,
    startTime: new Date(appState.startTime).toISOString(),
    lastAction: appState.lastAction,
    systemInfo: {
      platform: os.platform(),
      arch: os.arch(),
      cpus: os.cpus().length,
      memoryUsage: {
        heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024),
        heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024)
      },
      freeMemory: Math.round(os.freemem() / 1024 / 1024),
      totalMemory: Math.round(os.totalmem() / 1024 / 1024)
    }
  });
});

// Get application logs
app.get('/api/logs', (req, res) => {
  res.json({
    logs: appState.logs,
    count: appState.logs.length
  });
});

// Clear logs
app.post('/api/logs/clear', (req, res) => {
  appState.logs = [];
  appState.lastAction = 'Logs cleared';
  addLog('Cleared logs');
  res.json({ message: 'Logs cleared successfully', timestamp: new Date().toISOString() });
});

// Restart application indicator
app.post('/api/restart', (req, res) => {
  appState.lastAction = 'Restart initiated';
  addLog('Restart requested');
  res.json({
    message: 'Application restart requested',
    timestamp: new Date().toISOString(),
    action: 'restart'
  });
});

// Get component status
app.get('/api/components', (req, res) => {
  res.set('Cache-Control', 'public, max-age=10');
  res.json({
    components: {
      webApp: { status: 'running', path: '/', port: PORT },
      dashboard: { status: 'running', path: '/dashboard', port: PORT },
      overlay: { status: 'running', path: '/overlay', port: PORT },
      blog: { status: 'running', path: '/blog', port: PORT },
      api: { status: 'running', path: '/api', port: PORT }
    },
    timestamp: new Date().toISOString()
  });
});

// Toggle feature endpoint
app.post('/api/toggle/:feature', (req, res) => {
  const { feature } = req.params;
  const isEnabled = req.body?.enabled !== false;
  appState.lastAction = `Feature ${feature} toggled: ${isEnabled}`;
  addLog(`Toggled ${feature}`, `enabled: ${isEnabled}`);
  res.json({
    feature,
    enabled: isEnabled,
    message: `${feature} is now ${isEnabled ? 'enabled' : 'disabled'}`,
    timestamp: new Date().toISOString()
  });
});

// Control panel route
app.get('/control-panel', (req, res) => {
  res.set('Cache-Control', 'public, max-age=3600');
  res.send(`<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NetworkBuster Control Panel</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px}.container{max-width:1200px;margin:0 auto}.header{text-align:center;color:#fff;margin-bottom:30px}.header h1{font-size:2.5em;margin-bottom:10px}.status-bar{background:rgba(255,255,255,.95);padding:20px;border-radius:10px;margin-bottom:30px;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px}.status-item{padding:15px;background:#f8f9fa;border-radius:8px;border-left:4px solid #667eea}.status-label{font-size:.9em;color:#666;margin-bottom:5px;font-weight:600}.status-value{font-size:1.5em;color:#333;font-weight:bold}.controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;margin-bottom:30px}.control-section{background:rgba(255,255,255,.95);padding:25px;border-radius:10px}.section-title{font-size:1.2em;font-weight:700;color:#333;margin-bottom:20px}.button-group{display:flex;flex-direction:column;gap:10px}button{padding:12px 20px;border:none;border-radius:6px;font-size:1em;font-weight:600;cursor:pointer;transition:all .3s;color:#fff}.btn-success{background:#48bb78}.btn-success:hover{background:#38a169;transform:translateY(-2px)}.btn-primary{background:#667eea}.btn-primary:hover{background:#5568d3;transform:translateY(-2px)}.btn-info{background:#4299e1}.btn-info:hover{background:#3182ce;transform:translateY(-2px)}.btn-warning{background:#ed8936}.btn-warning:hover{background:#dd6b20;transform:translateY(-2px)}.btn-danger{background:#f56565}.btn-danger:hover{background:#e53e3e;transform:translateY(-2px)}.alert{padding:12px 16px;border-radius:6px;margin-bottom:15px}.alert-success{background:#c6f6d5;color:#22543d}.alert-error{background:#fed7d7;color:#742a2a}.alert-info{background:#bee3f8;color:#2c5282}.logs-container{background:rgba(255,255,255,.95);padding:25px;border-radius:10px}.logs-list{background:#1a202c;color:#a0aec0;padding:15px;border-radius:6px;max-height:300px;overflow-y:auto;font-family:monospace;font-size:.9em;line-height:1.6}</style></head><body><div class="container"><div class="header"><h1>Control Panel</h1><p>NetworkBuster Operational Dashboard</p></div><div class="status-bar"><div class="status-item"><div class="status-label">Status</div><div class="status-value" id="statusValue">Running</div></div><div class="status-item"><div class="status-label">Uptime</div><div class="status-value" id="uptimeValue">0s</div></div><div class="status-item"><div class="status-label">Requests</div><div class="status-value" id="requestsValue">0</div></div></div><div class="controls"><div class="control-section"><div class="section-title">Controls</div><div class="button-group"><button class="btn-success" onclick="checkHealth()">Health Check</button><button class="btn-info" onclick="getStatus()">System Info</button><button class="btn-danger" onclick="restartApp()">Restart</button></div></div></div><div class="logs-container"><div class="logs-list" id="logsList">Loading logs...</div></div></div><script>function updateStatus(){fetch('/api/status').then(r=>r.json()).then(d=>{document.getElementById('statusValue').textContent=d.status;document.getElementById('uptimeValue').textContent=formatUptime(d.uptime);document.getElementById('requestsValue').textContent=d.requestCount}).catch(e=>console.error(e))}function formatUptime(s){const h=Math.floor(s/3600),m=Math.floor(s%3600/60);return h>0?h+'h '+m+'m':m+'m'}function checkHealth(){fetch('/api/health').then(r=>r.json()).then(d=>alert('Healthy! Uptime: '+formatUptime(d.uptime))).catch(e=>alert('Failed'))}function getStatus(){fetch('/api/status').then(r=>r.json()).then(d=>{const m=d.systemInfo.memoryUsage;alert('Platform: '+d.systemInfo.platform+' | CPUs: '+d.systemInfo.cpus+' | Memory: '+m.heapUsed+'MB')}).catch(e=>alert('Failed'))}function restartApp(){fetch('/api/restart',{method:'POST'}).catch(e=>console.error(e))}setInterval(updateStatus,5000);updateStatus()</script></body></html>`);
});

// Serve static files (if they exist)
const staticPaths = [
  { prefix: '/blog', dir: 'blog' },
  { prefix: '/dashboard', dir: 'dashboard/dist' },
  { prefix: '/overlay', dir: 'challengerepo/real-time-overlay/dist' },
  { prefix: '/', dir: 'web-app' }
];

staticPaths.forEach(({ prefix, dir }) => {
  const fullPath = path.join(__dirname, dir);
  try {
    app.use(prefix, express.static(fullPath, { maxAge: '24h' }));
  } catch (err) {
    console.warn(`⚠️  Static path not found: ${fullPath}`);
  }
});

// SPA fallbacks (safe)
const dashboardPath = path.join(__dirname, 'dashboard/dist/index.html');
const overlayPath = path.join(__dirname, 'challengerepo/real-time-overlay/dist/index.html');

app.get('/dashboard/*', (req, res) => {
  res.set('Cache-Control', 'public, max-age=3600');
  res.sendFile(dashboardPath, (err) => {
    if (err) {
      res.status(404).json({ error: 'Dashboard not found' });
    }
  });
});

app.get('/overlay/*', (req, res) => {
  res.set('Cache-Control', 'public, max-age=3600');
  res.sendFile(overlayPath, (err) => {
    if (err) {
      res.status(404).json({ error: 'Overlay not found' });
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found', path: req.path });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`\n🚀 Server running at http://localhost:${PORT}`);
  console.log(`⚡ Features:`);
  if (compression) console.log(`   ✓ Compression enabled`);
  if (helmet) console.log(`   ✓ Security headers enabled`);
  console.log(`   ✓ Health checks available`);
  console.log(`   ✓ Control panel: /control-panel`);
  console.log(`   ✓ API: /api/*\n`);
  addLog('Server started', `Port: ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
