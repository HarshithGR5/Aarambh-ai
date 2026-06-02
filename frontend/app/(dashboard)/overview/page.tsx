'use client';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, childrenApi, referralsApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { StatCard } from '@/components/shared/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/shared/PageHeader';
import { Skeleton } from '@/components/ui/skeleton';
import { DDTRadarChart } from '@/components/ddt/RadarChart';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { formatDate } from '@/lib/utils';
import { Users, Building2, FileText, TrendingUp, AlertCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function OverviewPage() {
  const { user } = useAuthStore();

  const { data: overview } = useQuery({
    queryKey: ['overview'],
    queryFn: () => dashboardApi.overview().then(r => r.data),
  });

  const { data: cdpo } = useQuery({
    queryKey: ['cdpo-dashboard'],
    queryFn: () => dashboardApi.cdpo().then(r => r.data),
    enabled: user?.role !== 'AWW',
  });

  const { data: recentChildren = [] } = useQuery({
    queryKey: ['children-recent'],
    queryFn: () => childrenApi.list(undefined, 5).then(r => r.data),
  });

  const { data: recentReferrals = [] } = useQuery({
    queryKey: ['referrals-recent'],
    queryFn: () => referralsApi.list().then(r => r.data.slice(0, 5)),
  });

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title="Overview Dashboard"
        description={`${user?.role} · ${cdpo?.block_name ?? ''}`}
      />

      {/* Stats */}
      {overview ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Children" value={overview.total_children ?? 0} icon={<Users className="h-5 w-5" />} color="blue" />
          <StatCard title="AWC Centres" value={overview.total_awcs ?? 0} icon={<Building2 className="h-5 w-5" />} color="purple" />
          <StatCard title="Total Referrals" value={overview.total_referrals ?? 0} icon={<FileText className="h-5 w-5" />} color="amber" />
          {cdpo && <StatCard title="Referral Completion" value={`${cdpo.referral_completion_rate}%`} icon={<TrendingUp className="h-5 w-5" />} color="green" />}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
        </div>
      )}

      {cdpo && (
        <div className="grid sm:grid-cols-3 gap-4">
          <StatCard title="High Risk Children" value={cdpo.red_zone_children} icon={<AlertCircle className="h-5 w-5" />} color="red" />
          <StatCard title="Monitoring" value={cdpo.amber_zone_children} color="amber" />
          <StatCard title="On Track" value={cdpo.green_zone_children} color="green" />
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Children */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Children</CardTitle>
              <Link href="/children"><Button variant="ghost" size="sm" className="gap-1 text-xs">View All <ArrowRight className="h-3 w-3" /></Button></Link>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentChildren.slice(0, 5).map((child: any) => (
              <Link key={child.id} href={`/children/${child.id}`}>
                <div className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/50 transition-colors">
                  <div>
                    <p className="text-sm font-semibold">{child.full_name}</p>
                    <p className="text-xs text-muted-foreground">{child.age_years}y {child.age_months_remainder}m</p>
                  </div>
                  <RiskBadge level={child.latest_risk_level} score={child.latest_pdrs_score} />
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>

        {/* Recent Referrals */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Referrals</CardTitle>
              <Link href="/referrals"><Button variant="ghost" size="sm" className="gap-1 text-xs">View All <ArrowRight className="h-3 w-3" /></Button></Link>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentReferrals.length > 0 ? recentReferrals.map((ref: any) => (
              <div key={ref.id} className="flex items-start justify-between p-3 rounded-xl border">
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate">{ref.child_name ?? ref.primary_concern}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(ref.referral_date)}</p>
                </div>
                <Badge
                  variant={ref.status === 'ASSESSED' ? 'green' : ref.status === 'PENDING' ? 'amber' : 'secondary'}
                  className="text-xs shrink-0"
                >
                  {ref.status}
                </Badge>
              </div>
            )) : (
              <p className="text-sm text-muted-foreground text-center py-6">No referrals yet</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
