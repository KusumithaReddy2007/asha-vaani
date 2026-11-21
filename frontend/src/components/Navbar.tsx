import React from 'react';
import { User } from '../types';
import { Mic, Activity, Calendar, Shield, Cpu, LogIn, LogOut, Radio, FileText } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  user: User | null;
  onDemoLogin: () => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  user,
  onDemoLogin,
  onLogout,
}) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-teal-500/20 bg-[#031410]/80 backdrop-blur-xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <div
          onClick={() => setCurrentTab('landing')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-teal-600 to-[#00f5d4] p-[2px] shadow-[0_0_20px_rgba(0,245,212,0.35)] group-hover:shadow-[0_0_30px_rgba(0,245,212,0.6)] transition-all">
            <div className="w-full h-full bg-[#031c15] rounded-[14px] flex items-center justify-center">
              <Mic className="w-5 h-5 text-[#00f5d4] animate-pulse" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-[#00f5d4] transition-colors">
                ASHA-VAANI
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-500/20 text-[#00f5d4] border border-teal-500/30">
                PS1 • 2.0
              </span>
            </div>
            <p className="text-[11px] text-teal-300/70 hidden sm:block">
              Your Voice. Every Visit. Better Healthcare.
            </p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="hidden md:flex items-center gap-1.5 p-1 rounded-2xl bg-emerald-950/40 border border-teal-500/20 backdrop-blur-md">
          <button
            onClick={() => setCurrentTab('landing')}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
              currentTab === 'landing'
                ? 'bg-gradient-to-r from-teal-500/30 to-[#00f5d4]/20 text-[#00f5d4] border border-[#00f5d4]/40 shadow-[0_0_15px_rgba(0,245,212,0.2)]'
                : 'text-slate-300 hover:text-white hover:bg-white/5'
            }`}
          >
            Home
          </button>

          <button
            onClick={() => setCurrentTab('voice')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all relative ${
              currentTab === 'voice'
                ? 'bg-gradient-to-r from-teal-500 to-[#00f5d4] text-[#031410] shadow-[0_0_20px_rgba(0,245,212,0.5)]'
                : 'text-[#00f5d4] bg-[#00f5d4]/10 hover:bg-[#00f5d4]/20 border border-[#00f5d4]/30'
            }`}
          >
            <Radio className="w-3.5 h-3.5 animate-pulse text-current" />
            Live Voice Assistant
          </button>

          <button
            onClick={() => setCurrentTab('dashboard')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
              currentTab === 'dashboard'
                ? 'bg-gradient-to-r from-teal-500/30 to-[#00f5d4]/20 text-[#00f5d4] border border-[#00f5d4]/40 shadow-[0_0_15px_rgba(0,245,212,0.2)]'
                : 'text-slate-300 hover:text-white hover:bg-white/5'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            Dashboard
          </button>

          <button
            onClick={() => setCurrentTab('records')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
              currentTab === 'records'
                ? 'bg-gradient-to-r from-teal-500/30 to-[#00f5d4]/20 text-[#00f5d4] border border-[#00f5d4]/40'
                : 'text-slate-300 hover:text-white hover:bg-white/5'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Beneficiary Records
          </button>

          <button
            onClick={() => setCurrentTab('followups')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
              currentTab === 'followups'
                ? 'bg-gradient-to-r from-teal-500/30 to-[#00f5d4]/20 text-[#00f5d4] border border-[#00f5d4]/40 shadow-[0_0_15px_rgba(0,245,212,0.2)]'
                : 'text-slate-300 hover:text-white hover:bg-white/5'
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            Follow-ups
          </button>

          <button
            onClick={() => setCurrentTab('architecture')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
              currentTab === 'architecture'
                ? 'bg-gradient-to-r from-teal-500/30 to-[#00f5d4]/20 text-[#00f5d4] border border-[#00f5d4]/40 shadow-[0_0_15px_rgba(0,245,212,0.2)]'
                : 'text-slate-300 hover:text-white hover:bg-white/5'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            Architecture
          </button>
        </nav>

        {/* User Profile / Auth State */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-xs font-semibold text-white leading-tight">{user.full_name}</span>
                <span className="text-[10px] text-teal-400 font-mono">ASHA-BLR-042 • Kadugodi</span>
              </div>
              <div className="w-9 h-9 rounded-xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-teal-200 font-bold text-xs">
                SP
              </div>
              <button
                onClick={onLogout}
                title="Sign out"
                className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={onDemoLogin}
                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-teal-500/15 text-[#00f5d4] hover:bg-teal-500/25 border border-teal-500/40 transition-all shadow-[0_0_15px_rgba(0,245,212,0.15)]"
              >
                ⚡ 1-Click Demo Login
              </button>
              <button
                onClick={() => setCurrentTab('auth')}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
              >
                <LogIn className="w-3.5 h-3.5" />
                Sign In
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
