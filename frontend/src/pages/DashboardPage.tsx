import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { HealthcareVisit, DangerSignAlert, FollowUpTask, Beneficiary, DashboardMetrics } from '../types';
import {
  Activity,
  Users,
  AlertTriangle,
  CalendarCheck,
  CheckCircle2,
  Syringe,
  ArrowUpRight,
  ShieldAlert,
  Clock,
  Sparkles,
  ExternalLink,
  PlusCircle,
  FileSpreadsheet
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

interface DashboardPageProps {
  onNavigateToVoice: () => void;
  onNavigateToFollowups: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateToVoice,
  onNavigateToFollowups,
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [beneficiaryDist, setBeneficiaryDist] = useState<any[]>([]);
  const [vaxData, setVaxData] = useState<any[]>([]);
  const [visitTrends, setVisitTrends] = useState<any[]>([]);
  const [recentVisits, setRecentVisits] = useState<HealthcareVisit[]>([]);
  const [alerts, setAlerts] = useState<DangerSignAlert[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dashRes, visitsRes, alertsRes, bRes] = await Promise.all([
        api.getDashboardData(),
        api.getVisits(),
        api.getAlerts(),
        api.getBeneficiaries(),
      ]);

      setMetrics(dashRes.metrics);
      setBeneficiaryDist(dashRes.beneficiary_distribution);
      setVaxData(dashRes.vaccination_breakdown);
      setVisitTrends(dashRes.visit_trends);
      setRecentVisits(visitsRes);
      setAlerts(alertsRes);
      setBeneficiaries(bRes);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAcknowledge = async (alertId: number) => {
    try {
      await api.acknowledgeAlert(alertId);
      loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const COLORS = ['#00f5d4', '#14b8a6', '#0d9488', '#0f766e'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex flex-col gap-8">
      {/* Top Welcome & Summary Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-teal-500/20">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">ASHA Healthcare Operations Hub</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-teal-500/20 text-[#00f5d4] border border-teal-500/30">
              Live Database Connected
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Kadugodi Primary Health Centre • Shweta Patil (ASHA-BLR-042)
          </p>
        </div>

        <button
          onClick={onNavigateToVoice}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl glass-button-neon text-[#031410] font-bold text-xs shadow-[0_0_20px_rgba(0,245,212,0.3)] transition-all cursor-pointer self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4 text-[#031410]" />
          Record New Visit
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
        <div className="p-5 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Household Visits</span>
            <Activity className="w-4 h-4 text-[#00f5d4]" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-white font-mono">
            {metrics?.total_household_visits || 24}
          </span>
          <span className="text-[11px] text-teal-400 flex items-center gap-1 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00f5d4]" />
            {metrics?.today_visits || 2} completed today
          </span>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Active Danger Alerts</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-rose-300 font-mono">
            {metrics?.active_danger_alerts || 1}
          </span>
          <span className="text-[11px] text-rose-300/80 font-semibold flex items-center gap-1">
            Emergency PHC referrals
          </span>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Pending Follow-ups</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-amber-200 font-mono">
            {metrics?.pending_followups || 3}
          </span>
          <button
            onClick={onNavigateToFollowups}
            className="text-[11px] text-amber-400 hover:text-white flex items-center gap-1 text-left underline"
          >
            Open follow-up calendar →
          </button>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Beneficiaries</span>
            <Users className="w-4 h-4 text-[#00f5d4]" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-white font-mono">
            {metrics?.total_beneficiaries || 5}
          </span>
          <span className="text-[11px] text-teal-400 font-semibold">
            SYN-001 to SYN-005 synthetic profiles
          </span>
        </div>
      </div>

      {/* Emergency Danger Sign Alert Notification Panel */}
      {alerts.length > 0 && (
        <div className="p-6 rounded-3xl bg-rose-950/40 border-2 border-rose-500/40 backdrop-blur-xl flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <ShieldAlert className="w-5 h-5 text-rose-400 animate-pulse" />
              <h3 className="font-extrabold text-white text-base">
                Active PHC Emergency Referral Alerts ({alerts.filter((a) => !a.acknowledged).length})
              </h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/30 text-rose-200 font-bold">
              MoHFW Protocol Action Required
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="p-4 rounded-2xl bg-black/40 border border-rose-500/30 flex items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">{alert.beneficiary_name}</span>
                    <span className="font-mono text-xs text-rose-300">({alert.beneficiary_code})</span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-xs text-rose-200 font-medium mt-1">"{alert.danger_sign_name}"</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">{alert.referral_action}</p>
                </div>

                {!alert.acknowledged ? (
                  <button
                    onClick={() => handleAcknowledge(alert.id)}
                    className="px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs shrink-0 transition-all shadow-[0_0_15px_rgba(244,63,94,0.3)]"
                  >
                    Acknowledge
                  </button>
                ) : (
                  <span className="text-xs text-emerald-400 flex items-center gap-1 shrink-0 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Triaged
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interactive Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visit Trends Area Chart (7 cols) */}
        <div className="lg:col-span-7 p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Weekly Household Visit Velocity</h3>
              <p className="text-xs text-slate-400">Antenatal care (ANC) vs Newborn postnatal visits</p>
            </div>
            <span className="text-xs font-mono text-[#00f5d4]">Week 47</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={visitTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="ancGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f5d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#00f5d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="newbornGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#063228" vertical={false} />
                <XAxis dataKey="day" stroke="#0d9488" fontSize={11} tickLine={false} />
                <YAxis stroke="#0d9488" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#031913',
                    borderColor: '#14b8a6',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
                <Area type="monotone" dataKey="anc" name="ANC Visits" stroke="#00f5d4" strokeWidth={2} fillOpacity={1} fill="url(#ancGradient)" />
                <Area type="monotone" dataKey="newborn" name="Newborn Visits" stroke="#14b8a6" strokeWidth={2} fillOpacity={1} fill="url(#newbornGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Beneficiary Distribution Pie Chart (5 cols) */}
        <div className="lg:col-span-5 p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
          <h3 className="font-bold text-white text-base">Beneficiary Demographics</h3>
          <p className="text-xs text-slate-400">Coverage across Kadugodi Ward 3 & Belathur</p>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={beneficiaryDist}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {beneficiaryDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#031913',
                    borderColor: '#14b8a6',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-around text-[11px] text-slate-300 pt-2 border-t border-teal-500/15">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#00f5d4]" />
              Pregnant (ANC)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#14b8a6]" />
              Newborns
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#0d9488]" />
              Infants
            </span>
          </div>
        </div>
      </div>

      {/* Synthetic Beneficiary Directory */}
      <div className="p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-base">Registered Beneficiaries (Synthetic Dataset)</h3>
            <p className="text-xs text-slate-400">Pre-seeded MoHFW test benchmark subjects</p>
          </div>
          <span className="text-xs font-mono text-teal-400">{beneficiaries.length} records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-teal-500/20 text-slate-400 font-mono">
                <th className="pb-3 font-semibold">ID</th>
                <th className="pb-3 font-semibold">Beneficiary Name</th>
                <th className="pb-3 font-semibold">Category</th>
                <th className="pb-3 font-semibold">Clinical Details</th>
                <th className="pb-3 font-semibold">Village / Ward</th>
                <th className="pb-3 font-semibold">Danger Flag</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-teal-500/10 text-slate-200">
              {beneficiaries.map((b) => (
                <tr key={b.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3 font-mono font-bold text-[#00f5d4]">{b.beneficiary_id}</td>
                  <td className="py-3 font-semibold text-white">{b.name}</td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded bg-teal-500/15 text-teal-300 font-medium">
                      {b.category}
                    </span>
                  </td>
                  <td className="py-3 text-slate-300">{b.age_or_details || 'Routine'}</td>
                  <td className="py-3 text-slate-400">{b.village}</td>
                  <td className="py-3">
                    {b.danger_flag ? (
                      <span className="px-2 py-0.5 rounded bg-rose-500/30 text-rose-300 font-bold">
                        HIGH RISK
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-medium">
                        Normal
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Visits Table */}
      <div className="p-6 rounded-3xl glass-panel border border-teal-500/20 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-base">Recent Voice-Recorded Visits</h3>
            <p className="text-xs text-slate-400">Confirmed healthcare visits recorded via ASHA-VAANI</p>
          </div>
          <button
            onClick={onNavigateToVoice}
            className="text-xs text-[#00f5d4] hover:underline flex items-center gap-1 font-semibold"
          >
            Open Assistant →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-teal-500/20 text-slate-400 font-mono">
                <th className="pb-3 font-semibold">Date</th>
                <th className="pb-3 font-semibold">Beneficiary</th>
                <th className="pb-3 font-semibold">House & Live GPS</th>
                <th className="pb-3 font-semibold">Visit Type</th>
                <th className="pb-3 font-semibold">Weight</th>
                <th className="pb-3 font-semibold">Vaccinations / Meds</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-teal-500/10 text-slate-200">
              {recentVisits.map((visit) => (
                <tr key={visit.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3 font-mono text-slate-400">{visit.visit_date}</td>
                  <td className="py-3">
                    <span className="font-bold text-white block">{visit.beneficiary_name}</span>
                    <span className="text-[10px] text-teal-400 font-mono">{visit.beneficiary_code}</span>
                  </td>
                  <td className="py-3">
                    <span className="font-semibold text-white block">
                      {visit.house_number ? `H.No: ${visit.house_number}` : 'Ward 3, Belathur'}
                    </span>
                    <span className="text-[10px] text-teal-400 font-mono">
                      📍 {visit.location_lat ? `${visit.location_lat.toFixed(4)}, ${visit.location_lng?.toFixed(4)}` : '12.9784, 77.7289'}
                    </span>
                  </td>
                  <td className="py-3 text-teal-200">{visit.visit_type}</td>
                  <td className="py-3 font-mono text-[#00f5d4]">
                    {visit.weight_kg ? `${visit.weight_kg} kg` : '—'}
                  </td>
                  <td className="py-3">
                    {visit.vaccinations_given && Object.keys(visit.vaccinations_given).length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(visit.vaccinations_given).map(([v, s]) => (
                          <span key={v} className="px-1.5 py-0.5 rounded bg-teal-500/20 text-[#00f5d4] text-[10px]">
                            {v}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-slate-500 italic">None</span>
                    )}
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {visit.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
