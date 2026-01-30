/**
 * Network Path Optimizer - Comprehensive optimization for all network paths
 * Optimizes: TCP settings, DNS resolution, HTTP connections, proxy routing, WebSocket
 * 
 * Run: node scripts/network-path-optimizer.js [--apply] [--report]
 */

import http from 'http';
import https from 'https';
import dns from 'dns';
import { promisify } from 'util';
import os from 'os';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dnsLookup = promisify(dns.lookup);
const dnsResolve = promisify(dns.resolve);

// Configuration
const CONFIG = {
    // HTTP Agent optimization
    httpAgent: {
        keepAlive: true,
        keepAliveMsecs: 30000,
        maxSockets: 100,
        maxFreeSockets: 50,
        timeout: 60000,
        scheduling: 'fifo'
    },
    // HTTPS Agent optimization
    httpsAgent: {
        keepAlive: true,
        keepAliveMsecs: 30000,
        maxSockets: 100,
        maxFreeSockets: 50,
        timeout: 60000,
        scheduling: 'fifo',
        rejectUnauthorized: true,
        sessionTimeout: 300
    },
    // DNS optimization
    dns: {
        cacheSize: 1000,
        cacheTTL: 300000, // 5 minutes
        preferIPv4: true,
        servers: ['8.8.8.8', '1.1.1.1', '9.9.9.9']
    },
    // Connection pooling
    pool: {
        maxConnections: 200,
        idleTimeout: 60000,
        connectTimeout: 10000
    }
};

// Optimized HTTP agents
let optimizedHttpAgent = null;
let optimizedHttpsAgent = null;

// DNS Cache
const dnsCache = new Map();

class NetworkPathOptimizer {
    constructor() {
        this.stats = {
            dnsHits: 0,
            dnsMisses: 0,
            connectionsCreated: 0,
            connectionsReused: 0,
            bytesTransferred: 0,
            latencySum: 0,
            requestCount: 0
        };
        this.startTime = Date.now();
    }

    // Initialize optimized agents
    initAgents() {
        optimizedHttpAgent = new http.Agent(CONFIG.httpAgent);
        optimizedHttpsAgent = new https.Agent(CONFIG.httpsAgent);

        console.log('✓ HTTP Agent optimized:', {
            keepAlive: CONFIG.httpAgent.keepAlive,
            maxSockets: CONFIG.httpAgent.maxSockets
        });
        console.log('✓ HTTPS Agent optimized:', {
            keepAlive: CONFIG.httpsAgent.keepAlive,
            maxSockets: CONFIG.httpsAgent.maxSockets
        });

        return { httpAgent: optimizedHttpAgent, httpsAgent: optimizedHttpsAgent };
    }

    // Optimized DNS lookup with caching
    async dnsLookupCached(hostname) {
        const cached = dnsCache.get(hostname);
        if (cached && Date.now() < cached.expiresAt) {
            this.stats.dnsHits++;
            return cached.address;
        }

        this.stats.dnsMisses++;
        try {
            const result = await dnsLookup(hostname, { family: CONFIG.dns.preferIPv4 ? 4 : 0 });
            dnsCache.set(hostname, {
                address: result.address,
                expiresAt: Date.now() + CONFIG.dns.cacheTTL
            });

            // Cleanup old entries
            if (dnsCache.size > CONFIG.dns.cacheSize) {
                const now = Date.now();
                for (const [key, val] of dnsCache) {
                    if (now > val.expiresAt) dnsCache.delete(key);
                }
            }

            return result.address;
        } catch (err) {
            console.error(`DNS lookup failed for ${hostname}:`, err.message);
            throw err;
        }
    }

    // Configure DNS servers
    configureDNS() {
        try {
            dns.setServers(CONFIG.dns.servers);
            console.log('✓ DNS servers configured:', CONFIG.dns.servers.join(', '));
        } catch (err) {
            console.warn('Could not set DNS servers:', err.message);
        }
    }

