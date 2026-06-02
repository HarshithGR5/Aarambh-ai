'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { childrenApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { ChildCard } from '@/components/aww/ChildCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/EmptyState';
import { PageHeader } from '@/components/shared/PageHeader';
import { Plus, Search, Users, Filter } from 'lucide-react';
import type { Child, RiskLevel } from '@/lib/types';

type Filter = 'ALL' | 'GREEN' | 'AMBER' | 'RED';

export default function ChildrenPage() {
  const { user } = useAuthStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<Filter>('ALL');

  const { data: children = [], isLoading } = useQuery({
    queryKey: ['children', user?.awc_id],
    queryFn: () => childrenApi.list(user?.awc_id).then(r => r.data),
  });

  const filtered = children.filter(c => {
    const matchSearch = search === '' || c.full_name.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'ALL' || c.latest_risk_level === (filter as RiskLevel);
    return matchSearch && matchFilter;
  });

  const counts = {
    ALL: children.length,
    GREEN: children.filter(c => c.latest_risk_level === 'GREEN').length,
    AMBER: children.filter(c => c.latest_risk_level === 'AMBER').length,
    RED: children.filter(c => c.latest_risk_level === 'RED').length,
  };

  return (
    <div className="space-y-4 animate-fade-in">
      <PageHeader
        title="Children"
        description={`${children.length} children registered`}
        actions={
          <Link href="/children/new">
            <Button size="sm" className="gap-1.5">
              <Plus className="h-4 w-4" /> Register
            </Button>
          </Link>
        }
      />

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search children…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Risk filters */}
      <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
        {(['ALL', 'GREEN', 'AMBER', 'RED'] as Filter[]).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
              filter === f
                ? f === 'RED'    ? 'bg-red-100 text-red-700 border-red-300'
                : f === 'AMBER'  ? 'bg-amber-100 text-amber-700 border-amber-300'
                : f === 'GREEN'  ? 'bg-green-100 text-green-700 border-green-300'
                : 'bg-brand-100 text-brand-700 border-brand-300'
                : 'bg-background text-muted-foreground border-border hover:bg-muted/50'
            }`}
          >
            {f === 'ALL' ? 'All' : f}
            <span className="bg-white/60 px-1.5 py-0.5 rounded-full">{counts[f]}</span>
          </button>
        ))}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-20 rounded-2xl" />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<Users className="h-8 w-8" />}
          title={search ? 'No children found' : 'No children registered'}
          description={search ? 'Try a different search term' : 'Register the first child to get started'}
          action={!search && (
            <Link href="/children/new">
              <Button className="gap-2"><Plus className="h-4 w-4" /> Register Child</Button>
            </Link>
          )}
        />
      ) : (
        <div className="space-y-3">
          {filtered.map(child => <ChildCard key={child.id} child={child} />)}
        </div>
      )}
    </div>
  );
}
