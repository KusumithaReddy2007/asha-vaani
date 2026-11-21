import React from 'react';
import { Shield, Heart, Mic, FileText, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-teal-500/15 bg-[#020e0b] text-slate-400 py-12 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Col */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-[#00f5d4]">
                <Mic className="w-4 h-4" />
              </div>
              <span className="font-bold text-lg text-white">ASHA-VAANI</span>
            </div>
            <p className="text-sm text-slate-400 max-w-md leading-relaxed mb-4">
              AI-powered multilingual voice assistant built for the frontlines of Indian healthcare. 
              Eliminating paper registers, preventing missed visits, and ensuring zero missed maternal and neonatal danger signs.
            </p>
            <div className="flex items-center gap-2 text-xs text-teal-400 font-mono">
              <Shield className="w-4 h-4 text-[#00f5d4]" />
              Build Bengaluru 2.0 Innovation Challenge • PS1 Healthcare
            </div>
          </div>

          {/* Guidelines & Compliance */}
          <div>
            <h4 className="text-xs uppercase font-bold tracking-wider text-slate-200 mb-3">Clinical Protocols</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span>• MoHFW MCH Operational Guidelines</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span>• WHO/UNICEF IMNCI Neonatal Protocol</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span>• RMNCH+A High-Risk Pregnancy Tracker</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span>• Deterministic Rule Engine (Zero Miss Policy)</span>
              </li>
            </ul>
          </div>

          {/* Voice Technology */}
          <div>
            <h4 className="text-xs uppercase font-bold tracking-wider text-slate-200 mb-3">Platform Stack</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span className="text-[#00f5d4]">⚡ Gnani Prisma v3.0</span> (Streaming STT)
              </li>
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span className="text-[#00f5d4]">🔊 Gnani Timbre v3.0</span> (Audio TTS)
              </li>
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span>🐍 FastAPI & Python WebSockets</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-400 hover:text-teal-300 transition-colors">
                <span>🌐 Three.js 3D WebGL Canvas</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-teal-500/10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© 2026 ASHA-VAANI Team. Developed for Build Bengaluru 2.0.</p>
          <p className="flex items-center gap-1 mt-2 sm:mt-0">
            Dedicated to 1,000,000+ ASHA workers across India <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
          </p>
        </div>
      </div>
    </footer>
  );
};
