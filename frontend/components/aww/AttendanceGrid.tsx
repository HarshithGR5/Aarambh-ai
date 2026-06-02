'use client';
import { useState } from 'react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { Child } from '@/lib/types';

interface AttendanceGridProps {
  children: Child[];
  initialPresent?: Record<string, boolean>;
  onSave: (attendance: Record<string, boolean>) => Promise<void>;
  loading?: boolean;
}

export function AttendanceGrid({ children, initialPresent = {}, onSave, loading }: AttendanceGridProps) {
  const [present, setPresent] = useState<Record<string, boolean>>(initialPresent);

  const toggle = (id: string) => setPresent(p => ({ ...p, [id]: !p[id] }));
  const markAll = (val: boolean) => {
    const all: Record<string, boolean> = {};
    children.forEach(c => { all[c.id] = val; });
    setPresent(all);
  };

  const presentCount = Object.values(present).filter(Boolean).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="green">{presentCount} Present</Badge>
          <Badge variant="red">{children.length - presentCount} Absent</Badge>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => markAll(true)}>All Present</Button>
          <Button size="sm" variant="outline" onClick={() => markAll(false)}>All Absent</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {children.map(child => {
          const isPresent = !!present[child.id];
          const initials = child.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
          return (
            <button
              key={child.id}
              onClick={() => toggle(child.id)}
              className={cn(
                'flex items-center gap-2.5 p-3 rounded-xl border-2 transition-all text-left',
                isPresent
                  ? 'border-green-400 bg-green-50 text-green-800'
                  : 'border-border bg-background text-muted-foreground hover:bg-muted/50'
              )}
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback className={cn('text-xs', isPresent ? 'bg-green-200 text-green-800' : 'bg-muted')}>
                  {initials}
                </AvatarFallback>
              </Avatar>
              <div className="min-w-0">
                <p className="text-xs font-semibold truncate">{child.full_name}</p>
                <p className={cn('text-xs', isPresent ? 'text-green-600' : 'text-muted-foreground')}>
                  {isPresent ? '✓ Present' : 'Absent'}
                </p>
              </div>
            </button>
          );
        })}
      </div>

      <Button
        className="w-full"
        size="lg"
        loading={loading}
        onClick={() => onSave(present)}
      >
        Save Attendance
      </Button>
    </div>
  );
}
