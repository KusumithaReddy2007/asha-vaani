import React from 'react';
import {
  Cpu,
  Database,
  Radio,
  ShieldAlert,
  Volume2,
  FileCode2,
  GitBranch,
  Layers,
  ArrowRight,
  Server,
  Terminal,
  Activity,
  CheckCircle2
} from 'lucide-react';

export const ArchitecturePage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex flex-col gap-10">
      {/* Header */}
      <div className="pb-4 border-b border-teal-500/20">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">System Architecture & Technical Stack</h1>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-teal-500/20 text-[#00f5d4] border border-teal-500/30">
            Build Bengaluru 2.0 • PS1
          </span>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 mt-1">
          Detailed technical blueprints, Gnani API platform integration details, and MoHFW deterministic rule engine design.
        </p>
      </div>

      {/* Interactive 3D/Visual Pipeline Flowchart */}
      <div className="p-8 rounded-3xl glass-panel border border-[#00f5d4]/30 relative overflow-hidden flex flex-col gap-8">
        <div>
          <span className="text-xs font-mono font-bold uppercase tracking-widest text-[#00f5d4]">
            End-to-End Pipeline
          </span>
          <h2 className="text-2xl font-extrabold text-white mt-1">The 8-Stage Voice-to-Record Workflow</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 01</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Radio className="w-4 h-4 text-[#00f5d4]" />
              Audio Streaming
            </div>
            <p className="text-xs text-slate-300">
              Browser Web Audio API captures PCM/WebM linear audio chunks at 16,000Hz mono and streams via WebSocket.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 02</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Cpu className="w-4 h-4 text-[#00f5d4]" />
              Gnani Prisma v3.0
            </div>
            <p className="text-xs text-slate-300">
              Real-time streaming speech-to-text with Indic language support and natural English code-mixing.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 03</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Layers className="w-4 h-4 text-[#00f5d4]" />
              AI Extraction Engine
            </div>
            <p className="text-xs text-slate-300">
              Multi-turn conversational context extractor. Resolves beneficiary ID, weight (kg), vaccinations, and dates.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-rose-500/40 bg-rose-950/20 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-rose-300 font-bold">STAGE 04 (SAFETY)</span>
            <div className="flex items-center gap-2 text-rose-200 font-bold text-sm">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              Deterministic Rule Engine
            </div>
            <p className="text-xs text-rose-200/80">
              MoHFW & WHO IMNCI compliant zero-miss safety gate. Immediately escalates bleeding or newborn high fever.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 05</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Volume2 className="w-4 h-4 text-[#00f5d4]" />
              Gnani Timbre v3.0 TTS
            </div>
            <p className="text-xs text-slate-300">
              Synthesizes spoken confirmation readback prompt in English, Hindi, or Kannada.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 06</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <CheckCircle2 className="w-4 h-4 text-[#00f5d4]" />
              Voice Confirmation Gate
            </div>
            <p className="text-xs text-slate-300">
              "Is this correct?" Explicit confirmation required before committing ("Yes, save it" or correction).
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 07</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Database className="w-4 h-4 text-[#00f5d4]" />
              Database Persistence
            </div>
            <p className="text-xs text-slate-300">
              SQLAlchemy models persist visit records, vaccination entries, and audit logs.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#031c15] border border-teal-500/30 flex flex-col gap-2">
            <span className="text-[10px] font-mono text-[#00f5d4] font-bold">STAGE 08</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Activity className="w-4 h-4 text-[#00f5d4]" />
              Automated Follow-ups
            </div>
            <p className="text-xs text-slate-300">
              Auto-calculates next visit calendar tasks, overdue immunization reminders, and referral status.
            </p>
          </div>
        </div>
      </div>

      {/* Tech Stack Specs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <Cpu className="w-5 h-5 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">Gnani API Platform</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li>• <strong>STT Model:</strong> Prisma-v3.0 (Streaming WebSocket)</li>
            <li>• <strong>TTS Model:</strong> Timbre-v3.0 (High-fidelity speech)</li>
            <li>• <strong>Audio Encoding:</strong> Linear PCM / WebM 16kHz mono</li>
            <li>• <strong>Languages:</strong> en-IN, hi-IN, kn-IN code-mix</li>
            <li>• <strong>Zero Telephony:</strong> Direct browser WebSockets</li>
          </ul>
        </div>

        <div className="p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <Server className="w-5 h-5 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">Backend & AI Core</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li>• <strong>Framework:</strong> FastAPI & Python 3.12</li>
            <li>• <strong>WebSockets:</strong> Bidirectional streaming</li>
            <li>• <strong>ORM:</strong> SQLAlchemy (SQLite / PostgreSQL)</li>
            <li>• <strong>Rule Engine:</strong> Zero-dependency regex pattern catalog</li>
            <li>• <strong>Validation:</strong> Pydantic 2.0 schemas</li>
          </ul>
        </div>

        <div className="p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <Radio className="w-5 h-5 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">Frontend Experience</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li>• <strong>UI Stack:</strong> React 19, TypeScript, Vite</li>
            <li>• <strong>Styling:</strong> Tailwind CSS dark emerald & neon cyan</li>
            <li>• <strong>3D Engine:</strong> Three.js WebGL canvas scene</li>
            <li>• <strong>Data Viz:</strong> Recharts interactive charts</li>
            <li>• <strong>Audio:</strong> Web Audio API AnalyserNode</li>
          </ul>
        </div>
      </div>

      {/* Guidelines Citations */}
      <div className="p-6 rounded-3xl bg-teal-950/30 border border-teal-500/30 flex flex-col gap-3">
        <h3 className="font-bold text-white text-base">Official Clinical Guideline Citations</h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          1. <strong>Ministry of Health and Family Welfare (MoHFW)</strong>, Government of India: <em>Operational Guidelines for Maternal and Newborn Health Services at Primary Health Centres</em>, Chapter 4: Emergency Obstetric Care & High-Risk Pregnancy Identification.
        </p>
        <p className="text-xs text-slate-300 leading-relaxed">
          2. <strong>World Health Organization (WHO) / UNICEF / MoHFW</strong>: <em>Integrated Management of Neonatal and Childhood Illness (IMNCI)</em> Protocol, Module 2: Assess and Classify the Sick Young Infant (0–2 months).
        </p>
      </div>
    </div>
  );
};
