#!/usr/bin/env node

/**
 * NetworkBuster Unified Development Server
 * Runs Express backend and Vite frontend concurrently
 * with hot module replacement support
 */

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.dirname(__filename);
const viteBin = path.join(projectRoot, 'node_modules', 'vite', 'bin', 'vite.js');
const backendPort = '3001';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function startServer() {
  log('\n╔════════════════════════════════════════╗', 'cyan');
  log('║ NetworkBuster Unified Dev Environment ║', 'cyan');
  log('╚════════════════════════════════════════╝', 'cyan');
  log('\n🚀 Starting development servers...\n', 'bright');

  // Start Express backend
  const backendProcess = spawn(process.execPath, [path.join(projectRoot, 'server.js')], {
    cwd: projectRoot,
    env: { ...process.env, PORT: backendPort },
    stdio: 'inherit'
  });

  // Wait 2 seconds for backend to start, then start Vite
  setTimeout(() => {
    log('\n📦 Starting Vite frontend development server...\n', 'bright');
    
    const viteProcess = fs.existsSync(viteBin)
      ? spawn(process.execPath, [viteBin], {
          cwd: projectRoot,
          stdio: 'inherit'
        })
      : spawn('npx', ['vite'], {
          cwd: projectRoot,
          stdio: 'inherit',
          shell: true
        });

    // Handle process termination
    const cleanup = () => {
      log('\n\n🛑 Shutting down development servers...\n', 'yellow');
      backendProcess.kill();
      viteProcess.kill();
      process.exit(0);
    };

    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
  }, 2000);

  // Handle backend process errors
  backendProcess.on('error', (err) => {
    log(`❌ Failed to start backend: ${err.message}`, 'red');
    process.exit(1);
  });
}

// Display setup info
log('\n📝 Development Setup:', 'bright');
log(`  Backend (Express):  http://localhost:${backendPort}`, 'green');
log('  Frontend (Vite):    http://localhost:5173', 'blue');
log('  API Proxy:          Configured', 'green');
log('  Hot Reload:         Enabled', 'green');
log('\n⚡ Available Routes:', 'bright');
log('  /                 → Home Hub', 'yellow');
log('  /home             → Navigation Hub', 'yellow');
log('  /ai-world         → AI World Environment', 'yellow');
log('  /dashboard        → Dashboard', 'yellow');
log('  /control-panel    → Control Panel', 'yellow');
log('  /overlay          → Real-time Overlay', 'yellow');
log('  /blog             → Blog', 'yellow');
log('  /api/*            → API Endpoints', 'yellow');
log('\nPress Ctrl+C to stop all servers\n', 'cyan');

startServer();
