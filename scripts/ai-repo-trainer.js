/**
 * AI Repository Training Agent
 * Trains the AI model to understand repository patterns and file relationships
 * Uses the AI providers to generate embeddings and learn from existing code
 * 
 * Run: node scripts/ai-repo-trainer.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

// File categories for training
const FILE_CATEGORIES = {
    server: {
        pattern: /^server.*\.js$/,
        description: 'Server implementations and variants',
        examples: []
    },
    api: {
        pattern: /^api\//,
        description: 'API route handlers',
        examples: []
    },
    lib: {
        pattern: /^lib\//,
        description: 'Shared library modules',
        examples: []
    },
    scripts: {
        pattern: /^scripts\//,
        description: 'Automation and utility scripts',
        examples: []
    },
    docs: {
        pattern: /\.md$/,
        description: 'Documentation files',
        examples: []
    },
    config: {
        pattern: /\.(json|yaml|yml|env|config)$/i,
        description: 'Configuration files',
        examples: []
    },
    powershell: {
        pattern: /\.ps1$/,
        description: 'PowerShell automation scripts',
        examples: []
    },
    docker: {
        pattern: /(Dockerfile|docker-compose)/i,
        description: 'Docker containerization configs',
        examples: []
    }
};

// Training data structure
const TRAINING_DATA = {
    metadata: {
        generatedAt: new Date().toISOString(),
        repository: 'networkbuster.net',
        version: '1.0.0'
    },
    categories: {},
    fileRelationships: [],
    patterns: {
        naming: [],
        structure: [],
        dependencies: []
    },
    serverVariants: {
        files: [],
        purposes: {},
        consolidationOpportunities: []
    }
};

class AIRepoTrainer {
    constructor() {
        this.files = [];
        this.categories = { ...FILE_CATEGORIES };
    }

    log(msg) {
        console.log(`  ${msg}`);
    }

    async scanRepository() {
        console.log('\n📂 Scanning repository structure...\n');
        await this.scanDir(ROOT, '');
        console.log(`\n   Found ${this.files.length} files\n`);
    }

    async scanDir(dir, relativePath, depth = 0) {
        if (depth > 10) return;

        let entries;
        try {
            entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
            return;
        }

        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            const relPath = path.join(relativePath, entry.name);

            // Skip ignored directories
            if (['node_modules', '.git', 'dist', 'build', '.next'].includes(entry.name)) continue;

            if (entry.isDirectory()) {
                await this.scanDir(fullPath, relPath, depth + 1);
            } else {
                this.files.push({
                    name: entry.name,
                    path: relPath,
                    fullPath,
                    ext: path.extname(entry.name),
                    size: fs.statSync(fullPath).size
                });
            }
        }
    }

    categorizeFiles() {
        console.log('📊 Categorizing files...\n');

        for (const file of this.files) {
            for (const [catName, cat] of Object.entries(this.categories)) {
                if (cat.pattern.test(file.name) || cat.pattern.test(file.path)) {
                    cat.examples.push(file);
                    break;
                }
            }
        }

        for (const [name, cat] of Object.entries(this.categories)) {
            if (cat.examples.length > 0) {
                console.log(`   ${name}: ${cat.examples.length} files`);
                TRAINING_DATA.categories[name] = {
                    description: cat.description,
                    count: cat.examples.length,
                    files: cat.examples.map(f => f.path)
                };
            }
        }
    }

    analyzeServerVariants() {
        console.log('\n🖥️ Analyzing server variants...\n');

        const serverFiles = this.files.filter(f => /^server.*\.js$/.test(f.name) && f.path === f.name);
        TRAINING_DATA.serverVariants.files = serverFiles.map(f => f.name);

        // Analyze each variant
        for (const server of serverFiles) {
            const content = fs.readFileSync(server.fullPath, 'utf-8');

            // Extract purpose from comments/imports
            const purpose = this.extractServerPurpose(content, server.name);
            TRAINING_DATA.serverVariants.purposes[server.name] = purpose;

            console.log(`   ${server.name}: ${purpose.summary}`);
        }

        // Identify consolidation opportunities
        if (serverFiles.length > 2) {
            TRAINING_DATA.serverVariants.consolidationOpportunities.push({
                recommendation: 'Consider using a single server.js with feature flags',
                variants: serverFiles.map(f => f.name),
                approach: 'Use environment variables to enable/disable features'
            });
        }
    }

    extractServerPurpose(content, filename) {
        const result = {
            summary: 'Unknown',
            features: [],
            ports: [],
            dependencies: []
        };

        // Extract from filename
        if (filename.includes('audio')) {
            result.summary = 'Audio streaming server';
            result.features.push('audio-streaming', 'media-handling');
        } else if (filename.includes('enhanced')) {
            result.summary = 'Enhanced server with additional features';
        } else if (filename.includes('optimized')) {
            result.summary = 'Performance-optimized server';
            result.features.push('compression', 'caching');
        } else if (filename.includes('universal')) {
            result.summary = 'Universal server with all features';
            result.features.push('multi-purpose', 'comprehensive');
        } else if (filename === 'server.js') {
            result.summary = 'Main production server';
            result.features.push('core', 'production');
        }

        // Extract ports from content
        const portMatches = content.match(/PORT\s*[=:]\s*(\d+)|listen\((\d+)/g);
        if (portMatches) {
            result.ports = [...new Set(portMatches.map(m => m.match(/\d+/)?.[0]).filter(Boolean))];
        }

        // Extract major imports
        const importMatches = content.match(/(?:import|require)\s*(?:\{[^}]+\}|\w+)\s*from\s*['"]([^'"]+)['"]/g);
        if (importMatches) {
            result.dependencies = [...new Set(importMatches.slice(0, 10).map(m => m.match(/['"]([^'"]+)['"]/)?.[1]).filter(Boolean))];
        }

        return result;
    }

    analyzeNamingPatterns() {
        console.log('\n📝 Analyzing naming patterns...\n');

        const patterns = {
            kebabCase: this.files.filter(f => /-/.test(f.name.replace(/\.[^.]+$/, ''))),
            camelCase: this.files.filter(f => /[a-z][A-Z]/.test(f.name.replace(/\.[^.]+$/, ''))),
            uppercase: this.files.filter(f => /^[A-Z_]+\.[a-z]+$/.test(f.name)),
            lowercaseWithDots: this.files.filter(f => /^[a-z]+(\.[a-z]+)+\.[a-z]+$/.test(f.name))
        };

        for (const [style, files] of Object.entries(patterns)) {
            if (files.length > 0) {
                TRAINING_DATA.patterns.naming.push({
                    style,
                    count: files.length,
                    examples: files.slice(0, 5).map(f => f.name)
                });
                console.log(`   ${style}: ${files.length} files`);
            }
        }
    }

    generateTrainingOutput() {
        const outputPath = path.join(ROOT, 'data', 'repo-training-data.json');

        // Ensure data directory exists
        const dataDir = path.dirname(outputPath);
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }

        fs.writeFileSync(outputPath, JSON.stringify(TRAINING_DATA, null, 2));
        console.log(`\n💾 Training data saved to: data/repo-training-data.json\n`);

        return outputPath;
    }

    printSummary() {
        console.log('═'.repeat(60));
        console.log('📋 Repository Training Summary');
        console.log('═'.repeat(60));
        console.log(`\n   Total files analyzed: ${this.files.length}`);
        console.log(`   Server variants: ${TRAINING_DATA.serverVariants.files.length}`);
        console.log(`   Naming patterns: ${TRAINING_DATA.patterns.naming.length}`);
        console.log(`   File categories: ${Object.keys(TRAINING_DATA.categories).length}`);
        console.log('\n' + '═'.repeat(60) + '\n');
    }

    async run() {
        console.log('\n🤖 AI Repository Trainer\n');
        console.log('═'.repeat(60));

        await this.scanRepository();
        this.categorizeFiles();
        this.analyzeServerVariants();
        this.analyzeNamingPatterns();
        this.generateTrainingOutput();
        this.printSummary();

        return TRAINING_DATA;
    }
}

// CLI execution
const trainer = new AIRepoTrainer();
trainer.run().then(data => {
    console.log('Training complete! Data ready for AI consumption.\n');
}).catch(err => {
    console.error('Training failed:', err);
    process.exit(1);
});

export default AIRepoTrainer;
