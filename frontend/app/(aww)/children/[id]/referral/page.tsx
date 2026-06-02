'use client';
import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { childrenApi, referralsApi } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { FileText, Download, CheckCircle2, AlertTriangle, ExternalLink } from 'lucide-react';
import type { GovernmentScheme, Referral } from '@/lib/types';
import { DOMAIN_META, formatDate } from '@/lib/utils';

const DOMAIN_OPTIONS = Object.entries(DOMAIN_META).map(([k, v]) => ({ value: k, label: v.label }));

export default function ReferralPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();
  const [primaryConcern, setPrimaryConcern] = useState('');
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [created, setCreated] = useState<Referral | null>(null);

  const { data: child } = useQuery({
    queryKey: ['child', id],
    queryFn: () => childrenApi.getDDT(id).then(r => r.data.child),
  });

  const { data: schemes = [] } = useQuery({
    queryKey: ['schemes', id],
    queryFn: () => referralsApi.schemes(id).then(r => r.data),
    enabled: !!id,
  });

  const { data: existingReferrals = [] } = useQuery({
    queryKey: ['referrals', id],
    queryFn: () => referralsApi.list(id).then(r => r.data),
    enabled: !!id,
  });

  const createMutation = useMutation({
    mutationFn: () => referralsApi.create({
      child_id: id,
      primary_concern: primaryConcern,
      domains_of_concern: selectedDomains,
    }),
    onSuccess: (res) => {
      setCreated(res.data);
      qc.invalidateQueries({ queryKey: ['referrals', id] });
      toast.success('Referral letter generated!');
    },
    onError: () => toast.error('Failed to create referral.'),
  });

  const toggleDomain = (domain: string) => {
    setSelectedDomains(d => d.includes(domain) ? d.filter(x => x !== domain) : [...d, domain]);
  };

  const downloadLetter = async (referralId: string) => {
    try {
      const res = await referralsApi.downloadLetter(referralId);
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `referral_${referralId.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error('Failed to download letter.');
    }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader title="Referral" description={child?.full_name} backHref={`/children/${id}`} />

      {created ? (
        <div className="space-y-4">
          <Card className="border-green-200 bg-green-50/50">
            <CardContent className="p-5 text-center space-y-3">
              <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto" />
              <h3 className="font-bold text-lg">Referral Created</h3>
              <p className="text-sm text-muted-foreground">
                Referral letter generated for {child?.full_name}
              </p>
              <div className="flex gap-3 justify-center flex-wrap">
                <Button className="gap-2" onClick={() => downloadLetter(created.id)}>
                  <Download className="h-4 w-4" /> Download PDF
                </Button>
                <Button variant="outline" onClick={() => router.push(`/children/${id}`)}>
                  Back to Profile
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Government Schemes */}
          {schemes.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="text-base flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600" /> Eligible Schemes
              </CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {schemes.map((scheme: GovernmentScheme) => (
                  <div key={scheme.id} className="p-3 rounded-xl bg-green-50 border border-green-100">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-semibold text-sm text-green-800">{scheme.name}</p>
                        <p className="text-xs text-green-600 mt-0.5">{scheme.ministry}</p>
                        <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{scheme.description}</p>
                      </div>
                      {scheme.apply_url && (
                        <a href={scheme.apply_url} target="_blank" rel="noopener noreferrer">
                          <Button size="sm" variant="ghost" className="h-7 shrink-0">
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Create Referral */}
          <Card>
            <CardHeader><CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4 text-amber-600" /> Generate Referral Letter
            </CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Primary Concern *</Label>
                <Input
                  placeholder="e.g. Speech delay, motor delay, social withdrawal…"
                  value={primaryConcern}
                  onChange={e => setPrimaryConcern(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Domains of Concern (select all that apply)</Label>
                <div className="flex flex-wrap gap-2">
                  {DOMAIN_OPTIONS.map(d => (
                    <button
                      key={d.value}
                      onClick={() => toggleDomain(d.value)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                        selectedDomains.includes(d.value)
                          ? 'bg-brand-100 text-brand-700 border-brand-300'
                          : 'bg-background text-muted-foreground border-border hover:bg-muted/50'
                      }`}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                className="w-full gap-2"
                size="lg"
                loading={createMutation.isPending}
                disabled={!primaryConcern.trim()}
                onClick={() => createMutation.mutate()}
              >
                <FileText className="h-4 w-4" /> Generate Referral Letter
              </Button>
            </CardContent>
          </Card>

          {/* Existing referrals */}
          {existingReferrals.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Past Referrals</h3>
              {existingReferrals.map((ref: Referral) => (
                <Card key={ref.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold">{ref.primary_concern}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">{formatDate(ref.referral_date)}</p>
                        <Badge
                          variant={ref.status === 'ASSESSED' ? 'green' : ref.status === 'PENDING' ? 'amber' : 'secondary'}
                          className="mt-1.5 text-xs"
                        >
                          {ref.status}
                        </Badge>
                      </div>
                      {ref.letter_url && (
                        <Button size="sm" variant="ghost" onClick={() => downloadLetter(ref.id)}>
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
