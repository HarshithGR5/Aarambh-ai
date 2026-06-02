'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { BottomNav } from '@/components/aww/BottomNav';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import {
  Brain, Home, Users, CalendarCheck2, LogOut, Menu, X, Bell, ChevronRight,
} from 'lucide-react';

const navLinks = [
  { href: '/home',       label: 'Home',       icon: Home },
  { href: '/children',   label: 'Children',   icon: Users },
  { href: '/attendance', label: 'Attendance', icon: CalendarCheck2 },
];

function AWWSidebarContent({ onClose, onSignOut }: { onClose?: () => void; onSignOut: () => void }) {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const initials = user?.name?.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2) ?? 'A';

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 px-5 h-16 border-b border-slate-100">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center shadow-sm">
          <Brain className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="font-display font-bold text-gray-900 leading-tight">Aarambh AI</p>
          <p className="text-[10px] text-gray-400 uppercase tracking-wide mt-0.5">Anganwadi</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="ml-auto text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navLinks.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link key={href} href={href} onClick={onClose}>
              <span
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
              </span>
            </Link>
          );
        })}

      </nav>

      <Separator />

      <div className="p-4 space-y-3">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl bg-slate-50">
          <Avatar className="h-9 w-9 shrink-0">
            <AvatarFallback className="text-xs bg-brand-100 text-brand-700 font-bold">{initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">{user?.name}</p>
            <p className="text-xs text-gray-400">Anganwadi Worker</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl"
          onClick={onSignOut}
        >
          <LogOut className="h-4 w-4" /> Sign Out
        </Button>
      </div>
    </div>
  );
}

export default function AWWLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, clearAuth, isAuthenticated } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const DEFAULT_REDIRECT: Record<string, string> = {
    CDPO: '/overview', HEALTH_WORKER: '/referrals',
    STATE_OFFICER: '/district', ADMIN: '/overview',
  };

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return; }
    const role = (user as any)?.role ?? '';
    if (role && role !== 'AWW') {
      router.replace(DEFAULT_REDIRECT[role] ?? '/overview');
    }
  }, [isAuthenticated, user, router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const handleSignOut = () => {
    clearAuth();
    setSidebarOpen(false);
    router.replace('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Desktop sidebar — lg+ only */}
      <aside className="hidden lg:flex w-60 flex-col fixed inset-y-0 left-0 z-50 bg-white border-r border-slate-200">
        <AWWSidebarContent onSignOut={handleSignOut} />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" onClick={() => setSidebarOpen(false)}>
          <div className="absolute top-0 left-0 w-72 h-full bg-white shadow-2xl" onClick={e => e.stopPropagation()}>
            <AWWSidebarContent onClose={() => setSidebarOpen(false)} onSignOut={handleSignOut} />
          </div>
        </div>
      )}

      {/* Mobile-only top bar */}
      <header className="lg:hidden sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
        <div className="px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(true)}
              className="h-9 w-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition-colors"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-brand-600 to-brand-700 flex items-center justify-center ml-1">
              <Brain className="h-4 w-4 text-white" />
            </div>
            <span className="font-display font-bold text-gray-900 text-sm">Aarambh AI</span>
          </div>
          <button className="h-8 w-8 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200">
            <Bell className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="lg:pl-60">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 pb-24 lg:pb-8">
          {children}
        </div>
      </div>

      {/* Bottom nav — mobile only */}
      <div className="lg:hidden">
        <BottomNav />
      </div>
    </div>
  );
}
