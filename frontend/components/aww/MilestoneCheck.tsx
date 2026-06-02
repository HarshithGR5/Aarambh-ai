'use client';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { MilestoneAssessment } from '@/lib/types';
import { CheckCircle2, XCircle, HelpCircle, MinusCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';

type Result = 'YES' | 'SOMETIMES' | 'NOT_YET' | 'NA';

const resultConfig: Record<Result, { label: string; icon: React.FC<{ className?: string }>; color: string; bg: string }> = {
  YES:       { label: 'Yes',       icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-50 border-green-300' },
  SOMETIMES: { label: 'Sometimes', icon: HelpCircle,   color: 'text-amber-600', bg: 'bg-amber-50 border-amber-300' },
  NOT_YET:   { label: 'Not Yet',   icon: XCircle,      color: 'text-red-600',   bg: 'bg-red-50 border-red-300' },
  NA:        { label: 'N/A',       icon: MinusCircle,  color: 'text-gray-500',  bg: 'bg-gray-50 border-gray-200' },
};

interface MilestoneCheckProps {
  milestones: MilestoneAssessment[];
  onSave: (results: Array<{ milestone_id: number; result: string }>) => Promise<void>;
  loading?: boolean;
}

export function MilestoneCheck({ milestones, onSave, loading }: MilestoneCheckProps) {
  const [results, setResults] = useState<Record<number, Result>>(() => {
    const init: Record<number, Result> = {};
    milestones.forEach(m => { if (m.result) init[m.milestone_id] = m.result as Result; });
    return init;
  });
  const [expandedDomain, setExpandedDomain] = useState<string | null>(null);

  const byDomain = milestones.reduce((acc, m) => {
    if (!acc[m.domain_code]) acc[m.domain_code] = { name: m.domain_name, items: [] };
    acc[m.domain_code].items.push(m);
    return acc;
  }, {} as Record<string, { name: string; items: MilestoneAssessment[] }>);

  const setResult = (id: number, result: Result) =>
    setResults(r => ({ ...r, [id]: result }));

  const saveAll = () => {
    const arr = Object.entries(results).map(([id, result]) => ({ milestone_id: Number(id), result }));
    onSave(arr);
  };

  const answered = Object.keys(results).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{answered} / {milestones.length} answered</span>
        <div className="h-2 w-32 rounded-full bg-muted overflow-hidden">
          <div className="h-full bg-brand-600 rounded-full transition-all" style={{ width: `${(answered / milestones.length) * 100}%` }} />
        </div>
      </div>

      <div className="space-y-3">
        {Object.entries(byDomain).map(([code, { name, items }]) => {
          const open = expandedDomain === code;
          const domainAnswered = items.filter(i => results[i.milestone_id]).length;
          const hasConcern = items.some(i => results[i.milestone_id] === 'NOT_YET' && i.is_critical);

          return (
            <div key={code} className="rounded-xl border overflow-hidden">
              <button
                className="flex w-full items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                onClick={() => setExpandedDomain(open ? null : code)}
              >
                <div className="flex items-center gap-2">
                  {hasConcern && <AlertCircle className="h-4 w-4 text-red-500" />}
                  <span className="font-semibold text-sm">{name}</span>
                  <Badge variant="secondary" className="text-xs">{domainAnswered}/{items.length}</Badge>
                </div>
                {open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
              </button>

              {open && (
                <div className="divide-y border-t">
                  {items.map(m => {
                    const current = results[m.milestone_id];
                    return (
                      <div key={m.milestone_id} className="p-4 space-y-3 bg-background">
                        <div className="flex items-start gap-2">
                          {m.is_critical && <AlertCircle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />}
                          <p className="text-sm leading-relaxed text-foreground">{m.milestone_text}</p>
                        </div>
                        <div className="grid grid-cols-4 gap-1.5">
                          {(['YES', 'SOMETIMES', 'NOT_YET', 'NA'] as Result[]).map(r => {
                            const cfg = resultConfig[r];
                            const Icon = cfg.icon;
                            const selected = current === r;
                            return (
                              <button
                                key={r}
                                onClick={() => setResult(m.milestone_id, r)}
                                className={cn(
                                  'flex flex-col items-center gap-1 py-2 rounded-xl border-2 transition-all text-xs font-medium',
                                  selected ? cfg.bg : 'border-border bg-background text-muted-foreground hover:bg-muted/50'
                                )}
                              >
                                <Icon className={cn('h-4 w-4', selected ? cfg.color : 'text-muted-foreground')} />
                                {cfg.label}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <Button className="w-full" size="lg" loading={loading} onClick={saveAll} disabled={answered === 0}>
        Save Assessments ({answered})
      </Button>
    </div>
  );
}
