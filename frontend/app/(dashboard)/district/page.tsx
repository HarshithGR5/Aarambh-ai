'use client';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/store';
import { dashboardApi } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatCard } from '@/components/shared/StatCard';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { MapPin, Building2, AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function DistrictHeatmapPage() {
  const { user } = useAuthStore();
  const districtId = user?.district_id ?? 1;

  const { data, isLoading } = useQuery({
    queryKey: ['heatmap', districtId],
    queryFn: () => dashboardApi.heatmap(districtId).then(r => r.data),
  });

  const awcPoints = data?.awc_points ?? [];
  const redCount = awcPoints.filter((p: any) => p.risk_level === 'RED').length;
  const amberCount = awcPoints.filter((p: any) => p.risk_level === 'AMBER').length;
  const greenCount = awcPoints.filter((p: any) => p.risk_level === 'GREEN').length;

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader title="District Heatmap" description={`${data?.district_name ?? 'District'} · Risk distribution by AWC`} />

      {isLoading ? (
        <div className="grid sm:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid sm:grid-cols-3 gap-4">
          <StatCard title="High Risk AWCs" value={redCount} icon={<AlertCircle className="h-5 w-5" />} color="red" />
          <StatCard title="Monitoring AWCs" value={amberCount} icon={<AlertTriangle className="h-5 w-5" />} color="amber" />
          <StatCard title="Healthy AWCs" value={greenCount} icon={<CheckCircle2 className="h-5 w-5" />} color="green" />
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin className="h-4 w-4 text-brand-600" /> AWC Risk Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-16 rounded-xl" />)}
            </div>
          ) : awcPoints.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-12">No AWC data available</p>
          ) : (
            <div className="space-y-2">
              {awcPoints.map((awc: any) => (
                <div
                  key={awc.awc_id}
                  className={cn(
                    'flex items-center justify-between p-4 rounded-xl border transition-colors hover:shadow-sm',
                    awc.risk_level === 'RED'   ? 'border-red-200 bg-red-50/50' :
                    awc.risk_level === 'AMBER' ? 'border-amber-200 bg-amber-50/50' :
                    awc.risk_level === 'GREEN' ? 'border-green-200 bg-green-50/50' :
                    'border-border bg-muted/20'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Building2 className={cn(
                      'h-5 w-5',
                      awc.risk_level === 'RED' ? 'text-red-500' :
                      awc.risk_level === 'AMBER' ? 'text-amber-500' :
                      'text-green-500'
                    )} />
                    <div>
                      <p className="font-semibold text-sm">{awc.awc_name}</p>
                      <p className="text-xs text-muted-foreground">{awc.total_children} children</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-right">
                    {awc.avg_pdrs_score != null && (
                      <div>
                        <p className="text-xs text-muted-foreground">Avg PDRS</p>
                        <p className={cn('font-bold text-sm',
                          awc.risk_level === 'RED' ? 'text-red-600' :
                          awc.risk_level === 'AMBER' ? 'text-amber-600' : 'text-green-600'
                        )}>{awc.avg_pdrs_score}</p>
                      </div>
                    )}
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-1 text-xs">
                        <span className="w-2 h-2 rounded-full bg-red-500" />{awc.red_count}
                        <span className="w-2 h-2 rounded-full bg-amber-500 ml-1" />{awc.amber_count}
                        <span className="w-2 h-2 rounded-full bg-green-500 ml-1" />{awc.green_count}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
