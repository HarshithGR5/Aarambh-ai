import { cn } from '@/lib/utils';
import { GraduationCap, BookOpen, AlertTriangle } from 'lucide-react';

interface SchoolReadinessBadgeProps {
  flag?: string | null;
  note?: string | null;
  large?: boolean;
}

const readinessConfig = {
  ON_TRACK:      { icon: GraduationCap, label: 'School Ready', color: 'bg-green-50 text-green-700 border-green-200' },
  DEVELOPING:    { icon: BookOpen,      label: 'Developing',   color: 'bg-blue-50 text-blue-700 border-blue-200' },
  NEEDS_SUPPORT: { icon: AlertTriangle, label: 'Needs Support', color: 'bg-amber-50 text-amber-700 border-amber-200' },
};

export function SchoolReadinessBadge({ flag, note, large = false }: SchoolReadinessBadgeProps) {
  if (!flag) return null;
  const config = readinessConfig[flag as keyof typeof readinessConfig];
  if (!config) return null;
  const Icon = config.icon;

  return (
    <div className={cn('inline-flex flex-col gap-1', large ? 'w-full' : '')}>
      <div className={cn(
        'inline-flex items-center gap-2 rounded-xl border px-3 py-2 font-semibold',
        large ? 'text-sm w-full' : 'text-xs',
        config.color
      )}>
        <Icon className={large ? 'h-4 w-4' : 'h-3 w-3'} />
        {config.label}
      </div>
      {note && large && (
        <p className="text-xs text-muted-foreground px-1">{note}</p>
      )}
    </div>
  );
}
