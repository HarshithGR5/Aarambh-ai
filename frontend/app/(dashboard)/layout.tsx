'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import {
  Brain, LayoutDashboard, Map, FileText, BarChart3,
  LogOut, Building2, Menu, X, Bell, ChevronRight, Users,
} from 'lucide-react';

const ROLE_LABELS: Record<string, { label: string; color: string }> = {
  CDPO:          { label: 'CDPO Officer',      color: 'bg-blue-100 text-blue-700' },
  HEALTH_WORKER: { label: 'RBSK Health Worker', color: 'bg-green-100 text-green-700' },
  STATE_OFFICER: { label: 'State Officer',      color: 'bg-amber-100 text-amber-700' },
  ADMIN:         { label: 'Administrator',      color: 'bg-rose-100 text-rose-700' },
};

const navItems = [
  { href: '/overview',  label: 'Overview',    icon: LayoutDashboard, roles: ['CDPO', 'ADMIN'] },
  { href: '/children',  label: 'Children',    icon: Users,           roles: ['CDPO', 'ADMIN'] },
  { href: '/district',  label: 'Heatmap',     icon: Map,             roles: ['CDPO', 'STATE_OFFICER', 'ADMIN'] },
  { href: '/awcs',      label: 'AWC Centers', icon: Building2,       roles: ['CDPO', 'ADMIN'] },
  { href: '/referrals', label: 'Referrals',   icon: FileText,        roles: ['CDPO', 'HEALTH_WORKER', 'ADMIN'] },
  { href: '/reports',   label: 'Reports',     icon: BarChart3,       roles: ['CDPO', 'STATE_OFFICER', 'ADMIN'] },
];

function SidebarContent({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, clearAuth } = useAuthStore();
  const role = (user as any)?.role ?? '';
  const initials = user?.name?.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2) ?? 'U';
  const roleInfo = ROLE_LABELS[role] ?? { label: role, color: 'bg-gray-100 text-gray-700' };
  const visibleItems = navItems.filter(item => item.roles.includes(role) || role === 'ADMIN');

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 h-16 border-b border-slate-100">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center shadow-sm">
          <Brain className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="font-display font-bold text-gray-900 leading-tight">Aarambh AI</p>
          <p className="text-[10px] text-gray-400 uppercase tracking-wide mt-0.5">Dashboard</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="ml-auto text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {visibleItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link key={href} href={href}>
              <div
                onClick={onClose}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer',
                  active
                    ? 'bg-brand-600 text-white shadow-sm shadow-brand-200'
                    : 'text-gray-500 hover:bg-slate-100 hover:text-gray-900'
                )}
              >
                <Icon className={cn('h-4 w-4 shrink-0', active ? 'text-white' : '')} />
                {label}
                {active && <ChevronRight className="h-3.5 w-3.5 ml-auto opacity-60" />}
              </div>
            </Link>
          );
        })}
      </nav>

      <Separator />

      {/* User profile */}
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl bg-slate-50">
          <Avatar className="h-9 w-9 shrink-0">
            <AvatarFallback className="text-xs bg-brand-100 text-brand-700 font-bold">{initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">{user?.name}</p>
            <Badge className={cn('text-[10px] px-1.5 py-0 mt-0.5 font-medium border-0', roleInfo.color)}>
              {roleInfo.label}
            </Badge>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl"
          onClick={() => { clearAuth(); router.replace('/login'); }}
        >
          <LogOut className="h-4 w-4" /> Sign Out
        </Button>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isAuthenticated, clearAuth } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const role = (user as any)?.role ?? '';
  const roleInfo = ROLE_LABELS[role] ?? { label: role, color: 'bg-gray-100 text-gray-700' };

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return; }
    if (role === 'AWW') router.replace('/home');
  }, [isAuthenticated, role, router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-64 flex-col fixed inset-y-0 left-0 z-50 bg-white border-r border-slate-200">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" onClick={() => setSidebarOpen(false)}>
          <div className="absolute top-0 left-0 w-72 h-full bg-white shadow-2xl" onClick={e => e.stopPropagation()}>
            <SidebarContent onClose={() => setSidebarOpen(false)} />
          </div>
        </div>
      )}

      {/* Mobile top bar */}
      <header className="lg:hidden sticky top-0 z-40 bg-white border-b border-slate-200">
        <div className="flex items-center gap-3 px-4 h-14">
          <button
            onClick={() => setSidebarOpen(true)}
            className="h-9 w-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition-colors"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center">
              <Brain className="h-4 w-4 text-white" />
            </div>
            <span className="font-display font-bold text-gray-900 text-sm">Aarambh AI</span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Badge className={cn('text-[10px] font-semibold border-0', roleInfo.color)}>
              {roleInfo.label}
            </Badge>
            <button className="h-8 w-8 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500">
              <Bell className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="lg:pl-64">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
          {children}
        </div>
      </div>
    </div>
  );
}
