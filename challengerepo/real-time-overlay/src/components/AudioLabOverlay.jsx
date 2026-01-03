import { useState, useEffect, useRef } from 'react';
import { Music, Play, Pause, Square, Circle, Volume2, Sliders, Radio, Upload, List } from 'lucide-react';

// Waveform Visualizer
const WaveformVisualizer = ({ isPlaying }) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationId;
    let offset = 0;
    
    const draw = () => {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.3)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, '#8b5cf6');
      gradient.addColorStop(0.5, '#ec4899');
      gradient.addColorStop(1, '#6366f1');
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      const centerY = canvas.height / 2;
      for (let x = 0; x < canvas.width; x++) {
        const amplitude = isPlaying ? 30 : 5;
        const frequency = isPlaying ? 0.05 : 0.02;
        const y = centerY + Math.sin(x * frequency + offset) * amplitude * Math.sin(x * 0.01);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      
      if (isPlaying) offset += 0.1;
      animationId = requestAnimationFrame(draw);
    };
    
    draw();
    return () => cancelAnimationFrame(animationId);
  }, [isPlaying]);
  
  return <canvas ref={canvasRef} width={600} height={120} className="w-full h-24 rounded-lg bg-black/30" />;
};

// Spectrum Analyzer
const SpectrumAnalyzer = ({ isPlaying }) => {
  const [bars, setBars] = useState(Array(32).fill(20));
  
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setBars(prev => prev.map(() => Math.random() * 100 + 20));
    }, 100);
    
    return () => clearInterval(interval);
  }, [isPlaying]);
  
  return (
    <div className="flex items-end justify-between h-32 gap-1 p-4 bg-black/30 rounded-lg">
      {bars.map((height, i) => (
        <div
          key={i}
          className="flex-1 rounded-t transition-all duration-100"
          style={{
            height: `${isPlaying ? height : 20}%`,
            background: `linear-gradient(180deg, #ec4899, #8b5cf6, #6366f1)`
          }}
        />
      ))}
    </div>
  );
};

// Mixer Channel
const MixerChannel = ({ label, value, onChange }) => (
  <div className="flex flex-col items-center gap-2 p-3 bg-black/20 rounded-lg">
    <span className="text-xs text-gray-400">{label}</span>
    <input
      type="range"
      min="0"
      max="100"
      value={value}
      onChange={(e) => onChange(parseInt(e.target.value))}
      className="h-24 w-6 appearance-none bg-white/10 rounded-full [writing-mode:vertical-lr] [direction:rtl] accent-purple-500"
    />
    <span className="text-xs text-purple-400 font-bold">{value}%</span>
  </div>
);

// Effect Knob
const EffectKnob = ({ label, value }) => (
  <div className="flex flex-col items-center gap-2 p-3 bg-black/20 rounded-lg">
    <div 
      className="w-14 h-14 rounded-full border-4 border-purple-500/30 flex items-center justify-center"
      style={{
        background: `conic-gradient(from 135deg, #8b5cf6 0%, #8b5cf6 ${value}%, rgba(139, 92, 246, 0.2) ${value}%)`
      }}
    >
      <div className="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center">
        <span className="text-xs font-bold text-purple-400">{value}%</span>
      </div>
    </div>
    <span className="text-xs text-gray-400">{label}</span>
  </div>
);

