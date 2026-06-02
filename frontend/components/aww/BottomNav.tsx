'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Home, Users, CalendarCheck2 } from 'lucide-react';

const navItems = [
  { href: '/home',       label: 'Home',       icon: Home },
  { href: '/children',   label: 'Children',   icon: Users },
  { href: '/attendance', label: 'Attendance', icon: CalendarCheck2 },
];

export function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-200 bg-white/95 backdrop-blur-md pb-safe">
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto px-2">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex flex-col items-center gap-1 px-4 py-2 rounded-2xl transition-all duration-200 relative',
                active ? 'text-brand-600' : 'text-slate-400 hover:text-slate-600'
              )}
            >
              {active && (
                <span className="absolute -top-[1px] left-1/2 -translate-x-1/2 w-8 h-0.5 rounded-full bg-brand-600" />
              )}
              <Icon className={cn('h-5 w-5 transition-transform', active && 'scale-110')} />
              <span className={cn('text-xs font-medium', active && 'font-semibold')}>{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
