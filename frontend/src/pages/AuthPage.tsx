import React, { useState } from 'react';
import { api } from '../services/api';
import { User } from '../types';
import { Lock, Mail, User as UserIcon, Mic, Shield, Sparkles, LogIn } from 'lucide-react';

interface AuthPageProps {
  onSuccess: (user: User) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('ASHA_WORKER');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isRegister) {
        // Register
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: fullName, role }),
        });
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || 'Registration failed');
        }
        const data = await res.json();
        onSuccess(data.user);
      } else {
        // Login
        const data = await api.login(email, password);
        onSuccess(data.user);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication error');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.demoLogin();
      onSuccess(data.user);
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 w-full flex flex-col gap-6">
      <div className="text-center">
        <div className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-[#00f5d4] shadow-[0_0_25px_rgba(0,245,212,0.3)]">
          <Mic className="w-7 h-7" />
        </div>
        <h1 className="text-2xl font-black text-white">ASHA-VAANI Portal Access</h1>
        <p className="text-xs text-slate-300 mt-1">
          Secure healthcare documentation for ASHA Workers & PHC Medical Officers
        </p>
      </div>

      {/* 1-Click Demo Login Box (For Hackathon Review) */}
      <div className="p-5 rounded-2xl bg-teal-950/40 border border-[#00f5d4]/40 flex flex-col gap-3 text-center shadow-[0_0_20px_rgba(0,245,212,0.15)]">
        <span className="text-[11px] font-mono font-bold text-[#00f5d4] uppercase tracking-wider flex items-center justify-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          Hackathon Quick Access
        </span>
        <p className="text-xs text-slate-300">
          Sign in instantly with pre-seeded demo ASHA Worker credentials (Shweta Patil, Kadugodi PHC).
        </p>
        <button
          onClick={handleDemoLogin}
          disabled={loading}
          className="w-full py-3 rounded-xl glass-button-neon text-[#031410] font-bold text-xs shadow-[0_0_20px_rgba(0,245,212,0.4)] cursor-pointer"
        >
          ⚡ Launch with Demo ASHA Worker Profile
        </button>
      </div>

      <div className="flex items-center gap-4 text-xs text-slate-500">
        <div className="h-[1px] bg-teal-500/20 flex-1" />
        <span>or sign in with credentials</span>
        <div className="h-[1px] bg-teal-500/20 flex-1" />
      </div>

      {/* Auth Card */}
      <div className="p-8 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-5">
        <div className="flex items-center justify-around border-b border-teal-500/20 pb-3 text-xs font-bold">
          <button
            onClick={() => setIsRegister(false)}
            className={`pb-1 transition-colors ${!isRegister ? 'text-[#00f5d4] border-b-2 border-[#00f5d4]' : 'text-slate-400'}`}
          >
            Sign In
          </button>
          <button
            onClick={() => setIsRegister(true)}
            className={`pb-1 transition-colors ${isRegister ? 'text-[#00f5d4] border-b-2 border-[#00f5d4]' : 'text-slate-400'}`}
          >
            Register Profile
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-xs">
          {isRegister && (
            <div>
              <label className="text-slate-400 mb-1 block">Full Name</label>
              <div className="flex items-center gap-2 p-3 rounded-xl bg-white/5 border border-teal-500/20">
                <UserIcon className="w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Shweta Patil"
                  className="w-full bg-transparent border-0 text-white focus:outline-none"
                />
              </div>
            </div>
          )}

          <div>
            <label className="text-slate-400 mb-1 block">Government / Official Email</label>
            <div className="flex items-center gap-2 p-3 rounded-xl bg-white/5 border border-teal-500/20">
              <Mail className="w-4 h-4 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="asha.worker@karnataka.gov.in"
                className="w-full bg-transparent border-0 text-white focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-slate-400 mb-1 block">Password</label>
            <div className="flex items-center gap-2 p-3 rounded-xl bg-white/5 border border-teal-500/20">
              <Lock className="w-4 h-4 text-slate-400" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-transparent border-0 text-white focus:outline-none"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="text-slate-400 mb-1 block">Role Selection</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full p-3 rounded-xl bg-[#041d16] border border-teal-500/20 text-white focus:outline-none"
              >
                <option value="ASHA_WORKER">ASHA Worker (Field Community Health)</option>
                <option value="PHC_MO">Primary Health Centre Medical Officer</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3.5 rounded-xl bg-teal-500 hover:bg-[#00f5d4] text-[#031410] font-bold text-xs uppercase tracking-wider transition-all cursor-pointer shadow-[0_0_20px_rgba(20,184,166,0.3)]"
          >
            {loading ? 'Authenticating...' : isRegister ? 'Create Profile' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};