// Playlist Item
const PlaylistItem = ({ title, duration, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 p-3 rounded-lg transition ${
      active ? 'bg-purple-500/20 border-l-2 border-purple-500' : 'bg-black/20 hover:bg-white/5'
    }`}
  >
    <div className={`w-8 h-8 rounded flex items-center justify-center ${
      active ? 'bg-gradient-to-br from-purple-500 to-pink-500' : 'bg-white/10'
    }`}>
      {active ? <Play size={14} className="text-white" /> : <Music size={14} className="text-gray-400" />}
    </div>
    <div className="flex-1 text-left">
      <div className={`text-sm ${active ? 'text-white' : 'text-gray-300'}`}>{title}</div>
      <div className="text-xs text-gray-500">{duration}</div>
    </div>
  </button>
);

export default function AudioLabOverlay() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [activeTrack, setActiveTrack] = useState(0);
  const [mixer, setMixer] = useState({
    master: 80,
    vocals: 70,
    bass: 65,
    drums: 75,
    synth: 60,
    fx: 45
  });

  const tracks = [
    { title: 'Lunar Ambience', duration: '3:42' },
    { title: 'System Startup', duration: '0:08' },
    { title: 'Network Pulse', duration: '2:15' },
    { title: 'Data Stream', duration: '4:20' },
    { title: 'Cyber Dreams', duration: '5:30' }
  ];

  return (
    <div className="p-6 h-full overflow-auto">
      <div className="grid grid-cols-12 gap-6">
        {/* Waveform & Controls */}
        <div className="col-span-8">
          <div className="bg-white/5 rounded-xl border border-purple-500/30 p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Radio size={18} className="text-purple-400" />
                <span className="font-bold text-purple-400">WAVEFORM VISUALIZER</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className={`px-2 py-1 rounded ${isPlaying ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                  {isPlaying ? '● PLAYING' : '○ STOPPED'}
                </span>
                <span className="text-gray-400">44.1kHz / 16-bit / Stereo</span>
              </div>
            </div>
            
            <WaveformVisualizer isPlaying={isPlaying} />
            
            <div className="flex items-center justify-center gap-4 mt-4">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`p-4 rounded-full ${
                  isPlaying ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
                } hover:scale-105 transition`}
              >
                {isPlaying ? <Pause size={24} /> : <Play size={24} />}
              </button>
              <button
                onClick={() => { setIsPlaying(false); }}
                className="p-4 rounded-full bg-red-500/20 text-red-400 hover:scale-105 transition"
              >
                <Square size={24} />
              </button>
              <button
                onClick={() => setIsRecording(!isRecording)}
                className={`p-4 rounded-full ${
                  isRecording ? 'bg-red-500 animate-pulse' : 'bg-red-500/20'
                } text-red-400 hover:scale-105 transition`}
              >
                <Circle size={24} fill={isRecording ? 'currentColor' : 'none'} />
              </button>
            </div>
          </div>
          
          {/* Spectrum Analyzer */}
          <div className="bg-white/5 rounded-xl border border-pink-500/30 p-4 mt-4">
            <div className="flex items-center gap-2 mb-4">
              <Volume2 size={18} className="text-pink-400" />
              <span className="font-bold text-pink-400">SPECTRUM ANALYZER</span>
            </div>
            <SpectrumAnalyzer isPlaying={isPlaying} />
          </div>
        </div>

        {/* Right Panel */}
        <div className="col-span-4 space-y-4">
          {/* Mixer */}
          <div className="bg-white/5 rounded-xl border border-cyan-500/30 p-4">
            <div className="flex items-center gap-2 mb-4">
              <Sliders size={18} className="text-cyan-400" />
              <span className="font-bold text-cyan-400">CHANNEL MIXER</span>
            </div>
            <div className="grid grid-cols-6 gap-1">
              {Object.entries(mixer).map(([key, value]) => (
                <MixerChannel
                  key={key}
                  label={key.charAt(0).toUpperCase() + key.slice(1)}
                  value={value}
                  onChange={(v) => setMixer(prev => ({ ...prev, [key]: v }))}
                />
              ))}
            </div>
          </div>
          
          {/* Effects */}
          <div className="bg-white/5 rounded-xl border border-yellow-500/30 p-4">
            <div className="flex items-center gap-2 mb-4">
              <Music size={18} className="text-yellow-400" />
              <span className="font-bold text-yellow-400">EFFECTS RACK</span>
            </div>
            <div className="grid grid-cols-4 gap-2">
              <EffectKnob label="Reverb" value={42} />
              <EffectKnob label="Delay" value={28} />
              <EffectKnob label="Comp" value={65} />
              <EffectKnob label="EQ" value={15} />
            </div>
          </div>
          
          {/* Playlist */}
          <div className="bg-white/5 rounded-xl border border-green-500/30 p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <List size={18} className="text-green-400" />
                <span className="font-bold text-green-400">PLAYLIST</span>
              </div>
              <button className="p-2 bg-white/10 rounded hover:bg-white/20 transition">
                <Upload size={14} />
              </button>
            </div>
            <div className="space-y-2 max-h-40 overflow-auto">
              {tracks.map((track, i) => (
                <PlaylistItem
                  key={i}
                  {...track}
                  active={activeTrack === i}
                  onClick={() => setActiveTrack(i)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
