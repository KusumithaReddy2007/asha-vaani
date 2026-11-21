import React, { useEffect, useMemo, useState } from 'react';
import { Search, FileText, Edit3, Save, X, UserRound, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { Beneficiary, HealthcareVisit } from '../types';

type EditForm = {
  visit_type: string;
  weight_kg: string;
  vaccinations_given: string;
  health_observations: string;
  next_visit_date: string;
  house_number: string;
  location_address: string;
};

const emptyForm: EditForm = {
  visit_type: '',
  weight_kg: '',
  vaccinations_given: '{}',
  health_observations: '',
  next_visit_date: '',
  house_number: '',
  location_address: '',
};

export const BeneficiaryRecordsPage: React.FC = () => {
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [visits, setVisits] = useState<HealthcareVisit[]>([]);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Beneficiary | null>(null);
  const [editing, setEditing] = useState<HealthcareVisit | null>(null);
  const [form, setForm] = useState<EditForm>(emptyForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [people, reports] = await Promise.all([
        api.getBeneficiaries(),
        api.getVisits(),
      ]);
      setBeneficiaries(people);
      setVisits(reports);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return beneficiaries;
    return beneficiaries.filter((b) =>
      b.name.toLowerCase().includes(q) ||
      b.beneficiary_id.toLowerCase().includes(q) ||
      (b.village || '').toLowerCase().includes(q)
    );
  }, [beneficiaries, search]);

  const selectedVisits = selected
    ? visits.filter((v) => v.beneficiary_id === selected.id)
    : [];

  const startEdit = (visit: HealthcareVisit) => {
    setEditing(visit);
    setMessage('');
    setError('');
    setForm({
      visit_type: visit.visit_type || '',
      weight_kg: visit.weight_kg == null ? '' : String(visit.weight_kg),
      vaccinations_given: JSON.stringify(visit.vaccinations_given || {}, null, 2),
      health_observations: visit.health_observations || '',
      next_visit_date: visit.next_visit_date || '',
      house_number: visit.house_number || '',
      location_address: visit.location_address || '',
    });
  };

  const saveEdit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!editing) return;

    let vaccinations: Record<string, string>;
    try {
      vaccinations = JSON.parse(form.vaccinations_given || '{}');
      if (!vaccinations || Array.isArray(vaccinations) || typeof vaccinations !== 'object') {
        throw new Error();
      }
    } catch {
      setError('Vaccinations must be a valid JSON object, for example {"BCG":"Given"}.');
      return;
    }

    const weight = form.weight_kg.trim() === '' ? null : Number(form.weight_kg);
    if (weight !== null && (!Number.isFinite(weight) || weight < 0)) {
      setError('Enter a valid weight.');
      return;
    }

    setSaving(true);
    setError('');
    setMessage('');

    try {
      const updated = await api.updateVisit(editing.id, {
        visit_type: form.visit_type,
        weight_kg: weight,
        vaccinations_given: vaccinations,
        health_observations: form.health_observations,
        next_visit_date: form.next_visit_date || undefined,
        house_number: form.house_number,
        location_address: form.location_address,
      });

      setVisits((current) => current.map((v) => v.id === updated.id ? updated : v));
      setEditing(null);
      setMessage(`Report #${updated.id} updated successfully.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update report.');
    } finally {
      setSaving(false);
    }
  };

  const fieldClass = "w-full rounded-xl border border-teal-500/20 bg-[#061f19] px-3 py-2.5 text-sm text-white outline-none focus:border-teal-400";
  const labelClass = "mb-1.5 block text-xs font-semibold text-teal-200";

  return (
    <section className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-7 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-400">Records management</p>
          <h1 className="mt-2 text-3xl font-extrabold text-white">Beneficiary Records</h1>
          <p className="mt-2 text-sm text-slate-400">Find a beneficiary and view or edit their saved visit reports.</p>
        </div>
        <button onClick={() => void loadData()} className="flex items-center gap-2 rounded-xl border border-teal-500/30 px-4 py-2.5 text-sm text-teal-200 hover:bg-teal-500/10">
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {error && <div className="mb-4 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-300">{error}</div>}
      {message && <div className="mb-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-300">{message}</div>}

      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
        <aside className="rounded-2xl border border-teal-500/20 bg-[#062019] p-4">
          <h2 className="mb-3 flex items-center gap-2 font-bold text-white"><Search size={17} className="text-teal-400" /> Search beneficiaries</h2>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Name, beneficiary ID or village..."
            className={fieldClass}
          />
          <p className="my-3 text-xs text-slate-500">{filtered.length} beneficiary record(s)</p>
          <div className="max-h-[560px] space-y-2 overflow-y-auto">
            {loading ? <p className="p-3 text-sm text-slate-400">Loading beneficiaries...</p> :
              filtered.map((b) => (
                <button
                  key={b.id}
                  onClick={() => { setSelected(b); setEditing(null); setMessage(''); setError(''); }}
                  className={`w-full rounded-xl border p-3 text-left transition ${selected?.id === b.id ? 'border-teal-400 bg-teal-500/15' : 'border-white/5 bg-white/[0.03] hover:border-teal-500/30'}`}
                >
                  <div className="flex items-center gap-2">
                    <UserRound size={17} className="text-teal-400" />
                    <span className="font-semibold text-white">{b.name}</span>
                  </div>
                  <p className="mt-1 text-xs text-teal-300">{b.beneficiary_id}</p>
                  <p className="mt-1 text-xs text-slate-500">{b.village}</p>
                </button>
              ))}
            {!loading && filtered.length === 0 && <p className="p-3 text-sm text-slate-500">No matching beneficiaries found.</p>}
          </div>
        </aside>

        <div className="min-w-0">
          {!selected ? (
            <div className="flex min-h-64 items-center justify-center rounded-2xl border border-dashed border-teal-500/20 bg-[#062019] p-8 text-center">
              <div><FileText className="mx-auto mb-3 text-teal-400" size={32} /><h2 className="font-bold text-white">Select a beneficiary</h2><p className="mt-2 text-sm text-slate-400">Their saved visit reports will appear here.</p></div>
            </div>
          ) : (
            <>
              <div className="mb-4 rounded-2xl border border-teal-500/20 bg-[#062019] p-5">
                <p className="text-xs uppercase tracking-wider text-teal-400">Selected beneficiary</p>
                <h2 className="mt-1 text-xl font-bold text-white">{selected.name}</h2>
                <p className="mt-1 text-sm text-slate-400">{selected.beneficiary_id} ? {selected.category} ? {selected.village}</p>
                <p className="mt-3 text-xs text-slate-500">{selectedVisits.length} saved visit report(s)</p>
              </div>

              {editing ? (
                <form onSubmit={saveEdit} className="rounded-2xl border border-teal-500/30 bg-[#062019] p-5">
                  <div className="mb-5 flex items-center justify-between gap-3">
                    <div><p className="text-xs text-teal-400">Editing existing report</p><h3 className="text-lg font-bold text-white">Report #{editing.id}</h3></div>
                    <button type="button" onClick={() => setEditing(null)} className="rounded-lg p-2 text-slate-400 hover:bg-white/10"><X size={18} /></button>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <label><span className={labelClass}>Visit type</span><input required className={fieldClass} value={form.visit_type} onChange={(e) => setForm({...form, visit_type:e.target.value})} /></label>
                    <label><span className={labelClass}>Weight (kg)</span><input type="number" min="0" step="0.01" className={fieldClass} value={form.weight_kg} onChange={(e) => setForm({...form, weight_kg:e.target.value})} /></label>
                    <label><span className={labelClass}>Next visit date</span><input type="date" className={fieldClass} value={form.next_visit_date} onChange={(e) => setForm({...form, next_visit_date:e.target.value})} /></label>
                    <label><span className={labelClass}>House number</span><input className={fieldClass} value={form.house_number} onChange={(e) => setForm({...form, house_number:e.target.value})} /></label>
                    <label className="sm:col-span-2"><span className={labelClass}>Location address</span><input className={fieldClass} value={form.location_address} onChange={(e) => setForm({...form, location_address:e.target.value})} /></label>
                    <label className="sm:col-span-2"><span className={labelClass}>Health observations</span><textarea rows={3} className={fieldClass} value={form.health_observations} onChange={(e) => setForm({...form, health_observations:e.target.value})} /></label>
                    <label className="sm:col-span-2"><span className={labelClass}>Vaccinations (JSON object)</span><textarea rows={4} className={`${fieldClass} font-mono`} value={form.vaccinations_given} onChange={(e) => setForm({...form, vaccinations_given:e.target.value})} /></label>
                  </div>
                  <p className="mt-3 text-xs text-amber-300">Beneficiary assignment, original visit date, danger signs and referral details are locked during this edit.</p>
                  <div className="mt-5 flex flex-wrap gap-3">
                    <button disabled={saving} className="flex items-center gap-2 rounded-xl bg-teal-400 px-5 py-2.5 text-sm font-bold text-[#031410] disabled:opacity-50"><Save size={16} /> {saving ? 'Saving...' : 'Save changes'}</button>
                    <button type="button" onClick={() => setEditing(null)} className="rounded-xl border border-white/10 px-5 py-2.5 text-sm text-slate-300">Cancel</button>
                  </div>
                </form>
              ) : (
                <div className="space-y-3">
                  {selectedVisits.map((v) => (
                    <article key={v.id} className="rounded-2xl border border-teal-500/15 bg-[#062019] p-5">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="text-xs text-teal-400">Report #{v.id} ? {v.visit_date}</p>
                          <h3 className="mt-1 font-bold text-white">{v.visit_type}</h3>
                          <p className="mt-1 text-xs text-slate-500">Saved {new Date(v.created_at).toLocaleString()}</p>
                        </div>
                        <button onClick={() => startEdit(v)} className="flex items-center gap-2 rounded-xl border border-teal-400/30 px-3 py-2 text-xs font-semibold text-teal-200 hover:bg-teal-500/10"><Edit3 size={14} /> Edit report</button>
                      </div>
                      <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                        <p className="text-slate-300">Weight: <span className="text-white">{v.weight_kg ?? 'Not recorded'}{v.weight_kg != null ? ' kg' : ''}</span></p>
                        <p className="text-slate-300">Next visit: <span className="text-white">{v.next_visit_date || 'Not scheduled'}</span></p>
                        <p className="text-slate-300">House: <span className="text-white">{v.house_number || 'Not recorded'}</span></p>
                        <p className="text-slate-300">Referral: <span className="text-white">{v.referral_made ? `Yes - ${v.referral_facility || 'Facility not specified'}` : 'No'}</span></p>
                      </div>
                      {v.health_observations && <p className="mt-3 whitespace-pre-wrap text-sm text-slate-400">{v.health_observations}</p>}
                      {v.danger_signs_detected?.length > 0 && <p className="mt-3 text-xs text-rose-300">Danger signs recorded: {v.danger_signs_detected.map((d) => d.name).join(', ')}</p>}
                    </article>
                  ))}
                  {selectedVisits.length === 0 && <div className="rounded-2xl border border-dashed border-teal-500/20 p-8 text-center text-sm text-slate-400">No visit reports saved for this beneficiary yet. New confirmed visits will appear here.</div>}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  );
};
