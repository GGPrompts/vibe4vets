'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BarChart3,
  ClipboardCheck,
  Database,
  Calendar,
  Menu,
  X,
  ChevronLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

const navItems = [
  {
    href: '/admin',
    label: 'Review Queue',
    icon: ClipboardCheck,
    description: 'Pending reviews',
  },
  {
    href: '/admin/analytics',
    label: 'Analytics',
    icon: BarChart3,
    description: 'Usage metrics',
  },
  {
    href: '/admin/sources',
    label: 'Data Sources',
    icon: Database,
    description: 'Source health',
  },
  {
    href: '/admin/jobs',
    label: 'Scheduled Jobs',
    icon: Calendar,
    description: 'Job management',
  },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/admin') {
      return pathname === '/admin';
    }
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-[hsl(var(--v4v-bg-base))]">
      {/* Mobile Header */}
      <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-border/50 bg-card/80 backdrop-blur-sm px-4 lg:hidden">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setMobileMenuOpen(true)}
          aria-label="Open menu"
          className="hover:bg-[hsl(var(--v4v-gold)/0.1)]"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-3">
          <span className="font-display font-semibold text-[hsl(var(--v4v-navy))]">Admin</span>
        </div>
      </header>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 transform bg-card shadow-xl transition-transform duration-200 ease-in-out lg:hidden ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-border/50 px-4 bg-gradient-to-r from-[hsl(var(--v4v-navy))] to-[hsl(var(--v4v-navy)/0.9)]">
          <div className="flex items-center gap-3">
            <span className="font-display font-semibold text-[hsl(var(--v4v-gold))]">
              Admin Panel
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close menu"
            className="text-white/70 hover:text-white hover:bg-white/10"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        <nav className="flex flex-col gap-1.5 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`group flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition-all duration-200 ${
                  active
                    ? 'bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-navy))] font-medium border border-[hsl(var(--v4v-gold)/0.3)]'
                    : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                }`}
              >
                <div className={`flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                  active
                    ? 'bg-[hsl(var(--v4v-gold)/0.2)]'
                    : 'bg-muted group-hover:bg-[hsl(var(--v4v-gold)/0.1)]'
                }`}>
                  <Icon className={`h-4 w-4 ${active ? 'text-[hsl(var(--v4v-gold-dark))]' : 'text-muted-foreground group-hover:text-[hsl(var(--v4v-gold-dark))]'}`} />
                </div>
                <div className="flex flex-col">
                  <span>{item.label}</span>
                  <span className="text-xs text-muted-foreground">
                    {item.description}
                  </span>
                </div>
              </Link>
            );
          })}
        </nav>
        <Separator className="mx-4" />
        <div className="p-4">
          <Link href="/">
            <Button variant="outline" size="sm" className="w-full gap-2 hover:bg-[hsl(var(--v4v-gold)/0.1)] hover:border-[hsl(var(--v4v-gold)/0.3)]">
              <ChevronLeft className="h-4 w-4" />
              Back to Site
            </Button>
          </Link>
        </div>
      </aside>

      {/* Desktop Layout */}
      <div className="flex">
        {/* Desktop Sidebar */}
        <aside className="sticky top-0 hidden h-screen w-64 shrink-0 border-r border-border/50 bg-card lg:block">
          {/* Sidebar Header with Navy Background */}
          <div className="flex h-16 items-center gap-3 px-5 bg-gradient-to-r from-[hsl(var(--v4v-navy))] to-[hsl(var(--v4v-navy)/0.95)]">
            <span className="font-display font-semibold text-[hsl(var(--v4v-gold))]">
              Admin Panel
            </span>
          </div>
          <nav className="flex flex-col gap-1.5 p-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`group flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition-all duration-200 ${
                    active
                      ? 'bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-navy))] font-medium border border-[hsl(var(--v4v-gold)/0.3)]'
                      : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground border border-transparent'
                  }`}
                >
                  <div className={`flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                    active
                      ? 'bg-[hsl(var(--v4v-gold)/0.2)]'
                      : 'bg-muted/80 group-hover:bg-[hsl(var(--v4v-gold)/0.1)]'
                  }`}>
                    <Icon className={`h-4 w-4 ${active ? 'text-[hsl(var(--v4v-gold-dark))]' : 'text-muted-foreground group-hover:text-[hsl(var(--v4v-gold-dark))]'}`} />
                  </div>
                  <div className="flex flex-col">
                    <span>{item.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  </div>
                </Link>
              );
            })}
          </nav>
          <Separator className="mx-4" />
          <div className="p-4">
            <Link href="/">
              <Button variant="outline" size="sm" className="w-full gap-2 hover:bg-[hsl(var(--v4v-gold)/0.1)] hover:border-[hsl(var(--v4v-gold)/0.3)]">
                <ChevronLeft className="h-4 w-4" />
                Back to Site
              </Button>
            </Link>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 bg-[hsl(var(--v4v-bg-muted))]">{children}</main>
      </div>
    </div>
  );
}
