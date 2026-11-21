import React from 'react';
import { HeroScene } from '../components/3d/HeroScene';
import {
  Mic,
  Activity,
  ShieldAlert,
  CalendarCheck,
  Languages,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Zap,
  Users,
  Baby,
  Building2,
  Stethoscope,
  Volume2,
  Clock,
  FileSpreadsheet
} from 'lucide-react';

interface LandingPageProps {
  onStartRecording: () => void;
  onExploreDashboard: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartRecording,
  onExploreDashboard,
}) => {
  return (
    <div className="w-full flex flex-col gap-24 pb-20 overflow-hidden">
      {/* 1. HERO SECTION */}
      <section className="relative min-h-[calc(100vh-80px)] flex items-center justify-center pt-8 lg:pt-0">
        {/* Ambient background glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-teal-500/15 via-[#00f5d4]/10 to-transparent rounded-full blur-[140px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
          {/* Left Text Column */}
          <div className="lg:col-span-7 flex flex-col gap-6 text-left">
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/30 w-fit backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-[#00f5d4] animate-ping" />
              <span className="text-xs font-bold uppercase tracking-wider text-[#00f5d4]">
                Build Bengaluru 2.0 • PS1 Healthcare
              </span>
            </div>

            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-[1.08]">
              Your Voice.{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00f5d4] via-teal-300 to-emerald-400">
                Every Visit.
              </span>{' '}
              Better Healthcare.
            </h1>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-2xl font-normal">
              An AI-powered multilingual voice assistant built for India's 1,000,000+ ASHA workers. 
              Transforming natural conversational speech during household visits into structured, validated healthcare records in real-time.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={onStartRecording}
                className="flex items-center gap-2.5 px-8 py-4 rounded-2xl glass-button-neon font-bold text-sm text-[#031410] shadow-[0_0_30px_rgba(0,245,212,0.4)] hover:shadow-[0_0_40px_rgba(0,245,212,0.7)] transition-all cursor-pointer"
              >
                <Mic className="w-5 h-5 text-[#031410]" />
                Start Voice Recording
              </button>

              <button
                onClick={onExploreDashboard}
                className="flex items-center gap-2.5 px-7 py-4 rounded-2xl bg-white/5 hover:bg-white/10 text-white font-semibold text-sm border border-teal-500/30 backdrop-blur-md transition-all cursor-pointer"
              >
                Explore Dashboard
                <ArrowRight className="w-4 h-4 text-[#00f5d4]" />
              </button>
            </div>

            {/* Live Highlights Banner */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-teal-500/15 max-w-xl">
              <div>
                <span className="text-2xl font-black text-white">0%</span>
                <p className="text-xs text-teal-300/80">Typing Required</p>
              </div>
              <div>
                <span className="text-2xl font-black text-[#00f5d4]">100%</span>
                <p className="text-xs text-teal-300/80">Deterministic Safety</p>
              </div>
              <div>
                <span className="text-2xl font-black text-white">&lt; 1.2s</span>
                <p className="text-xs text-teal-300/80">Voice to Record</p>
              </div>
            </div>
          </div>

          {/* Right 3D Column */}
          <div className="lg:col-span-5 h-[460px] sm:h-[540px] lg:h-[600px] w-full relative flex items-center justify-center">
            <HeroScene />
          </div>
        </div>
      </section>

      {/* 2. THE PROBLEM SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="text-xs font-bold uppercase tracking-widest text-rose-400">The Ground Reality</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            The Administrative Burden on ASHA Workers
          </h2>
          <p className="text-slate-400 text-sm mt-3">
            Every day, community health workers spend up to 40% of their working hours wrestling with paperwork rather than delivering patient care.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/20 backdrop-blur-md flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Heavy Paper Registers</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Carrying 10+ cumbersome physical registers across rural terrain causes wear, loss, and illegible handwriting.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/20 backdrop-blur-md flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400">
              <Clock className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Delayed Documentation</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Household notes are transcribed days later into portals, introducing delayed reporting and memory errors.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/20 backdrop-blur-md flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400">
              <CalendarCheck className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Missed Follow-ups</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Without automated calendar reminders, essential immunizations and postpartum visits slip past their critical windows.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/20 backdrop-blur-md flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Delayed Danger Signs</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Maternal bleeding or neonatal sepsis symptoms lack an immediate digital escalation pathway to the nearest PHC.
            </p>
          </div>
        </div>
      </section>

      {/* 3. THE SOLUTION SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="p-8 sm:p-12 rounded-3xl glass-panel border border-[#00f5d4]/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#00f5d4]/10 rounded-full blur-[100px] pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-teal-500/20 text-[#00f5d4] text-xs font-bold mb-4">
                <Sparkles className="w-3.5 h-3.5" />
                The ASHA-VAANI Solution
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white leading-tight mb-4">
                Speak Naturally. AI Structures The Record.
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-6">
                ASHA-VAANI allows the health worker to speak unconstrained natural language—even mixing Kannada, Hindi, and English—while holding the baby or counseling the mother. The AI pipeline transcribes, extracts, validates against health guidelines, reads back for confirmation, and creates calendar follow-ups.
              </p>

              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#00f5d4] shrink-0 mt-0.5" />
                  <p className="text-xs sm:text-sm text-slate-200">
                    <strong className="text-white">Indic Code-Mixing:</strong> Understands terms like "IFA goli given", "BCG given", "weight 2.8 kilo", "ANC completed".
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#00f5d4] shrink-0 mt-0.5" />
                  <p className="text-xs sm:text-sm text-slate-200">
                    <strong className="text-white">Voice Confirmation Gate:</strong> Reads the record aloud using Gnani Timbre v3.0 before saving. Never commits unconfirmed data.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#00f5d4] shrink-0 mt-0.5" />
                  <p className="text-xs sm:text-sm text-slate-200">
                    <strong className="text-white">Zero-Miss Danger Signs:</strong> Deterministic rule engine triggers immediate Primary Health Centre (PHC) referral alert.
                  </p>
                </div>
              </div>
            </div>

            {/* Conversational Sample Preview */}
            <div className="bg-[#031913]/90 rounded-2xl border border-teal-500/30 p-6 flex flex-col gap-4 shadow-2xl">
              <div className="flex items-center justify-between pb-3 border-b border-teal-500/20 text-xs">
                <span className="font-mono text-teal-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#00f5d4] animate-pulse" />
                  Live Voice Extraction Preview
                </span>
                <span className="px-2 py-0.5 rounded bg-teal-500/20 text-[#00f5d4] font-bold">SYN-001</span>
              </div>

              <div className="flex flex-col gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-200">
                  <span className="text-[#00f5d4] font-bold">ASHA Worker: </span>
                  "Lakshmi, 10 days baby, weight 2.8 kilo, BCG given, next visit 20 November."
                </div>

                <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-emerald-200">
                  <span className="text-[#00f5d4] font-bold">ASHA-VAANI (Readback): </span>
                  "I have recorded Lakshmi's newborn visit. Weight is 2.8 kilograms. BCG vaccination is given. Next visit on 20 November. Is this correct?"
                </div>

                <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-200">
                  <span className="text-[#00f5d4] font-bold">ASHA Worker: </span>
                  "Yes, save it."
                </div>

                <div className="p-2.5 rounded-lg bg-[#00f5d4]/20 border border-[#00f5d4]/40 text-[#00f5d4] text-[11px] font-bold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#00f5d4]" />
                  Visit Confirmed & Saved • Follow-up task added to calendar!
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. WORKFLOW PIPELINE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-bold uppercase tracking-widest text-[#00f5d4]">The Complete Lifecycle</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            The Voice-to-Record Pipeline
          </h2>
          <p className="text-slate-400 text-sm mt-3">
            SPEAK → TRANSCRIBE → UNDERSTAND → EXTRACT → VALIDATE → READ BACK → CONFIRM → SAVE → FOLLOW-UP
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 text-center">
          {[
            { step: '01', title: 'SPEAK', desc: 'Natural Indic Voice', icon: Mic },
            { step: '02', title: 'TRANSCRIBE', desc: 'Gnani Prisma v3.0', icon: Volume2 },
            { step: '03', title: 'UNDERSTAND', desc: 'AI Orchestration', icon: Zap },
            { step: '04', title: 'EXTRACT', desc: 'Structured JSON', icon: FileSpreadsheet },
            { step: '05', title: 'VALIDATE', desc: 'MoHFW Rule Engine', icon: ShieldAlert },
            { step: '06', title: 'READ BACK', desc: 'Gnani Timbre v3.0', icon: Volume2 },
            { step: '07', title: 'CONFIRM', desc: 'Voice Confirmation', icon: CheckCircle2 },
            { step: '08', title: 'FOLLOW-UP', desc: 'Calendar Reminders', icon: CalendarCheck },
          ].map((item, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl glass-panel-hover glass-panel flex flex-col items-center gap-2 border border-teal-500/15"
            >
              <span className="text-[10px] font-mono font-bold text-[#00f5d4]">{item.step}</span>
              <div className="w-8 h-8 rounded-xl bg-teal-500/20 text-[#00f5d4] flex items-center justify-center">
                <item.icon className="w-4 h-4" />
              </div>
              <h4 className="font-extrabold text-xs text-white">{item.title}</h4>
              <p className="text-[10px] text-slate-400 leading-tight">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 5. DANGER SIGN ESCALATION BANNER (CRITICAL MODULE HIGHLIGHT) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="p-8 rounded-3xl bg-gradient-to-r from-rose-950/40 via-red-950/25 to-emerald-950/30 border-2 border-rose-500/40 backdrop-blur-xl relative">
          <div className="flex flex-col md:flex-row items-center gap-6 justify-between">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 shrink-0">
                <ShieldAlert className="w-8 h-8 animate-bounce" />
              </div>
              <div>
                <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 text-[11px] font-bold mb-1">
                  CRITICAL COMPETITION MODULE • ZERO MISS POLICY
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-white">
                  Deterministic Danger-Sign Rule Engine
                </h3>
                <p className="text-xs sm:text-sm text-slate-300 max-w-2xl mt-1 leading-relaxed">
                  Compliant with MoHFW Maternal Care & WHO IMNCI Protocols. Never relies on LLM guessing alone. 
                  When high fever in a newborn or bleeding in pregnancy is detected, immediate emergency PHC referral instructions are spoken and flagged.
                </p>
              </div>
            </div>

            <button
              onClick={onStartRecording}
              className="px-6 py-3.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs uppercase tracking-wider shrink-0 transition-all shadow-[0_0_20px_rgba(244,63,94,0.4)]"
            >
              Test Emergency Scenarios
            </button>
          </div>
        </div>
      </section>

      {/* 6. SOCIAL IMPACT */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-bold uppercase tracking-widest text-[#00f5d4]">Transformational Outcomes</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            Social Impact on Public Healthcare
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-3">
            <Users className="w-8 h-8 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">For ASHA Workers</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Saves 2.5 hours per day on data entry, eliminates register loss anxiety, and empowers voice-first community interaction.
            </p>
          </div>

          <div className="p-6 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-3">
            <Stethoscope className="w-8 h-8 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">For Pregnant Women</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Immediate identification of antepartum hemorrhage, pre-eclampsia, and timely delivery of IFA supplementation.
            </p>
          </div>

          <div className="p-6 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-3">
            <Baby className="w-8 h-8 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">For Newborns</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Accurate birth weight tracking, prompt BCG/Polio administration, and rapid sepsis referral within golden hours.
            </p>
          </div>

          <div className="p-6 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-3">
            <Building2 className="w-8 h-8 text-[#00f5d4]" />
            <h3 className="font-bold text-white text-base">For PHCs & Medical Officers</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              100% digital, deduplicated registry with real-time referral alerts to prepare emergency triage before patient arrival.
            </p>
          </div>
        </div>
      </section>

      {/* 7. FINAL CTA */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 w-full text-center">
        <div className="p-10 sm:p-14 rounded-3xl bg-gradient-to-b from-teal-950/60 to-emerald-950/40 border border-teal-500/30 backdrop-blur-xl flex flex-col items-center gap-6">
          <div className="w-14 h-14 rounded-2xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-[#00f5d4]">
            <Mic className="w-7 h-7" />
          </div>
          <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
            Ready to Experience ASHA-VAANI?
          </h2>
          <p className="text-slate-300 text-sm max-w-xl">
            Test natural Indic voice recording, multi-turn correction, danger-sign escalation, and automated follow-up generation now.
          </p>
          <button
            onClick={onStartRecording}
            className="px-8 py-4 rounded-2xl glass-button-neon text-[#031410] font-bold text-base shadow-[0_0_30px_rgba(0,245,212,0.4)] cursor-pointer"
          >
            Launch Live Voice Assistant
          </button>
        </div>
      </section>
    </div>
  );
};
