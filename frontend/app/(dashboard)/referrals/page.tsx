'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { referralsApi } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import { FileText, Download, CheckCircle2 } from 'lucide-react';
import type { Referral } from '@/lib/types';
import { useState } from 'react';

const STATUS_OPTIONS = ['PENDING', 'CONTACTED', 'ASSESSED', 'CLOSED', 'CANCELLED'];

export default function ReferralsPage() {
  const qc = useQueryClient();
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const { data: referrals = [], isLoading } = useQuery({
    queryKey: ['referrals-all'],
    queryFn: () => referralsApi.list().then(r => r.data),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      referralsApi.updateStatus(id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['referrals-all'] });
      toast.success('Status updated');
    },
  });

  const downloadLetter = async (id: string) => {
    try {
      const res = await referralsApi.downloadLetter(id);
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `referral_${id.slice(0, 8)}.pdf`;
      a.click();
    } catch { toast.error('Download failed'); }
  };

  const filtered = filterStatus === 'ALL'
    ? referrals
    : referrals.filter((r: Referral) => r.status === filterStatus);

  const statusVariant = (s: string) =>
    s === 'ASSESSED' ? 'green' : s === 'PENDING' ? 'amber' : s === 'CANCELLED' ? 'red' : 'secondary';

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Referral Management"
        description={`${referrals.length} total referrals`}
      />

      {/* Filter */}
      <div className="flex gap-3 flex-wrap">
        {['ALL', ...STATUS_OPTIONS].map(s => (
          <button
            key={s}
            onClick={() => setFilterStatus(s)}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
              filterStatus === s
                ? 'bg-brand-100 text-brand-700 border-brand-300'
                : 'bg-background text-muted-foreground border-border hover:bg-muted/50'
            }`}
          >
            {s} {s === 'ALL' ? `(${referrals.length})` : `(${referrals.filter((r: Referral) => r.status === s).length})`}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={<FileText className="h-8 w-8" />} title="No referrals" description="Referrals will appear here" />
      ) : (
        <div className="space-y-3">
          {filtered.map((ref: Referral) => (
            <Card key={ref.id}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="font-semibold">{ref.child_name ?? 'Child'}</p>
                      <Badge variant={statusVariant(ref.status) as any} className="text-xs">{ref.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{ref.primary_concern}</p>
                    <p className="text-xs text-muted-foreground mt-1">Referred: {formatDate(ref.referral_date)}</p>
                    {ref.domains_of_concern?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {ref.domains_of_concern.map(d => (
                          <Badge key={d} variant="secondary" className="text-xs">{d.replace(/_/g, ' ')}</Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    {ref.letter_url && (
                      <Button size="sm" variant="outline" className="gap-1" onClick={() => downloadLetter(ref.id)}>
                        <Download className="h-3.5 w-3.5" /> PDF
                      </Button>
                    )}
                    <Select
                      value={ref.status}
                      onValueChange={(v) => statusMutation.mutate({ id: ref.id, status: v })}
                    >
                      <SelectTrigger className="h-8 text-xs w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {STATUS_OPTIONS.map(s => (
                          <SelectItem key={s} value={s} className="text-xs">{s}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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
