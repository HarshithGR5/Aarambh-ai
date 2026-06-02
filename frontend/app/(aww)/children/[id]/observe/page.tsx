'use client';
import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { childrenApi, observationsApi } from '@/lib/api';
import { VoiceRecorder } from '@/components/aww/VoiceRecorder';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PageHeader } from '@/components/shared/PageHeader';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Mic, Type, Send, CheckCircle2 } from 'lucide-react';
import type { Observation } from '@/lib/types';
import { DOMAIN_META } from '@/lib/utils';

export default function ObservePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('en');
  const [result, setResult] = useState<Observation | null>(null);

  const { data: child } = useQuery({
    queryKey: ['child', id],
    queryFn: () => childrenApi.getDDT(id).then(r => r.data.child),
  });

  const voiceMutation = useMutation({
    mutationFn: (blob: Blob) => observationsApi.submitVoice(id, blob),
    onSuccess: (res) => {
      setResult(res.data);
      qc.invalidateQueries({ queryKey: ['child-ddt', id] });
      toast.success('Observation submitted & analysed!');
    },
    onError: () => toast.error('Failed to process voice. Check microphone & try again.'),
  });

  const textMutation = useMutation({
    mutationFn: () => observationsApi.submitText({ child_id: id, raw_text: text, language }),
    onSuccess: (res) => {
      setResult(res.data);
      setText('');
      qc.invalidateQueries({ queryKey: ['child-ddt', id] });
      toast.success('Observation submitted & analysed!');
    },
    onError: () => toast.error('Failed to submit observation.'),
  });

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader
        title="Record Observation"
        description={child?.full_name}
        backHref={`/children/${id}`}
      />

      {result ? (
        <div className="space-y-4">
          <Card className="border-green-200 bg-green-50/50">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2 text-green-700">
                <CheckCircle2 className="h-5 w-5" /> Observation Analysed
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.english_text && (
                <p className="text-sm text-foreground leading-relaxed border-l-2 border-brand-300 pl-3">
                  {result.english_text}
                </p>
              )}
              {result.markers?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Extracted Markers</p>
                  <div className="flex flex-wrap gap-1.5">
                    {result.markers.map(m => (
                      <Badge
                        key={m.id}
                        variant={m.marker_type === 'CONCERN' ? 'amber' : m.marker_type === 'FLAG' ? 'red' : 'green'}
                        className="text-xs"
                      >
                        <span className="font-normal opacity-70 mr-1">{DOMAIN_META[m.domain_code ?? '']?.label ?? m.domain_code}</span>
                        {m.description}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              <Badge variant={result.processing_status === 'DONE' ? 'green' : result.processing_status === 'FAILED' ? 'red' : 'secondary'}>
                Status: {result.processing_status}
              </Badge>
            </CardContent>
          </Card>
          <Button variant="outline" className="w-full" onClick={() => setResult(null)}>
            Record Another Observation
          </Button>
          <Button className="w-full" onClick={() => router.push(`/children/${id}`)}>
            View Child Profile
          </Button>
        </div>
      ) : (
        <Tabs defaultValue="voice">
          <TabsList className="w-full grid grid-cols-2">
            <TabsTrigger value="voice"><Mic className="h-4 w-4 mr-2" /> Voice</TabsTrigger>
            <TabsTrigger value="text"><Type className="h-4 w-4 mr-2" /> Text</TabsTrigger>
          </TabsList>

          <TabsContent value="voice">
            <Card>
              <CardContent>
                <VoiceRecorder
                  onSubmit={async (blob) => { await voiceMutation.mutateAsync(blob); }}
                  loading={voiceMutation.isPending}
                />
              </CardContent>
            </Card>
            <p className="text-xs text-muted-foreground text-center mt-2">
              Speak in Hindi, Kannada, English, or any Indian language
            </p>
          </TabsContent>

          <TabsContent value="text">
            <Card>
              <CardContent className="p-5 space-y-4">
                <div className="space-y-2">
                  <Label>Language</Label>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="hi">Hindi</SelectItem>
                      <SelectItem value="kn">Kannada</SelectItem>
                      <SelectItem value="mr">Marathi</SelectItem>
                      <SelectItem value="ta">Tamil</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Observation</Label>
                  <textarea
                    className="flex min-h-[120px] w-full rounded-xl border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 resize-none"
                    placeholder="Describe what you observed about the child's behaviour, speech, motor skills, or social interaction…"
                    value={text}
                    onChange={e => setText(e.target.value)}
                  />
                </div>
                <Button
                  className="w-full gap-2"
                  onClick={() => textMutation.mutate()}
                  loading={textMutation.isPending}
                  disabled={!text.trim()}
                  size="lg"
                >
                  <Send className="h-4 w-4" /> Submit Observation
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
