'use client';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { childrenApi, pdrsApi } from '@/lib/api';
import { DDTRadarChart } from '@/components/ddt/RadarChart';
import { PDRSGauge } from '@/components/ddt/PDRSGauge';
import { DomainBar } from '@/components/ddt/DomainBar';
import { SchoolReadinessBadge } from '@/components/ddt/SchoolReadinessBadge';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { PageHeader } from '@/components/shared/PageHeader';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { formatAge, formatDate, formatDateTime } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Mic, Target, Image, FileText, Calendar, User, Phone,
  RefreshCw, AlertTriangle, CheckCircle2, Sparkles, Brain,
} from 'lucide-react';

export default function ChildProfilePage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['child-ddt', id],
    queryFn: () => childrenApi.getDDT(id).then(r => r.data),
  });

  const computeMutation = useMutation({
    mutationFn: () => pdrsApi.compute(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['child-ddt', id] });
      toast.success('PDRS score updated!');
    },
    onError: () => toast.error('Failed to compute PDRS score.'),
  });

  const generateDDTMutation = useMutation({
    mutationFn: () => childrenApi.generateDDT(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['child-ddt', id] });
      toast.success('Developmental portrait generated!');
    },
    onError: () => toast.error('Failed to generate portrait. Check OpenAI key.'),
  });

  if (isLoading) return <PageLoader text="Loading child profile…" />;
  if (!data) return null;

  const { child, ddt, pdrs, recent_observations } = data;
  const initials = child.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader title={child.full_name} backHref="/children" />

      {/* Child Info Card */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className={`text-lg font-bold ${child.gender === 'FEMALE' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'}`}>
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl font-bold font-display">{child.full_name}</h2>
                <RiskBadge level={child.latest_risk_level} score={child.latest_pdrs_score} showScore />
              </div>
              <div className="flex items-center gap-3 mt-1.5 text-sm text-muted-foreground">
                <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" />{formatAge(child.age_months)} old</span>
                <span>·</span>
                <span>{child.gender === 'FEMALE' ? 'Girl' : 'Boy'}</span>
              </div>
              {child.parent_name && (
                <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                  <User className="h-3 w-3" />{child.parent_name}
                  {child.parent_phone && <><Phone className="h-3 w-3 ml-1" />{child.parent_phone}</>}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <Link href={`/children/${id}/observe`}>
          <Button variant="outline" className="w-full gap-2 h-12">
            <Mic className="h-4 w-4 text-purple-600" /> Observe
          </Button>
        </Link>
        <Link href={`/children/${id}/milestones`}>
          <Button variant="outline" className="w-full gap-2 h-12">
            <Target className="h-4 w-4 text-brand-600" /> Milestones
          </Button>
        </Link>
        <Link href={`/children/${id}/drawing`}>
          <Button variant="outline" className="w-full gap-2 h-12">
            <Image className="h-4 w-4 text-green-600" /> Drawing
          </Button>
        </Link>
        <Link href={`/children/${id}/referral`}>
          <Button variant="outline" className="w-full gap-2 h-12">
            <FileText className="h-4 w-4 text-amber-600" /> Referral
          </Button>
        </Link>
      </div>

      <Tabs defaultValue="ddt">
        <TabsList className="w-full grid grid-cols-3">
          <TabsTrigger value="ddt">
            <Brain className="h-4 w-4 mr-1.5" /> DDT
          </TabsTrigger>
          <TabsTrigger value="pdrs">PDRS</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* DDT Tab */}
        <TabsContent value="ddt">
          <div className="space-y-4">
            {ddt ? (
              <>
                <Card>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-brand-600" /> Developmental Portrait
                      </CardTitle>
                      <Button size="sm" variant="ghost" onClick={() => generateDDTMutation.mutate()} loading={generateDDTMutation.isPending}>
                        <RefreshCw className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm leading-relaxed text-foreground">{ddt.portrait_text}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {ddt.asd_flag && <Badge variant="red">ASD Flag</Badge>}
                      {ddt.speech_delay_flag && <Badge variant="amber">Speech Delay</Badge>}
                      {ddt.motor_delay_flag && <Badge variant="amber">Motor Delay</Badge>}
                    </div>
                    {ddt.school_readiness_flag && (
                      <div className="mt-3">
                        <SchoolReadinessBadge flag={ddt.school_readiness_flag} note={ddt.school_readiness_note} large />
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-3">Generated {formatDateTime(ddt.created_at)}</p>
                  </CardContent>
                </Card>

                {pdrs && Object.keys(pdrs.domain_scores).length > 0 && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">Domain Radar</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <DDTRadarChart domainScores={pdrs.domain_scores} />
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="py-12 text-center space-y-4">
                  <Brain className="h-12 w-12 text-muted-foreground mx-auto" />
                  <div>
                    <p className="font-semibold">No DDT Profile Yet</p>
                    <p className="text-sm text-muted-foreground mt-1">Record observations and milestones first, then generate the AI portrait</p>
                  </div>
                  <Button onClick={() => generateDDTMutation.mutate()} loading={generateDDTMutation.isPending} className="gap-2">
                    <Sparkles className="h-4 w-4" /> Generate Portrait
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* PDRS Tab */}
        <TabsContent value="pdrs">
          <div className="space-y-4">
            {pdrs ? (
              <>
                <Card>
                  <CardContent className="p-6 flex flex-col items-center gap-4">
                    <PDRSGauge score={pdrs.overall_score} riskLevel={pdrs.risk_level} size="lg" />
                    <p className="text-xs text-muted-foreground">Last computed {formatDateTime(pdrs.computed_at)}</p>
                  </CardContent>
                </Card>

                {Object.keys(pdrs.domain_scores).length > 0 && (
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base">Domain Breakdown</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {Object.entries(pdrs.domain_scores).map(([code, score]) => (
                        <DomainBar key={code} domainCode={code} score={Math.round(score as number)} />
                      ))}
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="py-12 text-center space-y-4">
                  <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto" />
                  <p className="font-semibold">No PDRS Score</p>
                  <p className="text-sm text-muted-foreground">Complete milestone assessments to compute risk score</p>
                  <Button onClick={() => computeMutation.mutate()} loading={computeMutation.isPending} className="gap-2">
                    <RefreshCw className="h-4 w-4" /> Compute Score
                  </Button>
                </CardContent>
              </Card>
            )}

            <Button variant="outline" className="w-full gap-2" onClick={() => computeMutation.mutate()} loading={computeMutation.isPending}>
              <RefreshCw className="h-4 w-4" /> Recompute PDRS
            </Button>
          </div>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <div className="space-y-3">
            {recent_observations?.length ? (
              recent_observations.map((obs) => (
                <Card key={obs.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Mic className="h-4 w-4 text-purple-600 shrink-0" />
                        <Badge variant="secondary" className="text-xs">{obs.observation_type}</Badge>
                        <Badge
                          variant={obs.processing_status === 'DONE' ? 'green' : obs.processing_status === 'FAILED' ? 'red' : 'secondary'}
                          className="text-xs"
                        >
                          {obs.processing_status}
                        </Badge>
                      </div>
                      <span className="text-xs text-muted-foreground shrink-0">{formatDate(obs.created_at)}</span>
                    </div>
                    {obs.english_text && <p className="text-sm mt-2 text-foreground leading-relaxed">{obs.english_text}</p>}
                    {obs.markers?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {obs.markers.map(m => (
                          <Badge key={m.id} variant={m.marker_type === 'CONCERN' ? 'amber' : m.marker_type === 'FLAG' ? 'red' : 'green'} className="text-xs">
                            {m.description}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="py-10 text-center">
                  <p className="text-muted-foreground text-sm">No observations recorded yet</p>
                  <Link href={`/children/${id}/observe`}>
                    <Button className="mt-4 gap-2 "><Mic className="h-4 w-4" /> Record First Observation</Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
