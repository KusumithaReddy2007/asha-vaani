import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { FollowUpTask } from '../types';
import {
  Calendar,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Filter,
  Check,
  CalendarCheck,
  Search,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';

export const FollowUpsPage: React.FC = () => {
  const [tasks, setTasks] = useState<FollowUpTask[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'PENDING' | 'OVERDUE' | 'COMPLETED'>('ALL');
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const loadFollowups = async () => {
    try {
      setLoading(true);
      const res = await api.getFollowups();
      setTasks(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFollowups();
  }, []);

  const handleMarkComplete = async (id: number) => {
    try {
      await api.updateFollowupStatus(id, 'COMPLETED', 'Follow-up visit conducted and verified by ASHA worker.');
      loadFollowups();
    } catch (e) {
      console.error(e);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (filter !== 'ALL' && t.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        t.beneficiary_name.toLowerCase().includes(q) ||
        t.beneficiary_code.toLowerCase().includes(q) ||
        t.task_title.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-teal-500/20">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Automated Follow-up Management</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-teal-500/20 text-[#00f5d4] border border-teal-500/30">
              Auto-Generated from Voice Records
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Tracks neonatal growth monitoring, pending immunizations, and emergency PHC referrals.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-emerald-950/60 border border-teal-500/30 backdrop-blur-md self-start sm:self-auto">
          {(['ALL', 'PENDING', 'OVERDUE', 'COMPLETED'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                filter === tab ? 'bg-[#00f5d4] text-[#031410]' : 'text-slate-300 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Search Input */}
      <div className="flex items-center gap-2 p-3 rounded-2xl glass-panel border border-teal-500/20">
        <Search className="w-4 h-4 text-slate-400 ml-2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by beneficiary name (Lakshmi, Priya, Sunita) or code (SYN-001)..."
          className="w-full bg-transparent border-0 text-xs text-white placeholder-slate-500 focus:outline-none"
        />
      </div>

      {/* Task Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredTasks.map((task) => (
          <div
            key={task.id}
            className={`p-6 rounded-3xl glass-panel border transition-all flex flex-col justify-between gap-4 ${
              task.priority === 'EMERGENCY'
                ? 'border-rose-500/50 bg-rose-950/20 shadow-[0_0_20px_rgba(244,63,94,0.15)]'
                : 'border-teal-500/20 hover:border-teal-500/40'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs font-bold text-[#00f5d4]">{task.beneficiary_code}</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                    task.status === 'COMPLETED'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : task.status === 'OVERDUE'
                      ? 'bg-rose-500/20 text-rose-300'
                      : 'bg-amber-500/20 text-amber-300'
                  }`}
                >
                  {task.status}
                </span>
              </div>

              <h3 className="font-bold text-white text-base leading-snug">{task.task_title}</h3>
              <p className="text-xs text-teal-300 font-semibold mt-1">{task.beneficiary_name}</p>

              {task.notes && (
                <p className="text-xs text-slate-300 mt-2 p-2.5 rounded-xl bg-white/5 border border-white/5 leading-relaxed">
                  {task.notes}
                </p>
              )}
            </div>

            <div className="pt-4 border-t border-teal-500/15 flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                <Calendar className="w-3.5 h-3.5 text-[#00f5d4]" />
                Due: <strong className="text-white">{task.due_date}</strong>
              </div>

              {task.status !== 'COMPLETED' ? (
                <button
                  onClick={() => handleMarkComplete(task.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-500/20 hover:bg-teal-500/30 text-[#00f5d4] border border-teal-500/40 font-bold text-xs transition-all cursor-pointer"
                >
                  <Check className="w-3.5 h-3.5" />
                  Mark Done
                </button>
              ) : (
                <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Completed
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
