import { Badge } from '@/components/ui/badge';
import { getRiskLabel } from '@/lib/utils';
import type { RiskLevel } from '@/lib/types';
import { ShieldCheck, AlertTriangle, AlertCircle } from 'lucide-react';

interface RiskBadgeProps {
  level?: RiskLevel | null;
  score?: number | null;
  showScore?: boolean;
}

export function RiskBadge({ level, score, showScore = false }: RiskBadgeProps) {
  const iconMap = {
    GREEN: <ShieldCheck className="h-3 w-3" />,
    AMBER: <AlertTriangle className="h-3 w-3" />,
    RED:   <AlertCircle className="h-3 w-3" />,
  };
  const variantMap: Record<string, 'green' | 'amber' | 'red'> = {
    GREEN: 'green', AMBER: 'amber', RED: 'red',
  };

  if (!level) {
    return <Badge variant="secondary">Not Assessed</Badge>;
  }

  return (
    <Badge variant={variantMap[level] ?? 'secondary'}>
      {iconMap[level]}
      {getRiskLabel(level)}
      {showScore && score != null && ` · ${score}`}
    </Badge>
  );
}