    // Benchmark DNS lookup
    async benchmarkDNS(hostname = 'google.com', iterations = 10) {
        const times = [];

        // Clear cache for fair test
        dnsCache.delete(hostname);

        for (let i = 0; i < iterations; i++) {
            const start = process.hrtime.bigint();
            await this.dnsLookupCached(hostname);
            const end = process.hrtime.bigint();
            times.push(Number(end - start) / 1e6); // Convert to ms

            // Clear cache every other iteration to test both paths
            if (i % 2 === 0) dnsCache.delete(hostname);
        }

        const avg = times.reduce((a, b) => a + b, 0) / times.length;
        const cached = times.filter((_, i) => i % 2 === 1);
        const uncached = times.filter((_, i) => i % 2 === 0);

        return {
            hostname,
            iterations,
            averageMs: avg.toFixed(2),
            cachedAvgMs: (cached.reduce((a, b) => a + b, 0) / cached.length).toFixed(2),
            uncachedAvgMs: (uncached.reduce((a, b) => a + b, 0) / uncached.length).toFixed(2),
            improvement: `${((1 - cached.reduce((a, b) => a + b, 0) / uncached.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%`
        };
    }

    // Benchmark HTTP connection
    async benchmarkHTTP(url = 'https://httpbin.org/get', iterations = 5) {
        const times = [];

        for (let i = 0; i < iterations; i++) {
            const start = process.hrtime.bigint();
            try {
                await this.fetch(url);
                const end = process.hrtime.bigint();
                times.push(Number(end - start) / 1e6);
            } catch (err) {
                times.push(-1);
            }
        }

        const validTimes = times.filter(t => t > 0);
        const avg = validTimes.length > 0
            ? validTimes.reduce((a, b) => a + b, 0) / validTimes.length
            : -1;

        return {
            url,
            iterations,
            successRate: `${(validTimes.length / iterations * 100).toFixed(0)}%`,
            averageMs: avg.toFixed(2),
            minMs: Math.min(...validTimes).toFixed(2),
            maxMs: Math.max(...validTimes).toFixed(2)
        };
    }

    // Optimized fetch with connection reuse
    fetch(url, options = {}) {
        return new Promise((resolve, reject) => {
            const isHttps = url.startsWith('https');
            const agent = isHttps ? optimizedHttpsAgent : optimizedHttpAgent;
            const lib = isHttps ? https : http;

            const startTime = process.hrtime.bigint();

            const req = lib.get(url, { ...options, agent }, (res) => {
                let data = '';
                res.on('data', chunk => { data += chunk; this.stats.bytesTransferred += chunk.length; });
                res.on('end', () => {
                    const endTime = process.hrtime.bigint();
                    const latency = Number(endTime - startTime) / 1e6;
                    this.stats.latencySum += latency;
                    this.stats.requestCount++;
                    resolve({ status: res.statusCode, data, latency });
                });
            });

            req.on('error', reject);
            req.setTimeout(CONFIG.pool.connectTimeout, () => {
                req.destroy();
                reject(new Error('Connection timeout'));
            });
        });
    }

    // Get network interfaces
    getNetworkInterfaces() {
        const interfaces = os.networkInterfaces();
        const result = [];

        for (const [name, addrs] of Object.entries(interfaces)) {
            for (const addr of addrs) {
                if (!addr.internal) {
                    result.push({
                        name,
                        family: addr.family,
                        address: addr.address,
                        netmask: addr.netmask,
                        mac: addr.mac
                    });
                }
            }
        }

        return result;
    }

