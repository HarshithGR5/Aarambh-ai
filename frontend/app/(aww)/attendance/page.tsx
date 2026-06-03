'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { childrenApi, attendanceApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { AttendanceGrid } from '@/components/aww/AttendanceGrid';
import { PageHeader } from '@/components/shared/PageHeader';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { toast } from 'sonner';
import { formatDate } from '@/lib/utils';
import type { Child } from '@/lib/types';

export default function AttendancePage() {
  const { user } = useAuthStore();
  const qc = useQueryClient();
  const today = new Date().toISOString().split('T')[0];

  const { data: children = [], isLoading } = useQuery({
    queryKey: ['children', user?.awc_id],
    queryFn: () => childrenApi.list(user?.awc_id).then(r => r.data),
  });

  const { data: todayAttendance } = useQuery({
    queryKey: ['attendance', 'today', user?.awc_id],
    queryFn: () => attendanceApi.getToday(user?.awc_id ?? 0).then(r => r.data),
    enabled: !!user?.awc_id,
  });

  const initialPresent: Record<string, boolean> = {};
  if (Array.isArray(todayAttendance)) {
    todayAttendance.forEach((a: { child_id: string; present: boolean }) => {
      initialPresent[a.child_id] = a.present;
    });
  }

  const mutation = useMutation({
    mutationFn: (attendance: Record<string, boolean>) => {
      const entries = Object.entries(attendance).map(([child_id, present]) => ({
        child_id, present, date: today,
      }));
      return attendanceApi.mark(entries);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['attendance'] });
      toast.success('Attendance saved!');
    },
    onError: () => toast.error('Failed to save attendance.'),
  });

  if (isLoading) return <PageLoader text="Loading children…" />;

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader
        title="Attendance"
        description={`Today · ${formatDate(today)}`}
      />
      <AttendanceGrid
        children={children as Child[]}
        initialPresent={initialPresent}
        onSave={async (att) => { await mutation.mutateAsync(att); }}
        loading={mutation.isPending}
      />
    </div>
  );
}
