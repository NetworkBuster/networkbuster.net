import { useState } from 'react';
import { Lock, Mail, User, Eye, EyeOff, Shield, Github, Chrome, Key, Fingerprint, Smartphone } from 'lucide-react';

// Input Field Component
const InputField = ({ icon: Icon, type, placeholder, value, onChange }) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  
  return (
    <div className="relative">
      <Icon size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
      <input
        type={isPassword && showPassword ? 'text' : type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full pl-12 pr-12 py-3 bg-black/30 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition"
      />
      {isPassword && (
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-purple-400 transition"
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      )}
    </div>
  );
};

// Social Button
const SocialButton = ({ icon: Icon, label, color }) => (
  <button className={`flex-1 p-3 rounded-xl border border-white/10 bg-white/5 hover:bg-${color}-500/20 hover:border-${color}-500/50 transition flex items-center justify-center gap-2`}>
    <Icon size={20} />
    <span className="text-sm">{label}</span>
  </button>
);

// 2FA Code Input
const TwoFactorInput = ({ value, onChange, index }) => (
  <input
    type="text"
    maxLength={1}
    value={value}
    onChange={(e) => onChange(index, e.target.value)}
    className="w-12 h-14 text-center text-2xl font-bold bg-black/30 border-2 border-white/10 rounded-xl text-white focus:outline-none focus:border-purple-500 transition"
  />
);

export default function AuthPortalOverlay() {
  const [mode, setMode] = useState('login'); // login, register, 2fa
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [twoFactorCode, setTwoFactorCode] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const handleSubmit = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      if (mode === 'login') setMode('2fa');
    }, 1500);
  };

  const handleTwoFactorChange = (index, value) => {
    const newCode = [...twoFactorCode];
    newCode[index] = value;
    setTwoFactorCode(newCode);
    
    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.querySelector(`input[data-index="${index + 1}"]`);
      nextInput?.focus();
    }
  };

  return (
    <div className="p-6 h-full overflow-auto flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-purple-500/30">
            <Lock size={40} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            NetworkBuster
          </h1>
          <p className="text-gray-400 text-sm mt-1">Secure Authentication Portal</p>
        </div>

        {/* Auth Card */}
        <div className="bg-white/5 rounded-2xl border border-purple-500/30 p-6 backdrop-blur">
          {/* Tab Switcher */}
          {mode !== '2fa' && (
            <div className="flex bg-black/30 rounded-xl p-1 mb-6">
              <button
                onClick={() => setMode('login')}
                className={`flex-1 py-2 px-4 rounded-lg transition font-medium ${
                  mode === 'login' 
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setMode('register')}
                className={`flex-1 py-2 px-4 rounded-lg transition font-medium ${
                  mode === 'register' 
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Register
              </button>
            </div>
          )}

          {/* Login Form */}
          {mode === 'login' && (
            <div className="space-y-4">
              <InputField 
                icon={Mail} 
                type="email" 
                placeholder="Email address" 
                value={email} 
                onChange={setEmail} 
              />
              <InputField 
                icon={Lock} 
                type="password" 
                placeholder="Password" 
                value={password} 
                onChange={setPassword} 
              />
              
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="accent-purple-500"
                  />
                  <span className="text-gray-400">Remember me</span>
                </label>
                <button className="text-purple-400 hover:text-pink-400 transition">
                  Forgot password?
                </button>
              </div>
              
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold text-white hover:opacity-90 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Sign In <Key size={18} /></>
                )}
              </button>
            </div>
          )}

          {/* Register Form */}
          {mode === 'register' && (
            <div className="space-y-4">
              <InputField 
                icon={User} 
                type="text" 
                placeholder="Full name" 
                value={name} 
                onChange={setName} 
              />
              <InputField 
                icon={Mail} 
                type="email" 
                placeholder="Email address" 
                value={email} 
                onChange={setEmail} 
              />
              <InputField 
                icon={Lock} 
                type="password" 
                placeholder="Password" 
                value={password} 
                onChange={setPassword} 
              />
              <InputField 
                icon={Lock} 
                type="password" 
                placeholder="Confirm password" 
                value={confirmPassword} 
                onChange={setConfirmPassword} 
              />
              
              <label className="flex items-start gap-2 text-sm text-gray-400 cursor-pointer">
                <input type="checkbox" className="accent-purple-500 mt-1" />
                <span>I agree to the <span className="text-purple-400">Terms of Service</span> and <span className="text-purple-400">Privacy Policy</span></span>
              </label>
              
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold text-white hover:opacity-90 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Create Account <User size={18} /></>
                )}
              </button>
            </div>
          )}

          {/* 2FA Form */}
          {mode === '2fa' && (
            <div className="space-y-6 text-center">
              <div className="w-16 h-16 mx-auto bg-purple-500/20 rounded-2xl flex items-center justify-center">
                <Smartphone size={32} className="text-purple-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white mb-2">Two-Factor Authentication</h2>
                <p className="text-gray-400 text-sm">Enter the 6-digit code from your authenticator app</p>
              </div>
              
              <div className="flex justify-center gap-2">
                {twoFactorCode.map((digit, i) => (
                  <input
                    key={i}
                    type="text"
                    maxLength={1}
                    value={digit}
                    data-index={i}
                    onChange={(e) => handleTwoFactorChange(i, e.target.value)}
                    className="w-12 h-14 text-center text-2xl font-bold bg-black/30 border-2 border-white/10 rounded-xl text-white focus:outline-none focus:border-purple-500 transition"
                  />
                ))}
              </div>
              
              <button
                onClick={() => setMode('login')}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold text-white hover:opacity-90 transition"
              >
                Verify Code
              </button>
              
              <button 
                onClick={() => setMode('login')}
                className="text-gray-400 hover:text-purple-400 transition text-sm"
              >
                ← Back to login
              </button>
            </div>
          )}

          {/* Divider */}
          {mode !== '2fa' && (
            <>
              <div className="flex items-center gap-4 my-6">
                <div className="flex-1 h-px bg-white/10" />
                <span className="text-gray-500 text-sm">or continue with</span>
                <div className="flex-1 h-px bg-white/10" />
              </div>

              {/* Social Login */}
              <div className="flex gap-3">
                <SocialButton icon={Chrome} label="Google" color="red" />
                <SocialButton icon={Github} label="GitHub" color="gray" />
                <SocialButton icon={Fingerprint} label="Biometric" color="purple" />
              </div>
            </>
          )}
        </div>

        {/* Security Badge */}
        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
          <Shield size={16} className="text-green-400" />
          <span>256-bit SSL Encrypted • GDPR Compliant</span>
        </div>
      </div>
    </div>
  );
}
