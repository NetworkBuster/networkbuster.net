#!/usr/bin/env node
/**
 * NetworkBuster Full Release Generator
 * Creates a comprehensive release package with all data, documentation, and resources
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync, cpSync } from 'fs';
import { join, basename } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

// Read package.json
const pkg = JSON.parse(readFileSync(join(rootDir, 'package.json'), 'utf8'));
const name = pkg.name || 'networkbuster';
const version = pkg.version || '0.0.0';
const releaseDate = new Date().toISOString().split('T')[0];

console.log(`\n╔════════════════════════════════════════════════════════════════╗`);
console.log(`║   NetworkBuster Full Release Generator v${version}          ║`);
console.log(`╚════════════════════════════════════════════════════════════════╝\n`);

// Create output directory
const outDir = join(rootDir, 'release');
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

const releaseDir = join(outDir, `${name}-${version}-full`);
if (!existsSync(releaseDir)) mkdirSync(releaseDir, { recursive: true });

console.log(`📁 Release directory: ${releaseDir}\n`);

// Files and directories to include
const itemsToInclude = [
  // Core files
  { src: 'package.json', desc: 'Package configuration' },
  { src: 'package-lock.json', desc: 'Dependency lock file' },
  { src: 'LICENSE', desc: 'MIT License' },
  { src: 'LICENSE.txt', desc: 'License text' },
  { src: 'README.md', desc: 'Main documentation' },
  { src: 'CHANGELOG.md', desc: 'Version history' },
  
  // Server files
  { src: 'server.js', desc: 'Main server' },
  { src: 'server-universal.js', desc: 'Universal server' },
  { src: 'proxy-server.js', desc: 'Proxy server' },
  { src: 'index.html', desc: 'Main HTML' },
  
  // Source code
  { src: 'src/', desc: 'React source code', dir: true },
  { src: 'api/', desc: 'API endpoints', dir: true },
  
  // Configuration
  { src: 'vite.config.js', desc: 'Vite configuration' },
  { src: 'vercel.json', desc: 'Vercel config' },
  
  // Data files
  { src: 'data/', desc: 'System data and specifications', dir: true },
  
  // Major projects
  { src: 'spaceship-3d-blueprints/', desc: 'Space infrastructure specs', dir: true },
  { src: 'mercedes-nvidia-ai-drive/', desc: 'Autonomous driving platform', dir: true },
  
  // Documentation
  { src: 'docs/', desc: 'Technical documentation', dir: true },
  
  // Android project
  { src: 'android/', desc: 'Android antigravity module', dir: true },
  
  // Web applications
  { src: 'web-app/', desc: 'Web applications', dir: true },
  { src: 'dashboard/', desc: 'Dashboard app', dir: true },
  { src: 'blog/', desc: 'Blog application', dir: true },
  
  // Scripts
  { src: 'scripts/', desc: 'Utility scripts', dir: true },
  
  // Additional resources
  { src: 'public-landing.html', desc: 'Landing page' },
];

console.log('📦 Copying files and directories...\n');

let copiedCount = 0;
let skippedCount = 0;

itemsToInclude.forEach(item => {
  const srcPath = join(rootDir, item.src);
  const destPath = join(releaseDir, item.src);
  
  if (existsSync(srcPath)) {
    try {
      if (item.dir) {
        mkdirSync(dirname(destPath), { recursive: true });
        cpSync(srcPath, destPath, { recursive: true });
        console.log(`  ✓ ${item.src.padEnd(40)} ${item.desc}`);
      } else {
        mkdirSync(dirname(destPath), { recursive: true });
        cpSync(srcPath, destPath);
        console.log(`  ✓ ${item.src.padEnd(40)} ${item.desc}`);
      }
      copiedCount++;
    } catch (err) {
      console.log(`  ⚠ ${item.src.padEnd(40)} Error: ${err.message}`);
      skippedCount++;
    }
  } else {
    console.log(`  ⊘ ${item.src.padEnd(40)} Not found`);
    skippedCount++;
  }
});

console.log(`\n📊 Summary: ${copiedCount} items copied, ${skippedCount} skipped\n`);

// Create release manifest
const manifest = {
  name: pkg.name,
  version: pkg.version,
  releaseDate,
  description: pkg.description,
  author: pkg.author,
  license: pkg.license,
  repository: pkg.repository,
  homepage: pkg.homepage,
  node: pkg.engines?.node || '24.x',
  contents: {
    core: ['server.js', 'package.json', 'README.md', 'CHANGELOG.md'],
    source: ['src/', 'api/'],
    data: ['data/', 'docs/'],
    projects: ['spaceship-3d-blueprints/', 'mercedes-nvidia-ai-drive/', 'android/'],
    webApps: ['web-app/', 'dashboard/', 'blog/'],
    scripts: ['scripts/']
  },
  features: [
    'Mercedes-NVIDIA AI Drive Platform',
    'Space Infrastructure Blueprints',
    'Android Antigravity Module (Kotlin 2.0.21, SDK 35)',
    'React Frontend Applications',
    'Express.js Backend Server',
    'Real-time Data Processing',
    'Comprehensive Documentation'
  ],
  itemsCopied: copiedCount,
  itemsSkipped: skippedCount
};

const manifestPath = join(releaseDir, 'RELEASE-MANIFEST.json');
writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
console.log(`✓ Created release manifest: ${basename(manifestPath)}\n`);

// Create release notes
const releaseNotes = `# NetworkBuster Release v${version}
Release Date: ${releaseDate}

## 🎉 What's New in v${version}

### Major Features

#### 🚗 Mercedes-NVIDIA AI Drive Platform
- Complete autonomous driving system documentation
- NVIDIA Drive Thor/Orin platform integration (2000 TOPS)
- Level 3/4 autonomy capabilities
- Cloud fleet management and OTA updates
- Comprehensive API documentation

#### 🚀 Space Infrastructure Enhancements
- Moonbase Alpha specifications
- Cloud One orbital station details
- NBS-1 Data Voyager spacecraft
- Complete 3D blueprints and technical specs

#### 📱 Android Antigravity Module Updates
- Updated to Kotlin 2.0.21
- Android Gradle Plugin 8.7.3
- Android SDK 35
- Java 17 compatibility

### Additional Updates
- Enhanced packaging and distribution scripts
- Improved documentation structure
- Updated dependencies and security patches
- Comprehensive data files and specifications

## 📦 Release Contents

This release includes:
- ✓ Complete source code (src/, api/)
- ✓ All documentation (docs/, README.md)
- ✓ Major projects (Mercedes-NVIDIA, Space Infrastructure, Android)
- ✓ Data files and system specifications
- ✓ Web applications (dashboard, blog)
- ✓ Build and deployment scripts
- ✓ Configuration files

## 🚀 Getting Started

### Prerequisites
- Node.js 24.x or higher
- npm 10.0.0 or higher

### Installation

\`\`\`bash
# Extract the release
unzip ${name}-${version}-full.zip
cd ${name}-${version}-full

# Install dependencies
npm install

# Start the server
npm start
\`\`\`

### Available Scripts

- \`npm start\` - Start production server
- \`npm run dev\` - Start development server
- \`npm run build\` - Build frontend applications
- \`npm run test\` - Run tests

## 📚 Documentation

- **Main README**: README.md
- **Changelog**: CHANGELOG.md
- **API Docs**: api/README.md
- **Mercedes-NVIDIA**: mercedes-nvidia-ai-drive/README.md
- **Space Infrastructure**: spaceship-3d-blueprints/README.md
- **Technical Docs**: docs/

## 🤝 Contributing

Visit our repository: ${pkg.repository?.url || 'https://github.com/NetworkBuster/networkbuster.net'}

## 📄 License

${pkg.license} - See LICENSE file for details

## 🙏 Acknowledgments

- Mercedes-Benz AG
- NVIDIA Corporation
- NetworkBuster Contributors
- Open Source Community

---

For support and issues: ${pkg.bugs?.url || 'https://github.com/NetworkBuster/networkbuster.net/issues'}
`;

const releaseNotesPath = join(releaseDir, 'RELEASE-NOTES.md');
writeFileSync(releaseNotesPath, releaseNotes);
console.log(`✓ Created release notes: ${basename(releaseNotesPath)}\n`);

// Create installation guide
const installGuide = `# NetworkBuster v${version} - Installation Guide

## Quick Start

### 1. Extract Release
\`\`\`bash
unzip ${name}-${version}-full.zip
cd ${name}-${version}-full
\`\`\`

### 2. Install Dependencies
\`\`\`bash
npm install
\`\`\`

### 3. Start Server
\`\`\`bash
npm start
\`\`\`

Visit http://localhost:3000 in your browser.

## Detailed Installation

### System Requirements
- **OS**: Windows, macOS, Linux
- **Node.js**: 24.x or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space

### Build Frontend (Optional)
\`\`\`bash
cd src
npm install
npm run build
\`\`\`

### Configure Environment
1. Copy \`.env.example\` to \`.env\`
2. Edit configuration as needed
3. Restart server

### Run Tests
\`\`\`bash
npm test
\`\`\`

## Project Structure

- \`src/\` - React frontend source
- \`api/\` - Backend API endpoints
- \`server.js\` - Main server entry point
- \`docs/\` - Technical documentation
- \`data/\` - System specifications
- \`mercedes-nvidia-ai-drive/\` - Autonomous driving project
- \`spaceship-3d-blueprints/\` - Space infrastructure specs
- \`android/\` - Android mobile app

## Troubleshooting

### Port Already in Use
\`\`\`bash
# Use different port
PORT=3001 npm start
\`\`\`

### Dependencies Failed
\`\`\`bash
# Clean install
rm -rf node_modules package-lock.json
npm install
\`\`\`

For more help, see docs/troubleshooting.md or visit our support portal.
`;

const installGuidePath = join(releaseDir, 'INSTALL.md');
writeFileSync(installGuidePath, installGuide);
console.log(`✓ Created installation guide: ${basename(installGuidePath)}\n`);

// Create archive
console.log('📦 Creating release archive...\n');
const zipName = `${name}-${version}-full.zip`;
const zipPath = join(outDir, zipName);

try {
  process.chdir(outDir);
  if (process.platform === 'win32') {
    execSync(`powershell -Command "Compress-Archive -Path '${basename(releaseDir)}/*' -DestinationPath '${zipName}' -Force"`, { stdio: 'inherit' });
  } else {
    execSync(`zip -r '${zipName}' '${basename(releaseDir)}'`, { stdio: 'inherit' });
  }
  console.log(`\n✓ Created release archive: ${zipPath}\n`);
} catch (e) {
  console.error('Failed to create archive:', e.message);
  process.exit(1);
}

// Summary
console.log(`╔════════════════════════════════════════════════════════════════╗`);
console.log(`║                    Release Complete!                           ║`);
console.log(`╚════════════════════════════════════════════════════════════════╝`);
console.log(`\n📦 Release Package: ${zipPath}`);
console.log(`📊 Version: ${version}`);
console.log(`📅 Date: ${releaseDate}`);
console.log(`💾 Size: Calculating...`);

try {
  const stats = execSync(`du -sh "${zipPath}" 2>/dev/null || echo "Unknown"`, { encoding: 'utf8' });
  console.log(`💾 Size: ${stats.split('\t')[0]}`);
} catch (e) {
  // Size calculation failed, skip
}

console.log(`\n✨ Next steps:`);
console.log(`   1. Test the release: cd ${releaseDir} && npm install && npm start`);
console.log(`   2. Review RELEASE-NOTES.md`);
console.log(`   3. Upload to GitHub releases`);
console.log(`   4. Update deployment documentation\n`);
