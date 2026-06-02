'use client';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { PageHeader } from '@/components/shared/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/EmptyState';
import { Building2, Users, AlertCircle, MapPin } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function AWCsPage() {
  const { user } = useAuthStore();
  const districtId = user?.district_id ?? 1;

  const { data, isLoading } = useQuery({
    queryKey: ['heatmap', districtId],
    queryFn: () => dashboardApi.heatmap(districtId).then(r => r.data),
  });

  const awcs = data?.awc_points ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="AWC Centres"
        description={`${data?.district_name ?? 'District'} · ${awcs.length} centres`}
      />

      {isLoading ? (
        <div className="grid sm:grid-cols-2 gap-4">
          {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-32 rounded-2xl" />)}
        </div>
      ) : awcs.length === 0 ? (
        <EmptyState icon={<Building2 className="h-8 w-8" />} title="No AWCs found" description="AWC data will appear here" />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {awcs.map((awc: any) => (
            <Card key={awc.awc_id} className={cn(
              'border-l-4',
              awc.risk_level === 'RED' ? 'border-l-red-400' :
              awc.risk_level === 'AMBER' ? 'border-l-amber-400' :
              awc.risk_level === 'GREEN' ? 'border-l-green-400' : 'border-l-border'
            )}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <Building2 className="h-5 w-5 text-brand-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">{awc.awc_name}</p>
                      {awc.latitude && (
                        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                          <MapPin className="h-3 w-3" />
                          {awc.latitude.toFixed(4)}, {awc.longitude?.toFixed(4)}
                        </p>
                      )}
                    </div>
                  </div>
                  {awc.risk_level && (
                    <Badge
                      variant={awc.risk_level === 'RED' ? 'red' : awc.risk_level === 'AMBER' ? 'amber' : 'green'}
                      className="text-xs shrink-0"
                    >
                      {awc.risk_level}
                    </Badge>
                  )}
                </div>

                <div className="mt-3 flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1.5 text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>{awc.total_children} children</span>
                  </div>
                  {awc.avg_pdrs_score != null && (
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <AlertCircle className="h-4 w-4" />
                      <span>Avg {awc.avg_pdrs_score} PDRS</span>
                    </div>
                  )}
                </div>

                <div className="mt-3 flex gap-3">
                  <div className="flex items-center gap-1 text-xs">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
                    <span>{awc.red_count}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs">
                    <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                    <span>{awc.amber_count}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs">
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
                    <span>{awc.green_count}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
