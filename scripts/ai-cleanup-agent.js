/**
 * AI Repository Cleanup Agent
 * Uses the AI providers to analyze and suggest repository cleanup actions
 * 
 * Run: node scripts/ai-cleanup-agent.js [--dry-run] [--execute]
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

// Patterns to identify for cleanup
const CLEANUP_PATTERNS = {
    backup: {
        patterns: [/\.bak$/, /\.backup$/, /\.original$/, /\.old$/, /~$/],
        action: 'remove',
        reason: 'Backup file - should be tracked in git history instead'
    },
    temp: {
        patterns: [/\.tmp$/, /\.temp$/, /\.swp$/, /\.swo$/],
        action: 'remove',
        reason: 'Temporary file - should not be committed'
    },
    duplicateConfig: {
        patterns: [/\.code-workspace$/],
        locations: ['docs/', 'src/'],
        action: 'review',
        reason: 'Workspace config in non-standard location'
    },
    logFiles: {
        patterns: [/\.log$/, /debug\.txt$/, /error\.txt$/],
        action: 'remove',
        reason: 'Log file - should be in .gitignore'
    },
    nodeModules: {
        patterns: [/node_modules/],
        action: 'skip',
        reason: 'Dependencies - should be in .gitignore'
    },
    buildArtifacts: {
        patterns: [/dist\//, /build\//, /\.next\//],
        action: 'review',
        reason: 'Build artifact - consider .gitignore'
    }
};

// Server variant analysis for consolidation suggestions
const SERVER_VARIANTS = [
    'server.js',
    'server-audio.js',
    'server-enhanced.js',
    'server-optimized.js',
    'server-universal.js'
];

class AICleanupAgent {
    constructor(options = {}) {
        this.dryRun = options.dryRun ?? true;
        this.verbose = options.verbose ?? true;
        this.issues = [];
        this.actions = [];
    }

    log(msg, type = 'info') {
        const prefix = {
            info: '  ',
            warn: '⚠️',
            error: '❌',
            success: '✓',
            action: '🔧'
        }[type] || '  ';
        console.log(`${prefix} ${msg}`);
    }

    async scanDirectory(dir, depth = 0) {
        if (depth > 10) return; // Max recursion

        let entries;
        try {
            entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
            return;
        }

        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            const relativePath = path.relative(ROOT, fullPath);

            // Skip node_modules and .git
            if (entry.name === 'node_modules' || entry.name === '.git') continue;

            if (entry.isDirectory()) {
                await this.scanDirectory(fullPath, depth + 1);
            } else {
                await this.analyzeFile(fullPath, relativePath);
            }
        }
    }

    async analyzeFile(fullPath, relativePath) {
        const filename = path.basename(fullPath);

        for (const [category, config] of Object.entries(CLEANUP_PATTERNS)) {
            for (const pattern of config.patterns) {
                if (pattern.test(filename) || pattern.test(relativePath)) {
                    this.issues.push({
                        path: relativePath,
                        fullPath,
                        category,
                        action: config.action,
                        reason: config.reason
                    });
                    break;
                }
            }
        }
    }

    analyzeServerVariants() {
        const serverFiles = SERVER_VARIANTS.filter(f =>
            fs.existsSync(path.join(ROOT, f))
        );

        if (serverFiles.length > 1) {
            this.log(`\nFound ${serverFiles.length} server variants:`, 'warn');
            for (const f of serverFiles) {
                const stats = fs.statSync(path.join(ROOT, f));
                const size = Math.round(stats.size / 1024);
                this.log(`  ${f} (${size} KB)`, 'info');
            }

            this.issues.push({
                path: 'Multiple server files',
                category: 'consolidation',
                action: 'review',
                reason: 'Consider consolidating server variants or documenting their purposes',
                files: serverFiles
            });
        }
    }

    async generateReport() {
        console.log('\n' + '═'.repeat(60));
        console.log('🤖 AI Repository Cleanup Report');
        console.log('═'.repeat(60) + '\n');

        // Group issues by category
        const byCategory = {};
        for (const issue of this.issues) {
            if (!byCategory[issue.category]) byCategory[issue.category] = [];
            byCategory[issue.category].push(issue);
        }

        for (const [category, issues] of Object.entries(byCategory)) {
            console.log(`\n📁 ${category.toUpperCase()} (${issues.length} items)`);
            console.log('─'.repeat(40));

            for (const issue of issues) {
                const actionIcon = {
                    remove: '🗑️',
                    review: '👁️',
                    skip: '⏭️'
                }[issue.action] || '❓';

                console.log(`${actionIcon} ${issue.path}`);
                if (this.verbose) {
                    console.log(`   └─ ${issue.reason}`);
                }
            }
        }

        console.log('\n' + '═'.repeat(60));
        console.log(`Total issues found: ${this.issues.length}`);
        console.log(`  - Remove: ${this.issues.filter(i => i.action === 'remove').length}`);
        console.log(`  - Review: ${this.issues.filter(i => i.action === 'review').length}`);
        console.log('═'.repeat(60) + '\n');

        return this.issues;
    }

    async executeCleanup() {
        if (this.dryRun) {
            console.log('\n🔍 DRY RUN MODE - No files will be modified\n');
        }

        const toRemove = this.issues.filter(i => i.action === 'remove');

        for (const issue of toRemove) {
            if (this.dryRun) {
                this.log(`Would delete: ${issue.path}`, 'action');
            } else {
                try {
                    fs.unlinkSync(issue.fullPath);
                    this.log(`Deleted: ${issue.path}`, 'success');
                    this.actions.push({ action: 'deleted', path: issue.path });
                } catch (err) {
                    this.log(`Failed to delete ${issue.path}: ${err.message}`, 'error');
                }
            }
        }

        return this.actions;
    }

    async run() {
        console.log('\n🤖 Starting AI Repository Cleanup Agent...\n');
        console.log(`   Root: ${ROOT}`);
        console.log(`   Mode: ${this.dryRun ? 'Dry Run' : 'Execute'}\n`);

        await this.scanDirectory(ROOT);
        this.analyzeServerVariants();
        await this.generateReport();

        if (!this.dryRun) {
            await this.executeCleanup();
        }

        return this.issues;
    }
}

// CLI execution
const args = process.argv.slice(2);
const dryRun = !args.includes('--execute');
const verbose = !args.includes('--quiet');

const agent = new AICleanupAgent({ dryRun, verbose });
agent.run().then(issues => {
    if (dryRun && issues.length > 0) {
        console.log('Run with --execute to apply changes\n');
    }
}).catch(err => {
    console.error('Cleanup agent failed:', err);
    process.exit(1);
});

export default AICleanupAgent;
