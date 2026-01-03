import { useState, useEffect } from 'react';
import { Server, Activity, Cpu, HardDrive, Wifi, RefreshCw, Power, Settings, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

// Server Card Component
const ServerCard = ({ name, port, status, onAction }) => {
  const statusColors = {
    online: 'text-green-400 border-green-400/30 bg-green-400/10',
    offline: 'text-red-400 border-red-400/30 bg-red-400/10',
    warning: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10'
  };

  return (
    <div className={`p-4 rounded-lg border ${statusColors[status]} transition-all hover:scale-[1.02]`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <Server size={20} />
          <div>
            <div className="font-bold">{name}</div>
            <div className="text-xs opacity-60">Port {port}</div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {status === 'online' && <CheckCircle size={16} className="text-green-400" />}
          {status === 'offline' && <XCircle size={16} className="text-red-400" />}
          {status === 'warning' && <AlertTriangle size={16} className="text-yellow-400" />}
        </div>
      </div>
      <div className="flex gap-2">
        <button 
          onClick={() => onAction('restart')}
          className="flex-1 p-2 bg-white/10 rounded text-xs hover:bg-white/20 transition flex items-center justify-center gap-1"
        >
          <RefreshCw size={12} /> Restart
        </button>
        <button 
          onClick={() => onAction('stop')}
          className="flex-1 p-2 bg-red-500/20 rounded text-xs hover:bg-red-500/30 transition flex items-center justify-center gap-1"
        >
          <Power size={12} /> Stop
        </button>
        <button 
          onClick={() => onAction('config')}
          className="p-2 bg-white/10 rounded text-xs hover:bg-white/20 transition"
        >
          <Settings size={12} />
        </button>
      </div>
    </div>
  );
};

// Resource Meter Component
const ResourceMeter = ({ label, value, max = 100, color = '#00f0ff' }) => {
  const percentage = (value / max) * 100;
  const barColor = percentage > 80 ? '#ff003c' : percentage > 60 ? '#fbbf24' : color;
  
  return (
    <div className="mb-4">
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span style={{ color: barColor }}>{value}%</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div 
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%`, background: `linear-gradient(90deg, ${barColor}, ${barColor}88)` }}
        />
      </div>
    </div>
  );
};

// Log Entry Component
const LogEntry = ({ time, level, message }) => {
  const levelColors = {
    info: 'bg-cyan-500/20 text-cyan-400',
    success: 'bg-green-500/20 text-green-400',
    warning: 'bg-yellow-500/20 text-yellow-400',
    error: 'bg-red-500/20 text-red-400'
  };

  return (
    <div className="flex items-start gap-2 p-2 border-b border-white/5 text-xs font-mono">
      <span className="text-gray-500">{time}</span>
      <span className={`px-2 py-0.5 rounded ${levelColors[level]}`}>{level.toUpperCase()}</span>
      <span className="text-gray-300">{message}</span>
    </div>
  );
};

export default function ControlPanelOverlay() {
  const [servers, setServers] = useState([
    { name: 'Web Server', port: 3500, status: 'online' },
    { name: 'Chatbot API', port: 3005, status: 'online' },
    { name: 'Audio Server', port: 3002, status: 'online' },
    { name: 'Overlay Dev', port: 5173, status: 'online' },
    { name: 'Analytics', port: 3010, status: 'offline' },
    { name: 'WebSocket', port: 8080, status: 'warning' }
  ]);

  const [resources, setResources] = useState({
    cpu: 34,
    memory: 67,
    disk: 52,
    network: 28
  });

  const [logs, setLogs] = useState([
    { time: '08:45:23', level: 'info', message: 'System initialized successfully' },
    { time: '08:45:24', level: 'success', message: 'All services started' },
    { time: '08:45:30', level: 'warning', message: 'High memory usage detected' },
    { time: '08:45:35', level: 'error', message: 'Analytics engine connection failed' }
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setResources(prev => ({
        cpu: Math.min(100, Math.max(0, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.min(100, Math.max(0, prev.memory + (Math.random() - 0.5) * 5)),
        disk: prev.disk,
        network: Math.min(100, Math.max(0, prev.network + (Math.random() - 0.5) * 15))
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleServerAction = (serverName, action) => {
    console.log(`${action} on ${serverName}`);
    // Add log entry
    setLogs(prev => [{
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      level: action === 'stop' ? 'warning' : 'info',
      message: `${action.charAt(0).toUpperCase() + action.slice(1)} initiated on ${serverName}`
    }, ...prev].slice(0, 20));
  };

  return (
    <div className="p-6 h-full overflow-auto">
      <div className="grid grid-cols-12 gap-6">
        {/* Server Grid */}
        <div className="col-span-8">
          <div className="mb-4 flex items-center gap-2">
            <Server size={20} className="text-cyan-400" />
            <h3 className="text-lg font-bold text-cyan-400">SERVER MANAGEMENT</h3>
            <span className="ml-auto px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs">
              {servers.filter(s => s.status === 'online').length}/{servers.length} Online
            </span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {servers.map((server, i) => (
              <ServerCard 
                key={i} 
                {...server} 
                onAction={(action) => handleServerAction(server.name, action)}
              />
            ))}
          </div>
        </div>

        {/* Resources Panel */}
        <div className="col-span-4">
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="flex items-center gap-2 mb-4">
              <Cpu size={18} className="text-green-400" />
              <h3 className="font-bold text-green-400">SYSTEM RESOURCES</h3>
            </div>
            <ResourceMeter label="CPU Usage" value={Math.round(resources.cpu)} color="#00f0ff" />
            <ResourceMeter label="Memory" value={Math.round(resources.memory)} color="#8b5cf6" />
            <ResourceMeter label="Disk I/O" value={Math.round(resources.disk)} color="#fbbf24" />
            <ResourceMeter label="Network" value={Math.round(resources.network)} color="#4ade80" />
          </div>

          {/* Quick Actions */}
          <div className="bg-white/5 rounded-lg p-4 border border-white/10 mt-4">
            <h3 className="font-bold text-yellow-400 mb-3 flex items-center gap-2">
              <Activity size={18} />
              QUICK ACTIONS
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { icon: RefreshCw, label: 'Restart All', color: 'cyan' },
                { icon: HardDrive, label: 'Clear Cache', color: 'purple' },
                { icon: Wifi, label: 'Health Check', color: 'green' },
                { icon: Settings, label: 'Settings', color: 'gray' }
              ].map((action, i) => (
                <button 
                  key={i}
                  className={`p-3 bg-${action.color}-500/10 border border-${action.color}-500/30 rounded-lg hover:bg-${action.color}-500/20 transition flex flex-col items-center gap-1`}
                >
                  <action.icon size={20} className={`text-${action.color}-400`} />
                  <span className="text-xs">{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Live Logs */}
        <div className="col-span-12">
          <div className="bg-black/50 rounded-lg border border-white/10">
            <div className="flex items-center justify-between p-3 border-b border-white/10">
              <h3 className="font-bold text-pink-400 flex items-center gap-2">
                <Activity size={18} />
                LIVE SYSTEM LOGS
              </h3>
              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs animate-pulse">
                ● Streaming
              </span>
            </div>
            <div className="max-h-48 overflow-auto">
              {logs.map((log, i) => (
                <LogEntry key={i} {...log} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
