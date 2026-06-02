'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { DashboardSidebar } from '@/components/dashboard/Sidebar';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Bell, Brain, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isAuthenticated, clearAuth } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated()) router.replace('/login');
  }, [isAuthenticated, router]);

  if (!user) return <div className="min-h-screen flex items-center justify-center"><LoadingSpinner size="lg" /></div>;

  const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <div className="min-h-screen bg-background">
      <DashboardSidebar />

      {/* Mobile header */}
      <header className="lg:hidden sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur-md">
        <div className="flex items-center justify-between px-4 h-14">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-brand-600" />
            <span className="font-display font-bold">Aarambh AI</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-9 w-9"><Bell className="h-4 w-4" /></Button>
            <Avatar className="h-8 w-8 cursor-pointer" onClick={clearAuth}>
              <AvatarFallback className="text-xs bg-brand-100 text-brand-700">{initials}</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>

      <main className="lg:pl-64">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
