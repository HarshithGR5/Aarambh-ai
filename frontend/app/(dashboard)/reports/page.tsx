'use client';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, childrenApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { PageHeader } from '@/components/shared/PageHeader';
import { StatCard } from '@/components/shared/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { DDTRadarChart } from '@/components/ddt/RadarChart';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { BarChart3, TrendingUp, Users, AlertCircle } from 'lucide-react';

const COLORS = ['#16a34a', '#d97706', '#dc2626'];

export default function ReportsPage() {
  const { user } = useAuthStore();

  const { data: cdpo } = useQuery({
    queryKey: ['cdpo-dashboard'],
    queryFn: () => dashboardApi.cdpo().then(r => r.data),
  });

  const { data: children = [] } = useQuery({
    queryKey: ['children-all'],
    queryFn: () => childrenApi.list().then(r => r.data),
  });

  const riskData = [
    { name: 'On Track', value: cdpo?.green_zone_children ?? 0, color: '#16a34a' },
    { name: 'Monitor',  value: cdpo?.amber_zone_children ?? 0, color: '#d97706' },
    { name: 'High Risk', value: cdpo?.red_zone_children ?? 0, color: '#dc2626' },
  ].filter(d => d.value > 0);

  const ageGroups: Record<string, number> = {};
  (children as any[]).forEach(c => {
    const group = `${Math.floor(c.age_months / 12) * 12}-${Math.floor(c.age_months / 12) * 12 + 11}m`;
    ageGroups[group] = (ageGroups[group] ?? 0) + 1;
  });
  const ageData = Object.entries(ageGroups).map(([name, count]) => ({ name, count })).sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader title="Analytics & Reports" description="Block-level developmental statistics" />

      {cdpo ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Children" value={cdpo.total_children} icon={<Users className="h-5 w-5" />} color="blue" />
          <StatCard title="AWC Centres" value={cdpo.total_awcs} color="purple" />
          <StatCard title="Referrals This Month" value={cdpo.referrals_this_month} icon={<TrendingUp className="h-5 w-5" />} color="amber" />
          <StatCard title="Completion Rate" value={`${cdpo.referral_completion_rate}%`} color="green" />
        </div>
      ) : (
        <div className="grid sm:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Risk Distribution Pie */}
        <Card>
          <CardHeader><CardTitle className="text-base">Risk Distribution</CardTitle></CardHeader>
          <CardContent>
            {riskData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={riskData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                    {riskData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Tooltip formatter={(val) => [`${val} children`, '']} />
                </PieChart>
              </ResponsiveContainer>
            ) : <p className="text-sm text-muted-foreground text-center py-10">No data yet</p>}
          </CardContent>
        </Card>

        {/* Age Distribution Bar */}
        <Card>
          <CardHeader><CardTitle className="text-base">Children by Age Group</CardTitle></CardHeader>
          <CardContent>
            {ageData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={ageData} barSize={32}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0d8ee8" radius={[6, 6, 0, 0]} name="Children" />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="text-sm text-muted-foreground text-center py-10">No data yet</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
