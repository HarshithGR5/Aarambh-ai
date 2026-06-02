import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatAge(ageMonths: number): string {
  const years = Math.floor(ageMonths / 12);
  const months = ageMonths % 12;
  if (years === 0) return `${months}m`;
  if (months === 0) return `${years}y`;
  return `${years}y ${months}m`;
}

export function calcAgeMonths(dob: string): number {
  const birth = new Date(dob);
  const now = new Date();
  return (
    (now.getFullYear() - birth.getFullYear()) * 12 +
    (now.getMonth() - birth.getMonth())
  );
}

export function getRiskColor(level: string | null | undefined): string {
  if (level === 'RED') return 'text-red-600';
  if (level === 'AMBER') return 'text-amber-600';
  return 'text-green-600';
}

export function getRiskBg(level: string | null | undefined): string {
  if (level === 'RED') return 'bg-red-50 border-red-200 text-red-700';
  if (level === 'AMBER') return 'bg-amber-50 border-amber-200 text-amber-700';
  return 'bg-green-50 border-green-200 text-green-700';
}

export function getRiskLabel(level: string | null | undefined): string {
  if (level === 'RED') return 'High Risk';
  if (level === 'AMBER') return 'Moderate Risk';
  if (level === 'GREEN') return 'On Track';
  return 'Not Assessed';
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
}

export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export const DOMAIN_META: Record<string, { label: string; color: string; bg: string }> = {
  PHYSICAL_MOTOR:     { label: 'Physical & Motor',         color: '#FF6B6B', bg: 'bg-red-50' },
  LANGUAGE_LITERACY:  { label: 'Language & Literacy',      color: '#4ECDC4', bg: 'bg-teal-50' },
  COGNITIVE:          { label: 'Cognitive',                color: '#45B7D1', bg: 'bg-sky-50' },
  SOCIAL_EMOTIONAL:   { label: 'Social-Emotional',         color: '#96CEB4', bg: 'bg-green-50' },
  AESTHETIC_CULTURAL: { label: 'Aesthetic & Cultural',     color: '#F4C430', bg: 'bg-yellow-50' },
  LEARNING_HABITS:    { label: 'Positive Learning Habits', color: '#DDA0DD', bg: 'bg-purple-50' },
};
