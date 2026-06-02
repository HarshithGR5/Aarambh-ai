'use client';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { childrenApi, milestonesApi } from '@/lib/api';
import { MilestoneCheck } from '@/components/aww/MilestoneCheck';
import { PageHeader } from '@/components/shared/PageHeader';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

export default function MilestonesPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();

  const { data: child } = useQuery({
    queryKey: ['child', id],
    queryFn: () => childrenApi.getDDT(id).then(r => r.data.child),
  });

  const { data: milestones = [], isLoading } = useQuery({
    queryKey: ['milestones', id],
    queryFn: () => milestonesApi.forChild(id).then(r => r.data),
    enabled: !!id,
  });

  const mutation = useMutation({
    mutationFn: (assessments: Array<{ milestone_id: number; result: string }>) =>
      milestonesApi.assess(id, assessments),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['milestones', id] });
      qc.invalidateQueries({ queryKey: ['child-ddt', id] });
      toast.success('Milestone assessments saved!');
      router.push(`/children/${id}`);
    },
    onError: () => toast.error('Failed to save assessments.'),
  });

  if (isLoading) return <PageLoader text="Loading milestones…" />;

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader
        title="Milestone Check"
        description={`${child?.full_name} · ${milestones.length} milestones`}
        backHref={`/children/${id}`}
      />

      {milestones.length > 0 ? (
        <MilestoneCheck
          milestones={milestones}
          onSave={async (results) => { await mutation.mutateAsync(results); }}
          loading={mutation.isPending}
        />
      ) : (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No age-appropriate milestones found. Child may need date of birth verified.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
