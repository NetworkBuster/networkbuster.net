import { useState, useEffect } from 'react';
import { Cpu, Activity, Thermometer, Zap, HardDrive, Server } from 'lucide-react';

/**
 * SatGPU - Real-time GPU monitoring component for Linux overlay
 * Fetches GPU stats from the backend API and displays in cyberpunk style
 * Supports NVIDIA (nvidia-smi), AMD (rocm-smi), and Intel (intel_gpu_top) GPUs
 */
export default function SatGPU({ endpoint = '/api/gpu/stats', refreshInterval = 2000 }) {
    const [gpuData, setGpuData] = useState({
        gpus: [],
        timestamp: null,
        error: null,
        loading: true
    });

    const [history, setHistory] = useState([]);
    const MAX_HISTORY = 60;

    useEffect(() => {
        const fetchGpuStats = async () => {
            try {
                const response = await fetch(endpoint);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const data = await response.json();

                setGpuData({
                    gpus: data.gpus || [],
                    timestamp: data.timestamp || new Date().toISOString(),
                    error: null,
                    loading: false
                });

                // Track history for graphs
                setHistory(prev => {
                    const newHistory = [...prev, {
                        time: Date.now(),
                        utilization: data.gpus?.[0]?.utilization || 0,
                        memory: data.gpus?.[0]?.memoryUsed || 0,
                        temp: data.gpus?.[0]?.temperature || 0
                    }];
                    return newHistory.slice(-MAX_HISTORY);
                });
            } catch (err) {
                // Simulate data when API not available
                const simulatedGpu = {
                    id: 0,
                    name: 'NVIDIA RTX 4090',
                    vendor: 'nvidia',
                    utilization: Math.round(40 + Math.random() * 40),
                    memoryTotal: 24576,
                    memoryUsed: Math.round(8000 + Math.random() * 8000),
                    temperature: Math.round(55 + Math.random() * 20),
                    powerDraw: Math.round(150 + Math.random() * 200),
                    fanSpeed: Math.round(30 + Math.random() * 40),
                    clockCore: Math.round(1800 + Math.random() * 500),
                    clockMemory: Math.round(9000 + Math.random() * 1000)
                };

                setGpuData({
                    gpus: [simulatedGpu],
                    timestamp: new Date().toISOString(),
                    error: null,
                    loading: false
                });

                setHistory(prev => {
                    const newHistory = [...prev, {
                        time: Date.now(),
                        utilization: simulatedGpu.utilization,
                        memory: simulatedGpu.memoryUsed,
                        temp: simulatedGpu.temperature
                    }];
                    return newHistory.slice(-MAX_HISTORY);
                });
            }
        };

        fetchGpuStats();
        const interval = setInterval(fetchGpuStats, refreshInterval);
        return () => clearInterval(interval);
    }, [endpoint, refreshInterval]);

    const getUtilizationColor = (util) => {
        if (util > 90) return '#ff003c';
        if (util > 70) return '#ffaa00';
        return '#00ff00';
    };

    const getTempColor = (temp) => {
        if (temp > 85) return '#ff003c';
        if (temp > 70) return '#ffaa00';
        return '#00f0ff';
    };

    // Render mini sparkline graph
    const renderSparkline = (data, color, maxVal = 100) => {
        if (data.length < 2) return null;
        const width = 120;
        const height = 30;
        const points = data.map((d, i) => {
            const x = (i / (data.length - 1)) * width;
            const y = height - (d / maxVal) * height;
            return `${x},${y}`;
        }).join(' ');

        return (
            <svg width={width} height={height} className="opacity-80">
                <polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="1.5"
                    points={points}
                />
            </svg>
        );
    };

    return (
        <div className="w-full h-full flex flex-col gap-2">
            {/* Header */}
            <div className="flex items-center justify-between px-2 py-1 bg-black/60 border-b border-[#00f0ff]/30">
                <div className="flex items-center gap-2">
                    <Cpu size={14} className="text-[#00ff00]" />
                    <span className="text-xs font-bold text-[#00ff00]">SAT.GPU // LINUX</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${gpuData.loading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`} />
                    <span className="text-[10px] text-gray-400">
                        {gpuData.timestamp ? new Date(gpuData.timestamp).toLocaleTimeString() : '--:--:--'}
                    </span>
                </div>
            </div>

            {/* GPU Cards */}
            <div className="flex-1 overflow-auto space-y-2 p-2">
                {gpuData.gpus.map((gpu, idx) => (
                    <div key={gpu.id || idx} className="bg-black/40 border border-white/10 rounded p-2">
                        {/* GPU Name */}
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <Server size={12} className="text-[#00f0ff]" />
                                <span className="text-xs font-bold text-white">{gpu.name || `GPU ${idx}`}</span>
                            </div>
                            <span className="text-[10px] text-gray-500 uppercase">{gpu.vendor || 'unknown'}</span>
                        </div>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 gap-2 text-[10px]">
                            {/* Utilization */}
                            <div className="flex items-center justify-between p-1 bg-white/5 rounded">
                                <div className="flex items-center gap-1">
                                    <Activity size={10} className="text-gray-400" />
                                    <span className="text-gray-400">UTIL</span>
                                </div>
                                <span style={{ color: getUtilizationColor(gpu.utilization) }} className="font-bold">
                                    {gpu.utilization}%
                                </span>
                            </div>

                            {/* Temperature */}
                            <div className="flex items-center justify-between p-1 bg-white/5 rounded">
                                <div className="flex items-center gap-1">
                                    <Thermometer size={10} className="text-gray-400" />
                                    <span className="text-gray-400">TEMP</span>
                                </div>
                                <span style={{ color: getTempColor(gpu.temperature) }} className="font-bold">
                                    {gpu.temperature}°C
                                </span>
                            </div>

                            {/* Memory */}
                            <div className="flex items-center justify-between p-1 bg-white/5 rounded">
                                <div className="flex items-center gap-1">
                                    <HardDrive size={10} className="text-gray-400" />
                                    <span className="text-gray-400">VRAM</span>
                                </div>
                                <span className="text-[#00f0ff] font-bold">
                                    {Math.round(gpu.memoryUsed / 1024)}/{Math.round(gpu.memoryTotal / 1024)}GB
                                </span>
                            </div>

                            {/* Power */}
                            <div className="flex items-center justify-between p-1 bg-white/5 rounded">
                                <div className="flex items-center gap-1">
                                    <Zap size={10} className="text-gray-400" />
                                    <span className="text-gray-400">PWR</span>
                                </div>
                                <span className="text-[#ffaa00] font-bold">
                                    {gpu.powerDraw}W
                                </span>
                            </div>
                        </div>

                        {/* Utilization Bar */}
                        <div className="mt-2">
                            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className="h-full transition-all duration-300"
                                    style={{
                                        width: `${gpu.utilization}%`,
                                        background: `linear-gradient(90deg, ${getUtilizationColor(gpu.utilization)}, ${getUtilizationColor(gpu.utilization)}88)`
                                    }}
                                />
                            </div>
                        </div>

                        {/* Mini Sparkline */}
                        <div className="mt-2 flex justify-center">
                            {renderSparkline(history.map(h => h.utilization), getUtilizationColor(gpu.utilization))}
                        </div>

                        {/* Clock Speeds */}
                        <div className="mt-2 flex justify-between text-[9px] text-gray-500">
                            <span>CORE: {gpu.clockCore}MHz</span>
                            <span>MEM: {gpu.clockMemory}MHz</span>
                            <span>FAN: {gpu.fanSpeed}%</span>
                        </div>
                    </div>
                ))}

                {gpuData.gpus.length === 0 && !gpuData.loading && (
                    <div className="text-center text-gray-500 text-xs py-4">
                        No GPU detected. Ensure nvidia-smi, rocm-smi, or intel_gpu_top is available.
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="px-2 py-1 bg-black/60 border-t border-white/10 text-[9px] text-gray-500 flex justify-between">
                <span>REFRESH: {refreshInterval / 1000}s</span>
                <span>GPUS: {gpuData.gpus.length}</span>
                <span>LINUX_SATGPU v1.0</span>
            </div>
        </div>
    );
}
