import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';
import { execSync, exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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
  if (appState.logs.length > 100) {
    appState.logs.shift();
  }
  console.log(logEntry);
}

// Update uptime
setInterval(() => {
  appState.uptime = Math.floor((Date.now() - appState.startTime) / 1000);
}, 1000);

// Request counter middleware
app.use((req, res, next) => {
  appState.requestCount++;
  next();
});

// ============================================
// OPERATIONAL API ENDPOINTS
// ============================================

// Health check endpoint
app.get('/api/health', (req, res) => {
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
      memoryUsage: process.memoryUsage(),
      freeMemory: os.freemem(),
      totalMemory: os.totalmem()
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

// ============================================
// GIT NAVIGATION API ENDPOINTS
// ============================================

// Get git repository status
app.get('/api/git/status', async (req, res) => {
  try {
    const gitDir = path.join(__dirname, '.git');
    const isGitRepo = require('fs').existsSync(gitDir);

    if (!isGitRepo) {
      return res.json({ error: 'Not a git repository', isGitRepo: false });
    }

    const status = execSync('git status --porcelain', { cwd: __dirname }).toString().trim();
    const branch = execSync('git rev-parse --abbrev-ref HEAD', { cwd: __dirname }).toString().trim();
    const commit = execSync('git rev-parse HEAD', { cwd: __dirname }).toString().trim();

    const files = status.split('\n').filter(line => line.trim()).map(line => {
      const status = line.substring(0, 2);
      const file = line.substring(3);
      return { status, file };
    });

    res.json({
      isGitRepo: true,
      branch,
      commit: commit.substring(0, 7),
      files,
      hasChanges: files.length > 0,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message, isGitRepo: false });
  }
});

// Get git branches
app.get('/api/git/branches', async (req, res) => {
  try {
    const branches = execSync('git branch -a', { cwd: __dirname }).toString().trim();
    const currentBranch = execSync('git rev-parse --abbrev-ref HEAD', { cwd: __dirname }).toString().trim();

    const branchList = branches.split('\n').map(branch => {
      const isCurrent = branch.startsWith('*');
      const name = branch.replace('*', '').trim();
      return { name, current: isCurrent };
    });

    res.json({
      branches: branchList,
      current: currentBranch,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get git commits
app.get('/api/git/commits', async (req, res) => {
  try {
    const limit = req.query.limit || 10;
    const commits = execSync('git log --oneline -' + limit, { cwd: __dirname }).toString().trim();

    const commitList = commits.split('\n').map(line => {
      const [hash, ...messageParts] = line.split(' ');
      return {
        hash,
        message: messageParts.join(' '),
        shortHash: hash.substring(0, 7)
      };
    });

    res.json({
      commits: commitList,
      count: commitList.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get git file tree
app.get('/api/git/files', async (req, res) => {
  try {
    const tree = execSync('git ls-tree -r --name-only HEAD', { cwd: __dirname }).toString().trim();
    const files = tree.split('\n').filter(file => file.trim());

    // Group files by directory
    const fileTree = {};
    files.forEach(file => {
      const parts = file.split('/');
      let current = fileTree;

      parts.forEach((part, index) => {
        if (index === parts.length - 1) {
          // File
          if (!current._files) current._files = [];
          current._files.push(part);
        } else {
          // Directory
          if (!current[part]) current[part] = {};
          current = current[part];
        }
      });
    });

    res.json({
      files: fileTree,
      totalFiles: files.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get git diff
app.get('/api/git/diff', async (req, res) => {
  try {
    const diff = execSync('git diff', { cwd: __dirname }).toString();
    res.json({
      diff,
      hasChanges: diff.length > 0,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// CONTENT CONNECTIONS API ENDPOINTS
// ============================================

// Get content sections
app.get('/api/content/sections', (req, res) => {
  const sections = {
    main: [
      { id: 'home', title: 'Home', path: '/', icon: '🏠', type: 'page' },
      { id: 'about', title: 'About', path: '/about.html', icon: 'ℹ️', type: 'page' },
      { id: 'projects', title: 'Projects', path: '/projects.html', icon: '🚀', type: 'page' },
      { id: 'technology', title: 'Technology', path: '/technology.html', icon: '⚡', type: 'page' },
      { id: 'documentation', title: 'Documentation', path: '/documentation.html', icon: '📖', type: 'page' },
      { id: 'contact', title: 'Contact', path: '/contact.html', icon: '✉️', type: 'page' }
    ],
    apps: [
      { id: 'dashboard', title: 'Dashboard', path: '/dashboard/', icon: '📊', type: 'app', port: 3000 },
      { id: 'control-panel', title: 'Control Panel', path: '/control-panel', icon: '🎛️', type: 'app', port: 3000 },
      { id: 'audio-lab', title: 'Audio Lab', path: '/audio-lab', icon: '🎵', type: 'app', port: 3002 },
      { id: 'auth-portal', title: 'Auth Portal', path: '/auth/', icon: '🔐', type: 'app', port: 3003 },
      { id: 'overlay', title: 'AI World Overlay', path: '/overlay/', icon: '🌐', type: 'app' },
      { id: 'git-nav', title: 'Git Navigator', path: '/git-nav', icon: '📂', type: 'app', port: 3000 }
    ],
    tools: [
      { id: 'calculator', title: 'Calculator', path: '/#calculator', icon: '🧮', type: 'tool' },
      { id: 'data-center', title: 'Data Center', path: '/#data', icon: '💾', type: 'tool' },
      { id: 'flash-commands', title: 'Flash Commands', path: '/flash-commands.html', icon: '⚡', type: 'tool' },
      { id: 'packages', title: 'Packages', path: '/packages.html', icon: '📦', type: 'tool' },
      { id: 'function-hud', title: 'Function HUD', path: '/hud.html', icon: '🛰️', type: 'tool' },
      { id: 'blog', title: 'Blog', path: '/blog/', icon: '📝', type: 'tool' }
    ],
    api: [
      { id: 'health', title: 'Health Check', path: '/api/health', icon: '❤️', type: 'api', method: 'GET' },
      { id: 'status', title: 'System Status', path: '/api/status', icon: '📊', type: 'api', method: 'GET' },
      { id: 'logs', title: 'System Logs', path: '/api/logs', icon: '📜', type: 'api', method: 'GET' },
      { id: 'git-status', title: 'Git Status', path: '/api/git/status', icon: '📂', type: 'api', method: 'GET' },
      { id: 'git-branches', title: 'Git Branches', path: '/api/git/branches', icon: '🌿', type: 'api', method: 'GET' },
      { id: 'git-commits', title: 'Git Commits', path: '/api/git/commits', icon: '📋', type: 'api', method: 'GET' }
    ]
  };

  res.json({
    sections,
    totalSections: Object.keys(sections).length,
    timestamp: new Date().toISOString()
  });
});

// Get content connections (relationships between sections)
app.get('/api/content/connections', (req, res) => {
  const connections = {
    'home': ['about', 'projects', 'technology', 'documentation', 'contact'],
    'about': ['home', 'projects', 'technology'],
    'projects': ['home', 'about', 'technology', 'documentation'],
    'technology': ['home', 'projects', 'documentation', 'git-nav'],
    'documentation': ['home', 'technology', 'projects', 'git-nav'],
    'contact': ['home', 'about'],
    'dashboard': ['control-panel', 'data-center', 'function-hud'],
    'control-panel': ['dashboard', 'health', 'status', 'logs'],
    'audio-lab': ['dashboard', 'control-panel'],
    'auth-portal': ['dashboard', 'control-panel'],
    'overlay': ['dashboard', 'audio-lab'],
    'git-nav': ['technology', 'documentation', 'git-status', 'git-branches', 'git-commits'],
    'calculator': ['data-center', 'function-hud'],
    'data-center': ['calculator', 'dashboard', 'function-hud'],
    'flash-commands': ['control-panel', 'function-hud'],
    'packages': ['documentation', 'git-nav'],
    'function-hud': ['calculator', 'data-center', 'dashboard'],
    'blog': ['documentation', 'about']
  };

  res.json({
    connections,
    timestamp: new Date().toISOString()
  });
});

// Toggle feature endpoint
app.post('/api/toggle/:feature', (req, res) => {
  const { feature } = req.params;
  const isEnabled = req.body.enabled !== false;
  appState.lastAction = `Feature ${feature} toggled: ${isEnabled}`;
  addLog(`Toggled ${feature}`, `enabled: ${isEnabled}`);
  res.json({
    feature,
    enabled: isEnabled,
    message: `${feature} is now ${isEnabled ? 'enabled' : 'disabled'}`,
    timestamp: new Date().toISOString()
  });
});

// Git Navigator route (temporarily disabled)
// app.get('/git-nav', (req, res) => {
//   res.send(`<h1>Git Navigator</h1><p>Coming soon...</p>`);
// });

// Control panel route (temporarily removed for debugging)
// app.get('/control-panel', (req, res) => {
//   res.send(`<!DOCTYPE html>
// <html>
// <head>
//     <meta charset="UTF-8">
//     <meta name="viewport" content="width=device-width, initial-scale=1">
//     <title>NetworkBuster Control Panel</title>
// </head>
// <body>
//     <h1>Control Panel</h1>
//     <p>Operational Dashboard</p>
// </body>
// </html>`);
// });

// Serve static files
app.use('/blog', express.static(path.join(__dirname, 'blog')));
app.use('/dashboard', express.static(path.join(__dirname, 'dashboard/dist')));        
app.use('/overlay', express.static(path.join(__dirname, 'challengerepo/real-time-overlay/dist')));
app.use('/', express.static(path.join(__dirname, 'web-app')));

// SPA fallbacks
app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'dashboard/dist/index.html'));
});

app.get('/overlay', (req, res) => {
  res.sendFile(path.join(__dirname, 'challengerepo/real-time-overlay/dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`\n🚀 Server running at http://localhost:${PORT}`);
  console.log(`🏠 Web app: http://localhost:${PORT}`);
  console.log(`🎨 Real-time overlay: http://localhost:${PORT}/overlay`);
  console.log(`📈 Dashboard: http://localhost:${PORT}/dashboard`);
  console.log(`📝 Blog: http://localhost:${PORT}/blog`);
  console.log(`⚙️ Control Panel: http://localhost:${PORT}/control-panel\n`);
  addLog('Server started', `Port: ${PORT}`);
});
