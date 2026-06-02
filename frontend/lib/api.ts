import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import type {
  User, Child, ChildCreate, PDRSScore, DDTSnapshot,
  Observation, Milestone, MilestoneAssessment, Drawing,
  Referral, GovernmentScheme, Recommendation, AWWDashboard, CDPODashboard,
} from './types';

const BASE_URL = '/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = Cookies.get('aarambh_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      Cookies.remove('aarambh_token');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

/* ─── AUTH ─────────────────────────────────── */
export const authApi = {
  requestOtp: (phone: string) =>
    api.post<{ message: string; otp?: string; phone: string }>('/auth/request-otp', { phone }),

  verifyOtp: (phone: string, otp: string) =>
    api.post<{ access_token: string; token_type: string; user: User }>('/auth/verify-otp', { phone, otp }),

  getMe: () => api.get<User>('/auth/me'),

  refresh: () =>
    api.post<{ access_token: string; user: User }>('/auth/refresh'),

  register: (data: {
    phone: string; name: string; role: string;
    awc_id?: number; district_id?: number; language?: string;
  }) => api.post<User>('/auth/register', data),
};

/* ─── CHILDREN ──────────────────────────────── */
export const childrenApi = {
  list: (awcId?: number, limit = 100, offset = 0) =>
    api.get<Child[]>('/children', { params: { awc_id: awcId, limit, offset } }),

  get: (id: string) => api.get<Child>(`/children/${id}`),

  create: (data: ChildCreate) => api.post<Child>('/children', data),

  update: (id: string, data: Partial<ChildCreate>) =>
    api.patch<Child>(`/children/${id}`, data),

  getDDT: (id: string) =>
    api.get<{ child: Child; ddt: DDTSnapshot | null; pdrs: PDRSScore | null; recent_observations: Observation[] }>(
      `/children/${id}/ddt`
    ),

  generateDDT: (id: string) =>
    api.post<DDTSnapshot>(`/children/${id}/ddt/generate`),

  uploadPhoto: (id: string, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post<{ photo_url: string }>(`/children/${id}/photo`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

/* ─── ATTENDANCE ─────────────────────────────── */
export const attendanceApi = {
  getToday: (awcId: number) =>
    api.get('/attendance/today', { params: { awc_id: awcId } }),

  mark: (entries: Array<{ child_id: string; present: boolean; date?: string }>) =>
    api.post('/attendance/bulk', { entries }),
};

/* ─── OBSERVATIONS ───────────────────────────── */
export const observationsApi = {
  listForChild: (childId: string) =>
    api.get<Observation[]>('/observations', { params: { child_id: childId } }),

  submitText: (data: { child_id: string; raw_text: string; language?: string }) =>
    api.post<Observation>('/observations/text', data),

  submitVoice: (childId: string, audioBlob: Blob) => {
    const form = new FormData();
    form.append('audio', audioBlob, 'recording.webm');
    form.append('child_id', childId);
    return api.post<Observation>('/observations/voice', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

/* ─── MILESTONES ─────────────────────────────── */
export const milestonesApi = {
  library: (ageMonths?: number) =>
    api.get<Milestone[]>('/milestones/library', { params: { age_months: ageMonths } }),

  forChild: (childId: string) =>
    api.get<MilestoneAssessment[]>(`/milestones/child/${childId}/due`),

  assess: (childId: string, assessments: Array<{ milestone_id: number; result: string; notes?: string }>) =>
    api.post(`/milestones/child/${childId}/assess`, { assessments }),
};

/* ─── PDRS ───────────────────────────────────── */
export const pdrsApi = {
  compute: (childId: string) =>
    api.post<PDRSScore>(`/pdrs/compute/${childId}`),

  getLatest: (childId: string) =>
    api.get<PDRSScore>(`/pdrs/child/${childId}/latest`),

  history: (childId: string) =>
    api.get<PDRSScore[]>(`/pdrs/child/${childId}/history`),
};

/* ─── DRAWINGS ───────────────────────────────── */
export const drawingsApi = {
  list: (childId: string) =>
    api.get<Drawing[]>('/drawings', { params: { child_id: childId } }),

  upload: (childId: string, file: File, context = 'free_drawing') => {
    const form = new FormData();
    form.append('file', file);
    form.append('child_id', childId);
    form.append('context', context);
    return api.post<Drawing>('/drawings/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  analyze: (drawingId: string) =>
    api.post<DrawingAnalysis>(`/drawings/${drawingId}/analyze`),
};

import type { DrawingAnalysis } from './types';

/* ─── REFERRALS ──────────────────────────────── */
export const referralsApi = {
  list: (childId?: string) =>
    api.get<Referral[]>('/referrals', { params: { child_id: childId } }),

  create: (data: {
    child_id: string; primary_concern: string;
    domains_of_concern: string[]; facility_id?: number;
  }) => api.post<Referral>('/referrals', data),

  updateStatus: (id: string, status: string, notes?: string) =>
    api.patch<Referral>(`/referrals/${id}/status`, { status, outcome_notes: notes }),

  downloadLetter: (id: string) =>
    api.get(`/referrals/${id}/letter`, { responseType: 'blob' }),

  schemes: (childId: string) =>
    api.get<GovernmentScheme[]>(`/referrals/schemes/${childId}`),
};

/* ─── RECOMMENDATIONS ────────────────────────── */
export const recommendationsApi = {
  list: (childId: string) =>
    api.get<Recommendation[]>('/recommendations', { params: { child_id: childId } }),

  generate: (childId: string) =>
    api.post<Recommendation[]>(`/recommendations/generate/${childId}`),
};

/* ─── DASHBOARD ──────────────────────────────── */
export const dashboardApi = {
  aww: () => api.get<AWWDashboard>('/dashboard/aww'),
  cdpo: () => api.get<CDPODashboard>('/dashboard/cdpo'),
  overview: () => api.get('/dashboard/overview'),
  heatmap: (districtId: number) =>
    api.get(`/dashboard/district/${districtId}/heatmap`),
};
