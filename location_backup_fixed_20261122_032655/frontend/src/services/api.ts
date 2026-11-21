import { User, Beneficiary, HealthcareVisit, DangerSignAlert, FollowUpTask, DashboardMetrics } from '../types';

const API_BASE = '/api';

export const api = {
  // Auth
  async demoLogin(): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/demo-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error('Demo login failed');
    return res.json();
  },

  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Invalid email or password');
    return res.json();
  },

  // Beneficiaries
  async getBeneficiaries(): Promise<Beneficiary[]> {
    const res = await fetch(`${API_BASE}/beneficiaries`);
    if (!res.ok) throw new Error('Failed to fetch beneficiaries');
    return res.json();
  },

  // Visits
  async getVisits(): Promise<HealthcareVisit[]> {
    const res = await fetch(`${API_BASE}/visits`);
    if (!res.ok) throw new Error('Failed to fetch visits');
    return res.json();
  },

  async saveConfirmedVisit(data: {
    beneficiary_id_str: string;
    visit_type: string;
    weight_kg?: number | null;
    vaccinations_given: Record<string, string>;
    health_observations?: string;
    next_visit_date?: string | null;
    danger_signs_detected: any[];
    referral_made: boolean;
    house_number?: string;
    location_lat?: number | null;
    location_lng?: number | null;
    location_address?: string;
    transcript_snippet?: string;
  }): Promise<HealthcareVisit> {
    const res = await fetch(`${API_BASE}/visits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to save visit record');
    return res.json();
  },

  // Danger Signs
  async getAlerts(): Promise<DangerSignAlert[]> {
    const res = await fetch(`${API_BASE}/danger-signs/alerts`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async acknowledgeAlert(id: number): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/danger-signs/alerts/${id}/acknowledge`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to acknowledge alert');
    return res.json();
  },

  async getDangerRules(): Promise<any> {
    const res = await fetch(`${API_BASE}/danger-signs/rules`);
    if (!res.ok) throw new Error('Failed to fetch rules catalog');
    return res.json();
  },

  async evaluateDanger(text: string, language: string = 'en'): Promise<any> {
    const res = await fetch(`${API_BASE}/danger-signs/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
    });
    if (!res.ok) throw new Error('Failed to evaluate danger');
    return res.json();
  },

  // Follow-ups
  async getFollowups(status?: string): Promise<FollowUpTask[]> {
    const url = status ? `${API_BASE}/followups?status=${status}` : `${API_BASE}/followups`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch followups');
    return res.json();
  },

  async updateFollowupStatus(id: number, status: string, notes?: string): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/followups/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, notes }),
    });
    if (!res.ok) throw new Error('Failed to update followup');
    return res.json();
  },

  // Analytics
  async getDashboardData(): Promise<{
    metrics: DashboardMetrics;
    beneficiary_distribution: any[];
    vaccination_breakdown: any[];
    visit_trends: any[];
  }> {
    const res = await fetch(`${API_BASE}/analytics/dashboard`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  async getSystemStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/analytics/system-status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },
};
