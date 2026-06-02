'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  Brain, LayoutDashboard, Users, Map, FileText,
  BarChart3, Settings, LogOut, Building2, Bell,
} from 'lucide-react';

const navItems = [
  { href: '/overview',   label: 'Overview',   icon: LayoutDashboard },
  { href: '/district',   label: 'Heatmap',    icon: Map },
  { href: '/awcs',       label: 'AWC Centers', icon: Building2 },
  { href: '/referrals',  label: 'Referrals',  icon: FileText },
  { href: '/reports',    label: 'Reports',    icon: BarChart3 },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const initials = user?.name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) ?? 'U';

  return (
    <aside className="hidden lg:flex w-64 flex-col fixed inset-y-0 left-0 z-50 bg-background border-r border-border">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 h-16 border-b border-border">
        <div className="h-8 w-8 rounded-lg bg-brand-600 flex items-center justify-center">
          <Brain className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="font-display font-bold text-foreground leading-none">Aarambh AI</p>
          <p className="text-[10px] text-muted-foreground uppercase tracking-wide mt-0.5">Dashboard</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link key={href} href={href}>
              <div className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                active
                  ? 'bg-brand-50 text-brand-700 border border-brand-200'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
              )}>
                <Icon className={cn('h-4.5 w-4.5', active ? 'text-brand-600' : 'text-current')} />
                {label}
              </div>
            </Link>
          );
        })}
      </nav>

      <Separator />

      {/* User */}
      <div className="p-4 space-y-2">
        <div className="flex items-center gap-3 px-2 py-2">
          <Avatar className="h-9 w-9">
            <AvatarFallback className="text-xs bg-brand-100 text-brand-700 font-semibold">{initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">{user?.name}</p>
            <p className="text-xs text-muted-foreground">{user?.role}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" className="w-full justify-start gap-2 text-muted-foreground hover:text-destructive" onClick={clearAuth}>
          <LogOut className="h-4 w-4" /> Sign Out
        </Button>
      </div>
    </aside>
  );
}
