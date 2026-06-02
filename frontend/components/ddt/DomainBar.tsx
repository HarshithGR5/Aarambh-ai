import { DOMAIN_META } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface DomainBarProps {
  domainCode: string;
  score: number;
}

export function DomainBar({ domainCode, score }: DomainBarProps) {
  const meta = DOMAIN_META[domainCode] ?? { label: domainCode, color: '#94a3b8', bg: 'bg-slate-50' };
  const level = score >= 70 ? 'text-red-600' : score >= 40 ? 'text-amber-600' : 'text-green-600';

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: meta.color }} />
          <span className="font-medium text-foreground truncate">{meta.label}</span>
        </div>
        <span className={cn('font-bold tabular-nums', level)}>{score}%</span>
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${score}%`, backgroundColor: meta.color }}
        />
      </div>
    </div>
  );
}
