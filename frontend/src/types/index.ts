export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export interface Beneficiary {
  id: number;
  beneficiary_id: string;
  name: string;
  category: 'PREGNANT_WOMAN' | 'NEWBORN' | 'INFANT' | 'CHILD';
  age_or_details?: string;
  guardian_name?: string;
  village: string;
  contact_phone: string;
  danger_flag: boolean;
  created_at: string;
}

export interface DetectedDangerSign {
  id: string;
  name: string;
  severity: string;
  action_instruction: string;
  spoken_instruction: string;
  matched_term?: string;
  guideline?: string;
}

export interface ExtractedRecord {
  beneficiary_id?: string;
  beneficiary_name?: string;
  visit_type?: string;
  pregnancy_or_newborn_details?: string;
  weight_kg?: number | null;
  vaccinations: Record<string, string>;
  health_observations: string[];
  next_visit_date?: string | null;
  danger_signs: DetectedDangerSign[];
  status: 'Pending Confirmation' | 'Confirmed' | 'Cancelled';
  confidence: number;
  clarification_needed?: string;
  raw_transcript?: string;
}

export interface HealthcareVisit {
  id: number;
  beneficiary_id: number;
  beneficiary_name: string;
  beneficiary_code: string;
  visit_type: string;
  visit_date: string;
  weight_kg?: number;
  vaccinations_given: Record<string, string>;
  health_observations?: string;
  next_visit_date?: string;
  danger_signs_detected: DetectedDangerSign[];
  referral_made: boolean;
  referral_facility?: string;
  status: string;
  confidence_score: number;
  transcript_snippet?: string;
  created_at: string;
}

export interface DangerSignAlert {
  id: number;
  visit_id?: number;
  beneficiary_id: number;
  beneficiary_name: string;
  beneficiary_code: string;
  danger_sign_name: string;
  severity: string;
  referral_action: string;
  guideline_citation: string;
  acknowledged: boolean;
  referred_to_phc: boolean;
  created_at: string;
}

export interface FollowUpTask {
  id: number;
  beneficiary_id: number;
  beneficiary_name: string;
  beneficiary_code: string;
  visit_id?: number;
  task_title: string;
  due_date: string;
  status: 'PENDING' | 'COMPLETED' | 'OVERDUE';
  priority: 'NORMAL' | 'HIGH' | 'EMERGENCY';
  notes?: string;
  completed_at?: string;
  created_at: string;
}

export interface DashboardMetrics {
  total_household_visits: number;
  today_visits: number;
  pending_followups: number;
  completed_records: number;
  active_danger_alerts: number;
  total_beneficiaries: number;
  vaccinations_delivered: number;
  referrals_to_phc: number;
}
