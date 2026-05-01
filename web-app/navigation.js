/**
 * NetworkBuster Navigation & URL Router
 * Ties all strings, buttons, UI together by category
 * Base URL: networkbuster.net
 */

const SITE_CONFIG = {
  baseUrl: 'https://networkbuster.net',
  localUrl: 'http://localhost:3000',
  name: 'NetworkBuster',
  version: '1.0.1'
};

// URL Categories & Routes
const NAVIGATION = {
  // Main Categories
  main: {
    home: { path: '/', label: 'Home', icon: '🏠' },
    about: { path: '/about.html', label: 'About', icon: 'ℹ️' },
    projects: { path: '/projects.html', label: 'Projects', icon: '🚀' },
    technology: { path: '/technology.html', label: 'Technology', icon: '⚡' },
    documentation: { path: '/documentation.html', label: 'Docs', icon: '📖' },
    contact: { path: '/contact.html', label: 'Contact', icon: '✉️' }
  },

  // Apps & Tools
  apps: {
    dashboard: { path: '/dashboard/', label: 'Dashboard', icon: '📊', port: 3000 },
    blog: { path: '/blog/', label: 'Blog', icon: '📝' },
    authUI: { path: '/auth/', label: 'Auth Portal', icon: '🔐', port: 3003 },
    audioLab: { path: '/audio-lab', label: 'Audio Lab', icon: '🎵', port: 3002 },
    controlPanel: { path: '/control-panel', label: 'Control Panel', icon: '🎛️', port: 3000 },
    overlay: { path: '/overlay/', label: 'AI World Overlay', icon: '🌐' }
  },

  // API Endpoints
  api: {
    health: { path: '/api/health', label: 'Health Check', method: 'GET', port: 3000 },
    specs: { path: '/api/specs', label: 'System Specs', method: 'GET', port: 3001 },
    audioStream: { path: '/api/audio/stream/create', label: 'Audio Stream', method: 'POST', port: 3002 },
    audioSynth: { path: '/api/audio/synthesize', label: 'Synthesize', method: 'POST', port: 3002 },
    authLogin: { path: '/api/auth/login', label: 'Login', method: 'POST', port: 3003 },
    authSignup: { path: '/api/auth/signup', label: 'Sign Up', method: 'POST', port: 3003 },
    authDocs: { path: '/api/docs', label: 'API Docs', method: 'GET', port: 3003 }
  },

  // Sub-pages by category
  lunar: {
    calculator: { path: '/#calculator', label: 'Calculator', icon: '🧮' },
    data: { path: '/#data', label: 'Data Center', icon: '💾' },
    flashCommands: { path: '/flash-commands.html', label: 'Flash Commands', icon: '⚡' }
  },

  // Challenge Repo (AI World)
  aiworld: {
    main: { path: '/challengerepo/real-time-overlay/', label: 'AI World', icon: '🤖' },
    avatarWorld: { path: '/challengerepo/real-time-overlay/src/components/AvatarWorld.jsx', label: 'Avatar World', icon: '👤' },
    satelliteMap: { path: '/challengerepo/real-time-overlay/src/components/SatelliteMap.jsx', label: 'Satellite Map', icon: '🛰️' },
    cameraFeed: { path: '/challengerepo/real-time-overlay/src/components/CameraFeed.jsx', label: 'Camera Feed', icon: '📹' },
    connectionGraph: { path: '/challengerepo/real-time-overlay/src/components/ConnectionGraph.jsx', label: 'Connection Graph', icon: '🔗' },
    immersiveReader: { path: '/challengerepo/real-time-overlay/src/components/ImmersiveReader.jsx', label: 'Immersive Reader', icon: '👁️' }
  }
};

// Button configurations
const BUTTONS = {
  primary: {
    login: { label: 'Login', action: 'navigate', target: '/auth/', class: 'btn-primary' },
    signup: { label: 'Sign Up', action: 'navigate', target: '/auth/', class: 'btn-primary' },
    getStarted: { label: 'Get Started', action: 'navigate', target: '/documentation.html', class: 'btn-primary' },
    launchDashboard: { label: 'Launch Dashboard', action: 'navigate', target: '/dashboard/', class: 'btn-primary' }
  },
  secondary: {
    viewDocs: { label: 'View Docs', action: 'navigate', target: '/documentation.html', class: 'btn-secondary' },
    learnMore: { label: 'Learn More', action: 'navigate', target: '/about.html', class: 'btn-secondary' },
    contact: { label: 'Contact Us', action: 'navigate', target: '/contact.html', class: 'btn-secondary' }
  },
  action: {
    playMusic: { label: '▶️ Play', action: 'toggle', target: 'music-player', class: 'btn-action' },
    muteAudio: { label: '🔇 Mute', action: 'toggle', target: 'audio-mute', class: 'btn-action' },
    refreshData: { label: '🔄 Refresh', action: 'fetch', target: '/api/specs', class: 'btn-action' },
    startStream: { label: '🎵 Start Stream', action: 'post', target: '/api/audio/stream/create', class: 'btn-action' }
  }
};

// Feature flag for auth links (set via build or environment)
const AUTH_ENABLED = (typeof process !== 'undefined' && process.env && process.env.AUTH_ENABLED === 'true') || false;

// Remove auth routes/links when disabled
if (!AUTH_ENABLED) {
  delete NAVIGATION.apps.authUI;
  delete NAVIGATION.api.authLogin;
  delete NAVIGATION.api.authSignup;
  delete NAVIGATION.api.authDocs;
  delete BUTTONS.primary.login;
  delete BUTTONS.primary.signup;
  console.log('Auth links removed from navigation (AUTH_ENABLED != "true")');
}

// Generate full URL
function getFullUrl(route, useLocal = false) {
  const base = useLocal ? SITE_CONFIG.localUrl : SITE_CONFIG.baseUrl;
  if (route.port && useLocal) {
    return `http://localhost:${route.port}${route.path}`;
  }
  return `${base}${route.path}`;
} 

// Generate navigation HTML
function generateNavHTML(category = 'main') {
  const routes = NAVIGATION[category];
  if (!routes) return '';

  let html = '<nav class="nav-category">\n';
  for (const [key, route] of Object.entries(routes)) {
    html += `  <a href="${route.path}" class="nav-link" data-route="${key}">${route.icon || ''} ${route.label}</a>\n`;
  }
  html += '</nav>';
  return html;
}

// Generate button HTML
function generateButtonHTML(type, key) {
  const btn = BUTTONS[type]?.[key];
  if (!btn) return '';
  return `<button class="${btn.class}" data-action="${btn.action}" data-target="${btn.target}">${btn.label}</button>`;
}

// Export for use
export { SITE_CONFIG, NAVIGATION, BUTTONS, getFullUrl, generateNavHTML, generateButtonHTML };
