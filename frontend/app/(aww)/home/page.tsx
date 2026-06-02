'use client';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { dashboardApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { StatCard } from '@/components/shared/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDate, getRiskBg } from '@/lib/utils';
import {
  Users, CheckCircle2, AlertTriangle, AlertCircle,
  ArrowRight, CalendarCheck2, Mic, Target,
  Brain, Pencil, BookOpen, FileText,
} from 'lucide-react';

export default function AWWHomePage() {
  const { user } = useAuthStore();
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', 'aww'],
    queryFn: () => dashboardApi.aww().then(r => r.data),
  });

  if (isLoading) return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-2 gap-3">
        {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
      </div>
      <Skeleton className="h-48 rounded-2xl" />
    </div>
  );

  if (!data) return null;

  const { stats, alerts, today_actions, awc } = data;
  const greeting = new Date().getHours() < 12 ? 'Good Morning' : new Date().getHours() < 17 ? 'Good Afternoon' : 'Good Evening';

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {greeting}, {user?.name?.split(' ')[0]} 👋
        </h1>
        {awc && <p className="text-sm text-muted-foreground mt-0.5">{awc.name} · {formatDate(data.today_date)}</p>}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard
          title="Children"
          value={stats.total_children}
          subtitle={`${stats.present_today} present today`}
          icon={<Users className="h-5 w-5" />}
          color="blue"
        />
        <StatCard
          title="On Track"
          value={stats.green_zone_children}
          subtitle="Green zone"
          icon={<CheckCircle2 className="h-5 w-5" />}
          color="green"
        />
        <StatCard
          title="Monitoring"
          value={stats.amber_zone_children}
          subtitle="Needs attention"
          icon={<AlertTriangle className="h-5 w-5" />}
          color="amber"
        />
        <StatCard
          title="High Risk"
          value={stats.red_zone_children}
          subtitle="Action needed"
          icon={<AlertCircle className="h-5 w-5" />}
          color="red"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-3">
        <Link href="/attendance">
          <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-brand-50 border border-brand-100 hover:bg-brand-100 transition-colors active:scale-[0.98]">
            <CalendarCheck2 className="h-6 w-6 text-brand-600" />
            <span className="text-xs font-semibold text-brand-700 text-center">Attendance</span>
          </div>
        </Link>
        <Link href="/children">
          <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-purple-50 border border-purple-100 hover:bg-purple-100 transition-colors active:scale-[0.98]">
            <Mic className="h-6 w-6 text-purple-600" />
            <span className="text-xs font-semibold text-purple-700 text-center">Observe</span>
          </div>
        </Link>
        <Link href="/children">
          <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-green-50 border border-green-100 hover:bg-green-100 transition-colors active:scale-[0.98]">
            <Target className="h-6 w-6 text-green-600" />
            <span className="text-xs font-semibold text-green-700 text-center">Milestones</span>
          </div>
        </Link>
      </div>

      {/* AI-Powered Tools */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Brain className="h-4 w-4 text-brand-600" /> AI-Powered Tools
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-2 pt-0">
          <Link href="/children">
            <div className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-purple-50 border border-purple-100 hover:bg-purple-100 transition-colors active:scale-[0.98]">
              <Mic className="h-5 w-5 text-purple-600" />
              <span className="text-xs font-semibold text-purple-700 text-center">Voice Observe</span>
              <span className="text-[10px] text-purple-500 text-center leading-tight">Any Indian language</span>
            </div>
          </Link>
          <Link href="/children">
            <div className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-blue-50 border border-blue-100 hover:bg-blue-100 transition-colors active:scale-[0.98]">
              <Pencil className="h-5 w-5 text-blue-600" />
              <span className="text-xs font-semibold text-blue-700 text-center">Drawing AI</span>
              <span className="text-[10px] text-blue-500 text-center leading-tight">GPT-4 Vision analysis</span>
            </div>
          </Link>
          <Link href="/children">
            <div className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-green-50 border border-green-100 hover:bg-green-100 transition-colors active:scale-[0.98]">
              <BookOpen className="h-5 w-5 text-green-600" />
              <span className="text-xs font-semibold text-green-700 text-center">Milestones</span>
              <span className="text-[10px] text-green-500 text-center leading-tight">WHO + NCERT tracking</span>
            </div>
          </Link>
          <Link href="/children">
            <div className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-amber-50 border border-amber-100 hover:bg-amber-100 transition-colors active:scale-[0.98]">
              <FileText className="h-5 w-5 text-amber-600" />
              <span className="text-xs font-semibold text-amber-700 text-center">AI Referral</span>
              <span className="text-[10px] text-amber-500 text-center leading-tight">RBSK / NPPCD letters</span>
            </div>
          </Link>
        </CardContent>
      </Card>

      {/* Today's Priorities */}
      {today_actions.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Today's Priorities</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 pt-0">
            {today_actions.map((action, i) => (
              <Link key={i} href={`/children/${action.child_id}`}>
                <div className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/50 transition-colors border border-border/50">
                  <div className="flex items-center gap-3">
                    <div className="h-7 w-7 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">
                      {action.priority}
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{action.child_name}</p>
                      <p className="text-xs text-muted-foreground">{action.action.replace(/_/g, ' ')}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" /> Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 pt-0">
            {alerts.map((alert, i) => (
              <Link key={i} href={`/children/${alert.child_id}`}>
                <div className="flex items-start gap-3 p-3 rounded-xl border border-amber-100 bg-amber-50/50 hover:bg-amber-50 transition-colors">
                  <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-foreground">{alert.child_name}</p>
                    <p className="text-xs text-amber-700 mt-0.5">
                      {alert.type === 'NO_OBSERVATION' && `No observation for ${alert.days_ago} days`}
                      {alert.type === 'HIGH_RISK_NEW' && `High risk · PDRS ${alert.pdrs_score}`}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      )}

      {/* View all children */}
      <Link href="/children">
        <Button variant="outline" className="w-full gap-2">
          View All Children <ArrowRight className="h-4 w-4" />
        </Button>
      </Link>
    </div>
  );
}
