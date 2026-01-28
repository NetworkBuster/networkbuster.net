/**
 * GPU Stats API - Endpoint for Linux GPU monitoring
 * Supports NVIDIA (nvidia-smi), AMD (rocm-smi), and Intel GPUs
 * 
 * GET /api/gpu/stats - Returns GPU statistics
 */

import express from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const router = express.Router();

// Cache for GPU stats
let gpuCache = {
    data: null,
    timestamp: 0,
    ttl: 1000 // 1 second cache
};

// Parse NVIDIA GPU stats from nvidia-smi
async function getNvidiaStats() {
    try {
        const { stdout } = await execAsync(
            'nvidia-smi --query-gpu=index,name,utilization.gpu,memory.total,memory.used,temperature.gpu,power.draw,fan.speed,clocks.gr,clocks.mem --format=csv,noheader,nounits'
        );

        return stdout.trim().split('\n').map(line => {
            const [index, name, utilization, memoryTotal, memoryUsed, temperature, powerDraw, fanSpeed, clockCore, clockMemory] = line.split(', ');
            return {
                id: parseInt(index),
                name: name?.trim() || 'NVIDIA GPU',
                vendor: 'nvidia',
                utilization: parseInt(utilization) || 0,
                memoryTotal: parseInt(memoryTotal) || 0,
                memoryUsed: parseInt(memoryUsed) || 0,
                temperature: parseInt(temperature) || 0,
                powerDraw: Math.round(parseFloat(powerDraw) || 0),
                fanSpeed: parseInt(fanSpeed) || 0,
                clockCore: parseInt(clockCore) || 0,
                clockMemory: parseInt(clockMemory) || 0
            };
        });
    } catch (err) {
        return null;
    }
}

// Parse AMD GPU stats from rocm-smi
async function getAmdStats() {
    try {
        const { stdout } = await execAsync('rocm-smi --showuse --showtemp --showpower --showfan --showclocks --json');
        const data = JSON.parse(stdout);

        return Object.entries(data).map(([id, gpu]) => ({
            id: parseInt(id.replace('card', '')),
            name: gpu['Card Series'] || 'AMD GPU',
            vendor: 'amd',
            utilization: parseInt(gpu['GPU use (%)']) || 0,
            memoryTotal: parseInt(gpu['VRAM Total Memory (B)'] / 1024 / 1024) || 0,
            memoryUsed: parseInt(gpu['VRAM Total Used Memory (B)'] / 1024 / 1024) || 0,
            temperature: parseInt(gpu['Temperature (Sensor edge) (C)']) || 0,
            powerDraw: parseInt(gpu['Average Graphics Package Power (W)']) || 0,
            fanSpeed: parseInt(gpu['Fan speed (%)']) || 0,
            clockCore: parseInt(gpu['sclk clock speed:']?.replace(/[^0-9]/g, '')) || 0,
            clockMemory: parseInt(gpu['mclk clock speed:']?.replace(/[^0-9]/g, '')) || 0
        }));
    } catch (err) {
        return null;
    }
}

// Parse Intel GPU stats (basic via sysfs or intel_gpu_top)
async function getIntelStats() {
    try {
        // Try intel_gpu_top with JSON output
        const { stdout } = await execAsync('timeout 1 intel_gpu_top -J 2>/dev/null || echo "{}"');
        const data = JSON.parse(stdout);

        if (data.engines) {
            const render = data.engines?.['Render/3D'] || {};
            return [{
                id: 0,
                name: 'Intel Integrated Graphics',
                vendor: 'intel',
                utilization: Math.round(render.busy || 0),
                memoryTotal: 0,
                memoryUsed: 0,
                temperature: 0,
                powerDraw: Math.round(data.power?.GPU || 0),
                fanSpeed: 0,
                clockCore: Math.round(data.frequency?.actual || 0),
                clockMemory: 0
            }];
        }
        return null;
    } catch (err) {
        return null;
    }
}

// Get GPU stats from any available source
async function getGpuStats() {
    // Check cache
    if (gpuCache.data && Date.now() - gpuCache.timestamp < gpuCache.ttl) {
        return gpuCache.data;
    }

    // Try each vendor
    let gpus = await getNvidiaStats();
    if (!gpus) gpus = await getAmdStats();
    if (!gpus) gpus = await getIntelStats();
    if (!gpus) gpus = [];

    const result = {
        gpus,
        timestamp: new Date().toISOString(),
        platform: process.platform,
        hostname: process.env.HOSTNAME || 'unknown'
    };

    // Update cache
    gpuCache = {
        data: result,
        timestamp: Date.now(),
        ttl: 1000
    };

    return result;
}

// GET /api/gpu/stats
router.get('/stats', async (req, res) => {
    try {
        const stats = await getGpuStats();
        res.json(stats);
    } catch (err) {
        res.status(500).json({
            error: 'Failed to get GPU stats',
            message: err.message,
            gpus: [],
            timestamp: new Date().toISOString()
        });
    }
});

// GET /api/gpu/health
router.get('/health', async (req, res) => {
    const stats = await getGpuStats();
    const hasGpu = stats.gpus.length > 0;

    res.json({
        status: hasGpu ? 'ok' : 'no-gpu',
        gpuCount: stats.gpus.length,
        vendors: [...new Set(stats.gpus.map(g => g.vendor))],
        timestamp: new Date().toISOString()
    });
});

// GET /api/gpu/simulate - For testing without real GPU
router.get('/simulate', (req, res) => {
    const simulatedGpus = [
        {
            id: 0,
            name: 'NVIDIA RTX 4090 (Simulated)',
            vendor: 'nvidia',
            utilization: Math.round(40 + Math.random() * 40),
            memoryTotal: 24576,
            memoryUsed: Math.round(8000 + Math.random() * 8000),
            temperature: Math.round(55 + Math.random() * 20),
            powerDraw: Math.round(150 + Math.random() * 200),
            fanSpeed: Math.round(30 + Math.random() * 40),
            clockCore: Math.round(1800 + Math.random() * 500),
            clockMemory: Math.round(9000 + Math.random() * 1000)
        },
        {
            id: 1,
            name: 'AMD RX 7900 XTX (Simulated)',
            vendor: 'amd',
            utilization: Math.round(30 + Math.random() * 50),
            memoryTotal: 24576,
            memoryUsed: Math.round(6000 + Math.random() * 10000),
            temperature: Math.round(50 + Math.random() * 25),
            powerDraw: Math.round(120 + Math.random() * 180),
            fanSpeed: Math.round(25 + Math.random() * 45),
            clockCore: Math.round(2000 + Math.random() * 400),
            clockMemory: Math.round(9500 + Math.random() * 500)
        }
    ];

    res.json({
        gpus: simulatedGpus,
        timestamp: new Date().toISOString(),
        simulated: true
    });
});

export default router;
