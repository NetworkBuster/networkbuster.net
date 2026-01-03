import { useState, useEffect, useRef } from 'react';
import { Brain, Zap, MessageSquare, Image, Mic, FileText, Search, Sparkles } from 'lucide-react';

// Neural Network Visualization
const NeuralNetwork = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationId;
    
    const neurons = [];
    for (let i = 0; i < 40; i++) {
      neurons.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 3 + 2
      });
    }
    
    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw connections
      neurons.forEach((n1, i) => {
        neurons.slice(i + 1).forEach(n2 => {
          const dist = Math.hypot(n1.x - n2.x, n1.y - n2.y);
          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.strokeStyle = `rgba(139, 92, 246, ${1 - dist / 100})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        });
      });
      
      // Draw and update neurons
      neurons.forEach(n => {
        n.x += n.vx;
        n.y += n.vy;
        
        if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
        if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
        
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#8b5cf6';
        ctx.fill();
        
        // Glow effect
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius * 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(139, 92, 246, 0.2)';
        ctx.fill();
      });
      
      animationId = requestAnimationFrame(animate);
    };
    
    animate();
    return () => cancelAnimationFrame(animationId);
  }, []);
  
  return <canvas ref={canvasRef} width={400} height={200} className="w-full h-48 rounded-lg" />;
};

// Model Card Component
const ModelCard = ({ name, desc, icon: Icon, active, onClick }) => (
  <button
    onClick={onClick}
    className={`p-4 rounded-xl border transition-all text-left ${
      active 
        ? 'bg-gradient-to-br from-purple-500/30 to-pink-500/30 border-purple-500 shadow-lg shadow-purple-500/20' 
        : 'bg-white/5 border-white/10 hover:border-purple-500/50'
    }`}
  >
    <Icon size={24} className={active ? 'text-purple-400' : 'text-gray-400'} />
    <div className="mt-2 font-bold text-white">{name}</div>
    <div className="text-xs text-gray-400">{desc}</div>
  </button>
);

// Chat Message Component
const ChatMessage = ({ role, content }) => (
  <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
    <div className={`max-w-[80%] p-3 rounded-2xl ${
      role === 'user' 
        ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
        : 'bg-white/10 text-gray-200'
    }`}>
      {content}
    </div>
  </div>
);

// Stat Card
const StatCard = ({ label, value, icon: Icon }) => (
  <div className="bg-white/5 rounded-xl p-4 border border-white/10 text-center">
    <Icon size={24} className="mx-auto text-purple-400 mb-2" />
    <div className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
      {value}
    </div>
    <div className="text-xs text-gray-400">{label}</div>
  </div>
);

export default function AIWorldOverlay() {
  const [activeModel, setActiveModel] = useState('gpt4');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '👋 Hello! I\'m NetworkBuster AI. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const models = [
    { id: 'gpt4', name: 'GPT-4 Turbo', desc: 'Most capable', icon: Brain },
    { id: 'gpt35', name: 'GPT-3.5', desc: 'Fast & efficient', icon: Zap },
    { id: 'dalle', name: 'DALL-E 3', desc: 'Image generation', icon: Image },
    { id: 'whisper', name: 'Whisper', desc: 'Speech-to-text', icon: Mic }
  ];

  const sendMessage = () => {
    if (!input.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsTyping(true);
    
    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "I've analyzed your request. Here's what I found...",
        "That's an interesting question! Let me help you with that.",
        "Based on my training, I can provide the following insights...",
        "Processing complete. Here are my recommendations..."
      ];
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: responses[Math.floor(Math.random() * responses.length)]
      }]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="p-6 h-full overflow-auto">
      <div className="grid grid-cols-12 gap-6">
        {/* Stats Row */}
        <div className="col-span-12">
          <div className="grid grid-cols-4 gap-4">
            <StatCard label="Parameters" value="1.2B" icon={Brain} />
            <StatCard label="Accuracy" value="99.7%" icon={Sparkles} />
            <StatCard label="Response Time" value="24ms" icon={Zap} />
            <StatCard label="Queries Today" value="12.4K" icon={MessageSquare} />
          </div>
        </div>

        {/* Neural Network Viz */}
        <div className="col-span-4">
          <div className="bg-white/5 rounded-xl border border-white/10 p-4">
            <h3 className="text-sm font-bold text-purple-400 mb-3 flex items-center gap-2">
              <Brain size={16} />
              NEURAL NETWORK ACTIVITY
            </h3>
            <NeuralNetwork />
          </div>
          
          {/* Model Selection */}
          <div className="mt-4 bg-white/5 rounded-xl border border-white/10 p-4">
            <h3 className="text-sm font-bold text-purple-400 mb-3">SELECT MODEL</h3>
            <div className="grid grid-cols-2 gap-2">
              {models.map(model => (
                <ModelCard
                  key={model.id}
                  {...model}
                  active={activeModel === model.id}
                  onClick={() => setActiveModel(model.id)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="col-span-8">
          <div className="bg-white/5 rounded-xl border border-purple-500/30 h-full flex flex-col">
            <div className="p-4 border-b border-white/10 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Brain size={20} className="text-white" />
              </div>
              <div>
                <div className="font-bold text-white">NetworkBuster AI</div>
                <div className="text-xs text-green-400 flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Online • {models.find(m => m.id === activeModel)?.name}
                </div>
              </div>
            </div>
            
            <div className="flex-1 p-4 space-y-4 overflow-auto min-h-[300px]">
              {messages.map((msg, i) => (
                <ChatMessage key={i} {...msg} />
              ))}
              {isTyping && (
                <div className="flex gap-1 p-3 bg-white/10 rounded-2xl w-fit">
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-white/10">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type your message..."
                  className="flex-1 bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                />
                <button
                  onClick={sendMessage}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold text-white hover:opacity-90 transition flex items-center gap-2"
                >
                  <Sparkles size={18} />
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="col-span-12 grid grid-cols-3 gap-4">
          {[
            { icon: MessageSquare, title: 'Natural Language', desc: 'Chat, summarize, translate' },
            { icon: Image, title: 'Computer Vision', desc: 'Image analysis & OCR' },
            { icon: FileText, title: 'Content Generation', desc: 'Write, code, create' }
          ].map((feature, i) => (
            <div key={i} className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl p-4 border border-purple-500/20">
              <feature.icon size={24} className="text-purple-400 mb-2" />
              <div className="font-bold text-white">{feature.title}</div>
              <div className="text-xs text-gray-400">{feature.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
