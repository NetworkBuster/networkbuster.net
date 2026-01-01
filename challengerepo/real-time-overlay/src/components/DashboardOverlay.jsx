import { useState, useEffect, useRef } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, 
         ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid, RadarChart, 
         Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import { Activity, Cpu, Database, Globe, Server, Wifi, Zap, TrendingUp, 
         Users, Shield, Clock, HardDrive } from 'lucide-react';

// Animated metric card with glow effect
function MetricCard({ icon: Icon, label, value, trend, color, unit = '' }) {
    const [displayValue, setDisplayValue] = useState(0);
    
    useEffect(() => {
        const timer = setInterval(() => {
            setDisplayValue(prev => {
                const diff = value - prev;
                return prev + diff * 0.1;
            });
        }, 50);
        return () => clearInterval(timer);
    }, [value]);
    
    return (
        <div className="relative group">
            <div className={`absolute inset-0 bg-gradient-to-r ${color} opacity-20 blur-xl group-hover:opacity-40 transition-opacity rounded-xl`} />
            <div className="relative bg-black/60 backdrop-blur-sm border border-white/10 rounded-xl p-4 hover:border-white/30 transition-all">
                <div className="flex items-center justify-between mb-2">
                    <Icon size={20} className="text-white/60" />
                    {trend && (
                        <span className={`text-xs ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
                        </span>
                    )}
                </div>
                <div className="text-2xl font-bold text-white mb-1">
                    {displayValue.toFixed(1)}{unit}
                </div>
                <div className="text-xs text-white/50 uppercase tracking-wider">{label}</div>
            </div>
        </div>
    );
}

// Real-time line chart with gradient
function LiveChart({ data, dataKey, color, title }) {
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-bold text-white/80 mb-3 flex items-center gap-2">
                <Activity size={14} className={`text-[${color}]`} />
                {title}
            </h3>
            <ResponsiveContainer width="100%" height={120}>
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                            <stop offset="100%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="time" tick={false} stroke="#444" />
                    <YAxis tick={{ fontSize: 10, fill: '#666' }} stroke="#444" />
                    <Tooltip 
                        contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 8 }}
                        itemStyle={{ color: color }}
                    />
                    <Area 
                        type="monotone" 
                        dataKey={dataKey} 
                        stroke={color} 
                        strokeWidth={2}
                        fill={`url(#gradient-${dataKey})`}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}

// Radar chart for system health
function SystemRadar({ data }) {
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-bold text-white/80 mb-3 flex items-center gap-2">
                <Shield size={14} className="text-[#00f0ff]" />
                SYSTEM HEALTH
            </h3>
            <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={data}>
                    <PolarGrid stroke="#333" />
                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10, fill: '#888' }} />
                    <PolarRadiusAxis tick={{ fontSize: 8, fill: '#666' }} />
                    <Radar 
                        name="Current" 
                        dataKey="value" 
                        stroke="#00f0ff" 
                        fill="#00f0ff" 
                        fillOpacity={0.3} 
                    />
                    <Radar 
                        name="Optimal" 
                        dataKey="optimal" 
                        stroke="#00ff88" 
                        fill="#00ff88" 
                        fillOpacity={0.1} 
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}

// Traffic distribution pie chart
function TrafficPie({ data }) {
    const COLORS = ['#00f0ff', '#ff003c', '#00ff88', '#ff9500', '#667eea'];
    
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-bold text-white/80 mb-3 flex items-center gap-2">
                <Globe size={14} className="text-[#ff003c]" />
                TRAFFIC DISTRIBUTION
            </h3>
            <ResponsiveContainer width="100%" height={150}>
                <PieChart>
                    <Pie
                        data={data}
                        innerRadius={40}
                        outerRadius={60}
                        paddingAngle={2}
                        dataKey="value"
                    >
                        {data.map((entry, index) => (
                            <Cell key={index} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip 
                        contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 8 }}
                    />
                </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap gap-2 justify-center mt-2">
                {data.map((item, i) => (
                    <span key={i} className="text-[10px] text-white/60 flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full" style={{ background: COLORS[i] }} />
                        {item.name}
                    </span>
                ))}
            </div>
        </div>
    );
}

// Server status grid
function ServerGrid({ servers }) {
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-bold text-white/80 mb-3 flex items-center gap-2">
                <Server size={14} className="text-[#00ff88]" />
                SERVER CLUSTER
            </h3>
            <div className="grid grid-cols-4 gap-2">
                {servers.map((server, i) => (
                    <div 
                        key={i}
                        className={`aspect-square rounded-lg flex flex-col items-center justify-center text-[10px] border ${
                            server.status === 'online' 
                                ? 'bg-green-500/20 border-green-500/50 text-green-400' 
                                : server.status === 'warning'
                                ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400'
                                : 'bg-red-500/20 border-red-500/50 text-red-400'
                        }`}
                    >
                        <HardDrive size={16} />
                        <span className="mt-1">{server.name}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Activity feed
function ActivityFeed({ activities }) {
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4 h-full">
            <h3 className="text-sm font-bold text-white/80 mb-3 flex items-center gap-2">
                <Clock size={14} className="text-[#667eea]" />
                LIVE ACTIVITY
            </h3>
            <div className="space-y-2 overflow-y-auto max-h-[200px] custom-scrollbar">
                {activities.map((activity, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs p-2 bg-white/5 rounded-lg">
                        <span className={`w-2 h-2 rounded-full mt-1 ${
                            activity.type === 'success' ? 'bg-green-400' :
                            activity.type === 'warning' ? 'bg-yellow-400' :
                            activity.type === 'error' ? 'bg-red-400' : 'bg-blue-400'
                        }`} />
                        <div>
                            <div className="text-white/80">{activity.message}</div>
                            <div className="text-white/40 text-[10px]">{activity.time}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function DashboardOverlay() {
    const [metrics, setMetrics] = useState({
        cpu: 45, memory: 62, network: 78, disk: 34,
        requests: 1247, users: 89, uptime: 99.9
    });
    
    const [chartData, setChartData] = useState([]);
    const [radarData] = useState([
        { metric: 'CPU', value: 85, optimal: 95 },
        { metric: 'Memory', value: 72, optimal: 90 },
        { metric: 'Network', value: 91, optimal: 95 },
        { metric: 'Storage', value: 68, optimal: 85 },
        { metric: 'Security', value: 95, optimal: 100 },
    ]);
    
    const [trafficData] = useState([
        { name: 'API', value: 40 },
        { name: 'Web', value: 30 },
        { name: 'CDN', value: 20 },
        { name: 'Other', value: 10 },
    ]);
    
    const [servers] = useState([
        { name: 'US-E1', status: 'online' },
        { name: 'US-W1', status: 'online' },
        { name: 'EU-1', status: 'warning' },
        { name: 'EU-2', status: 'online' },
        { name: 'AP-1', status: 'online' },
        { name: 'AP-2', status: 'online' },
        { name: 'SA-1', status: 'offline' },
        { name: 'AF-1', status: 'online' },
    ]);
    
    const [activities, setActivities] = useState([
        { type: 'success', message: 'Deployment completed successfully', time: '2s ago' },
        { type: 'info', message: 'New user registered', time: '15s ago' },
        { type: 'warning', message: 'High memory usage on EU-1', time: '1m ago' },
        { type: 'success', message: 'Database backup completed', time: '5m ago' },
        { type: 'error', message: 'SA-1 server unreachable', time: '10m ago' },
    ]);
    
    // Update metrics in real-time
    useEffect(() => {
        const interval = setInterval(() => {
            setMetrics(prev => ({
                cpu: Math.max(20, Math.min(95, prev.cpu + (Math.random() - 0.5) * 10)),
                memory: Math.max(30, Math.min(90, prev.memory + (Math.random() - 0.5) * 5)),
                network: Math.max(40, Math.min(99, prev.network + (Math.random() - 0.5) * 8)),
                disk: Math.max(20, Math.min(80, prev.disk + (Math.random() - 0.5) * 2)),
                requests: Math.floor(prev.requests + (Math.random() - 0.3) * 50),
                users: Math.max(50, Math.min(150, prev.users + Math.floor((Math.random() - 0.5) * 5))),
                uptime: 99.9
            }));
            
            setChartData(prev => {
                const newData = [...prev, {
                    time: new Date().toLocaleTimeString(),
                    cpu: metrics.cpu,
                    memory: metrics.memory,
                    network: metrics.network
                }];
                return newData.slice(-20);
            });
        }, 1000);
        
        return () => clearInterval(interval);
    }, [metrics]);
    
    return (
        <div className="w-full h-full p-4 overflow-auto custom-scrollbar">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00f0ff] to-[#667eea] flex items-center justify-center">
                            <Zap size={20} className="text-black" />
                        </div>
                        SYSTEM DASHBOARD
                    </h1>
                    <p className="text-white/50 text-sm mt-1">Real-time infrastructure monitoring</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <div className="text-xs text-white/50">Last updated</div>
                        <div className="text-sm text-[#00f0ff]">{new Date().toLocaleTimeString()}</div>
                    </div>
                    <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                </div>
            </div>
            
            {/* Metrics Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <MetricCard icon={Cpu} label="CPU Usage" value={metrics.cpu} trend={2.3} color="from-[#00f0ff] to-[#0099ff]" unit="%" />
                <MetricCard icon={Database} label="Memory" value={metrics.memory} trend={-1.2} color="from-[#ff003c] to-[#ff6b6b]" unit="%" />
                <MetricCard icon={Wifi} label="Network" value={metrics.network} trend={5.7} color="from-[#00ff88] to-[#00cc6a]" unit="%" />
                <MetricCard icon={TrendingUp} label="Requests/s" value={metrics.requests} trend={12.4} color="from-[#667eea] to-[#764ba2]" />
            </div>
            
            {/* Charts Row */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <LiveChart data={chartData} dataKey="cpu" color="#00f0ff" title="CPU LOAD" />
                <LiveChart data={chartData} dataKey="memory" color="#ff003c" title="MEMORY USAGE" />
                <LiveChart data={chartData} dataKey="network" color="#00ff88" title="NETWORK I/O" />
            </div>
            
            {/* Bottom Grid */}
            <div className="grid grid-cols-4 gap-4">
                <SystemRadar data={radarData} />
                <TrafficPie data={trafficData} />
                <ServerGrid servers={servers} />
                <ActivityFeed activities={activities} />
            </div>
        </div>
    );
}
