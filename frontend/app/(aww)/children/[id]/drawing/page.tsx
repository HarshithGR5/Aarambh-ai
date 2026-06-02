'use client';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { childrenApi, drawingsApi } from '@/lib/api';
import { DrawingUpload } from '@/components/aww/DrawingUpload';
import { PageHeader } from '@/components/shared/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import Image from 'next/image';
import { formatDate } from '@/lib/utils';
import { Brain, Star, Pencil, Eye } from 'lucide-react';
import type { Drawing } from '@/lib/types';

export default function DrawingPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();

  const { data: child } = useQuery({
    queryKey: ['child', id],
    queryFn: () => childrenApi.getDDT(id).then(r => r.data.child),
  });

  const { data: drawings = [] } = useQuery({
    queryKey: ['drawings', id],
    queryFn: () => drawingsApi.list(id).then(r => r.data),
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, context }: { file: File; context: string }) =>
      drawingsApi.upload(id, file, context),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['drawings', id] });
      toast.success('Drawing uploaded! Analysing with AI…');
      analyzeMutation.mutate(res.data.id);
    },
    onError: () => toast.error('Failed to upload drawing.'),
  });

  const analyzeMutation = useMutation({
    mutationFn: (drawingId: string) => drawingsApi.analyze(drawingId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['drawings', id] });
      toast.success('Analysis complete!');
    },
    onError: () => toast.warning('Drawing saved but AI analysis failed. Check OpenAI key.'),
  });

  const isLoading = uploadMutation.isPending || analyzeMutation.isPending;

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader
        title="Drawing Analysis"
        description={child?.full_name}
        backHref={`/children/${id}`}
      />

      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Pencil className="h-4 w-4 text-green-600" /> Upload Drawing</CardTitle></CardHeader>
        <CardContent>
          <DrawingUpload
            onUpload={async (file, context) => { await uploadMutation.mutateAsync({ file, context }); }}
            loading={isLoading}
          />
        </CardContent>
      </Card>

      {drawings.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Past Drawings</h3>
          {drawings.map((drawing: Drawing) => (
            <Card key={drawing.id}>
              <CardContent className="p-4 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="relative h-20 w-20 shrink-0 rounded-xl overflow-hidden border">
                    <Image src={drawing.image_url} alt="Child drawing" fill className="object-cover" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="secondary" className="text-xs capitalize">{drawing.context?.replace(/_/g, ' ')}</Badge>
                      <span className="text-xs text-muted-foreground">{formatDate(drawing.upload_date)}</span>
                    </div>
                    {drawing.analysis ? (
                      <div className="mt-2 space-y-2">
                        <p className="text-sm leading-relaxed">{drawing.analysis.ai_summary}</p>
                        <div className="grid grid-cols-3 gap-2">
                          {drawing.analysis.fine_motor_score != null && (
                            <div className="text-center p-2 rounded-lg bg-muted">
                              <p className="text-lg font-bold text-brand-600">{drawing.analysis.fine_motor_score}</p>
                              <p className="text-xs text-muted-foreground">Motor</p>
                            </div>
                          )}
                          {drawing.analysis.cognitive_score != null && (
                            <div className="text-center p-2 rounded-lg bg-muted">
                              <p className="text-lg font-bold text-blue-600">{drawing.analysis.cognitive_score}</p>
                              <p className="text-xs text-muted-foreground">Cognitive</p>
                            </div>
                          )}
                          {drawing.analysis.emotional_tone && (
                            <div className="text-center p-2 rounded-lg bg-muted">
                              <p className="text-xs font-bold capitalize">{drawing.analysis.emotional_tone.toLowerCase()}</p>
                              <p className="text-xs text-muted-foreground">Tone</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="mt-2 flex items-center gap-2">
                        <Brain className="h-4 w-4 text-muted-foreground animate-pulse" />
                        <span className="text-xs text-muted-foreground">Analysis pending…</span>
                        <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => analyzeMutation.mutate(drawing.id)}>
                          Retry
                        </Button>
                      </div>
                    )}
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
