'use client';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, childrenApi, referralsApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { StatCard } from '@/components/shared/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/shared/PageHeader';
import { Skeleton } from '@/components/ui/skeleton';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { formatDate } from '@/lib/utils';
import { Users, Building2, FileText, TrendingUp, AlertCircle, ArrowRight, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

const DEMO_OVERVIEW = { total_children: 847, total_awcs: 24, total_referrals: 38, avg_pdrs_score: 71 };
const DEMO_CDPO = {
  block_name: 'Demo Block (API offline)',
  total_awcs: 24, total_children: 847,
  green_zone_children: 612, amber_zone_children: 178, red_zone_children: 57,
  referrals_this_month: 14, referral_completion_rate: 71, inactive_awws: 2,
};
const DEMO_CHILDREN = [
  { id: 1, full_name: 'Aarav Sharma',    age_years: 3, age_months_remainder: 4, latest_risk_level: 'GREEN', latest_pdrs_score: 84 },
  { id: 2, full_name: 'Priya Nair',      age_years: 2, age_months_remainder: 8, latest_risk_level: 'AMBER', latest_pdrs_score: 61 },
  { id: 3, full_name: 'Rohan Patel',     age_years: 4, age_months_remainder: 1, latest_risk_level: 'GREEN', latest_pdrs_score: 79 },
  { id: 4, full_name: 'Ananya Reddy',    age_years: 1, age_months_remainder: 11, latest_risk_level: 'RED',  latest_pdrs_score: 38 },
  { id: 5, full_name: 'Vikram Iyer',     age_years: 5, age_months_remainder: 2, latest_risk_level: 'GREEN', latest_pdrs_score: 91 },
];
const DEMO_REFERRALS = [
  { id: 1, child_name: 'Ananya Reddy',   primary_concern: 'Motor delay', referral_date: '2025-05-20', status: 'PENDING' },
  { id: 2, child_name: 'Priya Nair',     primary_concern: 'Speech delay', referral_date: '2025-05-18', status: 'ASSESSED' },
  { id: 3, child_name: 'Suresh Kumar',   primary_concern: 'Vision concern', referral_date: '2025-05-12', status: 'PENDING' },
];

export default function OverviewPage() {
  const { user } = useAuthStore();

  const { data: overviewData, isError: overviewErr } = useQuery({
    queryKey: ['overview'],
    queryFn: () => dashboardApi.overview().then(r => r.data),
    retry: 1,
  });

  const { data: cdpoData, isError: cdpoErr } = useQuery({
    queryKey: ['cdpo-dashboard'],
    queryFn: () => dashboardApi.cdpo().then(r => r.data),
    enabled: (user as any)?.role !== 'AWW',
    retry: 1,
  });

  const { data: recentChildren = [], isError: childrenErr } = useQuery({
    queryKey: ['children-recent'],
    queryFn: () => childrenApi.list(undefined, 5).then(r => r.data),
    retry: 1,
  });

  const { data: recentReferrals = [], isError: referralsErr } = useQuery({
    queryKey: ['referrals-recent'],
    queryFn: () => referralsApi.list().then(r => r.data.slice(0, 5)),
    retry: 1,
  });

  const overview = overviewData ?? (overviewErr ? DEMO_OVERVIEW : null);
  const cdpo     = cdpoData ?? (cdpoErr ? DEMO_CDPO : null);
  const children = (recentChildren.length > 0 ? recentChildren : (childrenErr ? DEMO_CHILDREN : [])) as typeof DEMO_CHILDREN;
  const referrals = (recentReferrals.length > 0 ? recentReferrals : (referralsErr ? DEMO_REFERRALS : [])) as typeof DEMO_REFERRALS;

  const anyError = overviewErr || cdpoErr;

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title="Overview Dashboard"
        description={`${(user as any)?.role ?? ''} · ${cdpo?.block_name ?? ''}`}
      />

      {anyError && (
        <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded-xl px-4 py-3">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Backend offline — showing demo data. Connect the API server to see live data.
        </div>
      )}

      {/* Stats */}
      {overview ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Children"    value={overview.total_children ?? 0}  icon={<Users className="h-5 w-5" />}    color="blue" />
          <StatCard title="AWC Centres"       value={overview.total_awcs ?? 0}       icon={<Building2 className="h-5 w-5" />} color="purple" />
          <StatCard title="Total Referrals"   value={overview.total_referrals ?? 0}  icon={<FileText className="h-5 w-5" />} color="amber" />
          {cdpo && <StatCard title="Referral Completion" value={`${cdpo.referral_completion_rate}%`} icon={<TrendingUp className="h-5 w-5" />} color="green" />}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
        </div>
      )}

      {cdpo && (
        <div className="grid sm:grid-cols-3 gap-4">
          <StatCard title="High Risk Children" value={cdpo.red_zone_children}   icon={<AlertCircle className="h-5 w-5" />} color="red" />
          <StatCard title="Monitoring"          value={cdpo.amber_zone_children} color="amber" />
          <StatCard title="On Track"            value={cdpo.green_zone_children} color="green" />
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Children */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Children</CardTitle>
              <Link href="/children">
                <Button variant="ghost" size="sm" className="gap-1 text-xs">View All <ArrowRight className="h-3 w-3" /></Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {children.slice(0, 5).map((child) => (
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
            {children.length === 0 && <p className="text-sm text-muted-foreground text-center py-6">No children yet</p>}
          </CardContent>
        </Card>

        {/* Recent Referrals */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Referrals</CardTitle>
              <Link href="/referrals">
                <Button variant="ghost" size="sm" className="gap-1 text-xs">View All <ArrowRight className="h-3 w-3" /></Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {referrals.length > 0 ? referrals.map((ref) => (
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
