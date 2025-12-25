import httpProxy from 'http-proxy';
import http from 'http';
import https from 'https';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3001';
const AI_GATEWAY_URL = process.env.AI_GATEWAY_URL || 'http://localhost:3002';
const PROXY_PORT = process.env.PROXY_PORT || 3000;
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://192.168.1.180:5173';

// Create proxy for backend
const backendProxy = httpProxy.createProxyServer({
  target: BACKEND_URL,
  changeOrigin: true,
  ws: true,
  xfwd: true,
  logLevel: 'info'
});

// Create proxy for AI gateway
const aiProxy = httpProxy.createProxyServer({
  target: AI_GATEWAY_URL,
  changeOrigin: true,
  xfwd: true,
  logLevel: 'info'
});

// Error handling for backend proxy
backendProxy.on('error', (err, req, res) => {
  console.error('Backend proxy error:', err);
  if (res.writeHead) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Bad Gateway', message: err.message }));
  }
});

// Error handling for AI proxy
aiProxy.on('error', (err, req, res) => {
  console.error('AI Gateway proxy error:', err);
  if (res.writeHead) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'AI Gateway Unavailable', message: err.message }));
  }
});

// Create HTTP server
const server = http.createServer((req, res) => {
  // Add CORS headers
  const allowOrigin = req.headers.origin || FRONTEND_URL;
  res.setHeader('Access-Control-Allow-Origin', allowOrigin);
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Device-Id, X-API-Key');
  res.setHeader('Access-Control-Allow-Credentials', 'true');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Route AI requests to AI gateway
  if (req.url.startsWith('/api/ai/') || req.url.startsWith('/ai/')) {
    // Strip /api prefix if present for AI gateway
    const aiPath = req.url.replace(/^\/api\/ai/, '').replace(/^\/ai/, '');
    req.url = aiPath || '/';

    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url} -> AI Gateway`);
    aiProxy.web(req, res);
    return;
  }

  // Log requests
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url} -> ${BACKEND_URL}`);

  // Forward all other requests to backend
  backendProxy.web(req, res);
});

// WebSocket support
server.on('upgrade', (req, socket, head) => {
  console.log(`[WebSocket] Upgrading ${req.url}`);
  backendProxy.ws(req, socket, head);
});

server.listen(PROXY_PORT, '0.0.0.0', () => {
  console.log(`\n🔄 Network Proxy Server`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`✓ Listening on all interfaces: http://0.0.0.0:${PROXY_PORT}`);
  console.log(`✓ Network access: http://192.168.1.180:${PROXY_PORT}`);
  console.log(`✓ Localhost: http://localhost:${PROXY_PORT}`);
  console.log(`✓ Backend: ${BACKEND_URL}`);
  console.log(`✓ AI Gateway: ${AI_GATEWAY_URL}`);
  console.log(`✓ Frontend: ${FRONTEND_URL}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📍 Routes:`);
  console.log(`   /api/ai/* -> AI Proxy Gateway`);
  console.log(`   /*        -> Backend Server`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
});

export default server;