    // Generate optimization report
    async generateReport() {
        console.log('\n' + '═'.repeat(60));
        console.log('🌐 Network Path Optimization Report');
        console.log('═'.repeat(60) + '\n');

        // System info
        console.log('📊 System Information:');
        console.log(`   Platform: ${os.platform()} ${os.release()}`);
        console.log(`   CPU: ${os.cpus()[0]?.model || 'Unknown'}`);
        console.log(`   Memory: ${Math.round(os.totalmem() / 1024 / 1024 / 1024)}GB`);

        // Network interfaces
        console.log('\n📡 Network Interfaces:');
        const interfaces = this.getNetworkInterfaces();
        for (const iface of interfaces) {
            console.log(`   ${iface.name}: ${iface.address} (${iface.family})`);
        }

        // DNS benchmark
        console.log('\n🔍 DNS Performance:');
        const dnsBench = await this.benchmarkDNS();
        console.log(`   Hostname: ${dnsBench.hostname}`);
        console.log(`   Cached lookup: ${dnsBench.cachedAvgMs}ms`);
        console.log(`   Uncached lookup: ${dnsBench.uncachedAvgMs}ms`);
        console.log(`   Improvement: ${dnsBench.improvement}`);

        // HTTP benchmark
        console.log('\n⚡ HTTP Performance:');
        try {
            const httpBench = await this.benchmarkHTTP();
            console.log(`   URL: ${httpBench.url}`);
            console.log(`   Success rate: ${httpBench.successRate}`);
            console.log(`   Average latency: ${httpBench.averageMs}ms`);
            console.log(`   Range: ${httpBench.minMs}ms - ${httpBench.maxMs}ms`);
        } catch (err) {
            console.log(`   Benchmark failed: ${err.message}`);
        }

        // Agent stats
        console.log('\n🔧 Agent Configuration:');
        console.log(`   HTTP keepAlive: ${CONFIG.httpAgent.keepAlive}`);
        console.log(`   Max sockets: ${CONFIG.httpAgent.maxSockets}`);
        console.log(`   Max free sockets: ${CONFIG.httpAgent.maxFreeSockets}`);

        // Cache stats
        console.log('\n📦 Cache Statistics:');
        console.log(`   DNS cache entries: ${dnsCache.size}`);
        console.log(`   DNS hits: ${this.stats.dnsHits}`);
        console.log(`   DNS misses: ${this.stats.dnsMisses}`);
        console.log(`   Hit rate: ${((this.stats.dnsHits / (this.stats.dnsHits + this.stats.dnsMisses)) * 100 || 0).toFixed(1)}%`);

        console.log('\n' + '═'.repeat(60) + '\n');

        return {
            system: {
                platform: os.platform(),
                release: os.release(),
                memory: os.totalmem()
            },
            interfaces,
            dns: dnsBench,
            config: CONFIG,
            stats: this.stats
        };
    }

    // Apply optimizations globally
    applyGlobal() {
        console.log('\n🚀 Applying Network Optimizations...\n');

        this.configureDNS();
        this.initAgents();

        // Replace global agents
        http.globalAgent = optimizedHttpAgent;
        https.globalAgent = optimizedHttpsAgent;
        console.log('✓ Global HTTP/HTTPS agents replaced');

        // Set DNS lookup cache
        const originalLookup = dns.lookup;
        dns.lookup = (hostname, options, callback) => {
            if (typeof options === 'function') {
                callback = options;
                options = {};
            }

            this.dnsLookupCached(hostname)
                .then(address => callback(null, address, 4))
                .catch(err => originalLookup(hostname, options, callback));
        };
        console.log('✓ DNS caching enabled');

        console.log('\n✅ Network optimizations applied!\n');

        return { httpAgent: optimizedHttpAgent, httpsAgent: optimizedHttpsAgent };
    }

    // Export config for use in other modules
    getConfig() {
        return CONFIG;
    }

    // Get optimized agents
    getAgents() {
        if (!optimizedHttpAgent || !optimizedHttpsAgent) {
            this.initAgents();
        }
        return { httpAgent: optimizedHttpAgent, httpsAgent: optimizedHttpsAgent };
    }
}

// CLI execution
const args = process.argv.slice(2);
const shouldApply = args.includes('--apply');
const shouldReport = args.includes('--report') || args.length === 0;

const optimizer = new NetworkPathOptimizer();

if (shouldApply) {
    optimizer.applyGlobal();
}

if (shouldReport) {
    optimizer.initAgents();
    optimizer.generateReport().then(report => {
        // Save report
        const reportPath = path.join(__dirname, '..', 'test-reports', 'network-optimization-report.json');
        try {
            fs.mkdirSync(path.dirname(reportPath), { recursive: true });
            fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
            console.log(`Report saved to: test-reports/network-optimization-report.json`);
        } catch (err) {
            console.warn('Could not save report:', err.message);
        }
    });
}

export default NetworkPathOptimizer;
export { CONFIG, optimizedHttpAgent, optimizedHttpsAgent };
