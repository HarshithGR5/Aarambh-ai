'use client';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { formatAge, cn } from '@/lib/utils';
import type { Child } from '@/lib/types';
import { Calendar, User } from 'lucide-react';

interface ChildCardProps {
  child: Child;
  compact?: boolean;
}

export function ChildCard({ child, compact = false }: ChildCardProps) {
  const initials = child.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  const genderColor = child.gender === 'FEMALE' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700';

  return (
    <Link href={`/children/${child.id}`}>
      <Card className={cn(
        'hover:border-brand-300 hover:shadow-md transition-all duration-200 cursor-pointer active:scale-[0.99]',
        !child.is_active && 'opacity-50'
      )}>
        <CardContent className={cn('p-4', compact ? 'py-3' : '')}>
          <div className="flex items-center gap-3">
            <Avatar className={cn(compact ? 'h-10 w-10' : 'h-12 w-12')}>
              <AvatarFallback className={genderColor}>{initials}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <p className={cn('font-semibold text-foreground truncate', compact ? 'text-sm' : 'text-base')}>
                  {child.full_name}
                </p>
                <RiskBadge level={child.latest_risk_level} score={child.latest_pdrs_score} />
              </div>
              <div className="flex items-center gap-3 mt-1">
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Calendar className="h-3 w-3" />
                  {formatAge(child.age_months)}
                </span>
                <span className={cn('text-xs font-medium px-1.5 py-0.5 rounded-full', genderColor)}>
                  {child.gender === 'FEMALE' ? '♀' : '♂'}
                </span>
                {child.parent_name && (
                  <span className="flex items-center gap-1 text-xs text-muted-foreground truncate">
                    <User className="h-3 w-3 shrink-0" />
                    {child.parent_name}
                  </span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
