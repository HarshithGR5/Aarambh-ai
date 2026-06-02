export type UserRole = 'AWW' | 'CDPO' | 'HEALTH_WORKER' | 'STATE_OFFICER' | 'ADMIN';
export type RiskLevel = 'GREEN' | 'AMBER' | 'RED';
export type GenderType = 'MALE' | 'FEMALE' | 'OTHER';

export interface User {
  id: string;
  phone: string;
  name: string;
  role: UserRole;
  awc_id?: number;
  district_id?: number;
  language: string;
  is_active: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface Child {
  id: string;
  full_name: string;
  date_of_birth: string;
  gender: GenderType;
  awc_id: number;
  parent_name?: string;
  parent_phone?: string;
  parent_language: string;
  registration_date: string;
  photo_url?: string;
  qr_code?: string;
  is_active: boolean;
  notes?: string;
  created_at: string;
  age_months: number;
  age_years: number;
  age_months_remainder: number;
  latest_pdrs_score?: number;
  latest_risk_level?: RiskLevel;
}

export interface ChildCreate {
  full_name: string;
  date_of_birth: string;
  gender: GenderType;
  awc_id: number;
  parent_name?: string;
  parent_phone?: string;
  parent_language?: string;
  notes?: string;
}

export interface PDRSScore {
  id: number;
  child_id: string;
  overall_score: number;
  risk_level: RiskLevel;
  domain_scores: Record<string, number>;
  computed_at: string;
}

export interface DDTSnapshot {
  id: number;
  child_id: string;
  pdrs_score_id?: number;
  portrait_text: string;
  portrait_text_hi?: string;
  school_readiness_flag?: string;
  school_readiness_note?: string;
  asd_flag: boolean;
  speech_delay_flag: boolean;
  motor_delay_flag: boolean;
  snapshot_data: Record<string, unknown>;
  created_at: string;
}

export interface Observation {
  id: string;
  child_id: string;
  observation_type: string;
  raw_text?: string;
  transcript?: string;
  english_text?: string;
  processing_status: string;
  markers: ObservationMarker[];
  created_at: string;
}

export interface ObservationMarker {
  id: number;
  domain_id: number;
  domain_code?: string;
  domain_name?: string;
  marker_type: 'POSITIVE' | 'CONCERN' | 'FLAG';
  severity?: string;
  description: string;
  confidence?: number;
}

export interface Milestone {
  id: number;
  domain_id: number;
  domain_code: string;
  domain_name: string;
  text: string;
  text_hi?: string;
  age_min_months: number;
  age_max_months: number;
  is_critical: boolean;
  source: string;
}

export interface MilestoneAssessment {
  milestone_id: number;
  milestone_text: string;
  domain_code: string;
  domain_name: string;
  result: 'YES' | 'SOMETIMES' | 'NOT_YET' | 'NA' | null;
  is_critical: boolean;
  assessed_date?: string;
}

export interface Drawing {
  id: string;
  child_id: string;
  image_url: string;
  context?: string;
  upload_date: string;
  analysis?: DrawingAnalysis;
}

export interface DrawingAnalysis {
  id: number;
  drawing_id: string;
  fine_motor_score?: number;
  cognitive_score?: number;
  emotional_tone?: string;
  spatial_org_score?: number;
  figure_complexity?: number;
  ai_summary: string;
  ai_summary_hi?: string;
  domain_flags: Record<string, unknown>;
  analyzed_at: string;
}

export interface Referral {
  id: string;
  child_id: string;
  child_name?: string;
  referred_by: string;
  facility_id?: number;
  facility_name?: string;
  primary_concern: string;
  domains_of_concern: string[];
  referral_date: string;
  status: 'PENDING' | 'CONTACTED' | 'ASSESSED' | 'CLOSED' | 'CANCELLED';
  letter_url?: string;
  follow_up_date?: string;
  outcome_notes?: string;
}

export interface GovernmentScheme {
  id: number;
  name: string;
  ministry: string;
  description: string;
  eligibility_criteria?: string;
  benefits?: string;
  apply_url?: string;
}

export interface Recommendation {
  id: number;
  child_id: string;
  domain_code: string;
  title: string;
  activity_description: string;
  materials_needed?: string;
  frequency?: string;
  created_at: string;
}

export interface AWWDashboard {
  today_date: string;
  awc?: { id: number; name: string };
  stats: {
    total_children: number;
    present_today: number;
    red_zone_children: number;
    amber_zone_children: number;
    green_zone_children: number;
    pending_milestones: number;
    overdue_referrals: number;
  };
  alerts: Array<{
    type: string;
    child_id: string;
    child_name: string;
    days_ago?: number;
    pdrs_score?: number;
  }>;
  today_actions: Array<{
    priority: number;
    action: string;
    child_id: string;
    child_name: string;
  }>;
}

export interface CDPODashboard {
  block_name: string;
  total_awcs: number;
  total_children: number;
  red_zone_children: number;
  amber_zone_children: number;
  green_zone_children: number;
  referrals_this_month: number;
  referral_completion_rate: number;
  inactive_awws: number;
}

export interface AnganwadiCenter {
  id: number;
  name: string;
  center_number: string;
  village?: string;
  is_active: boolean;
}
