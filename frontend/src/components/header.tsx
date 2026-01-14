'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, ChevronDown, Home, Search, Compass, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/search', label: 'Search', icon: Search },
  { href: '/discover', label: 'Discover', icon: Compass },
];

const hubItems = [
  { href: '/hubs/employment', label: 'Employment', color: 'bg-v4v-employment' },
  { href: '/hubs/training', label: 'Training', color: 'bg-v4v-training' },
  { href: '/hubs/housing', label: 'Housing', color: 'bg-v4v-housing' },
  { href: '/hubs/legal', label: 'Legal', color: 'bg-v4v-legal' },
];

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [hubsOpen, setHubsOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  const isHubActive = hubItems.some((hub) => pathname.startsWith(hub.href));

  // Don't render header on admin pages (admin has its own layout)
  if (pathname.startsWith('/admin')) {
    return null;
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo/Brand */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
            <span className="font-display text-lg font-bold text-primary-foreground">V4V</span>
          </div>
          <div className="flex flex-col">
            <span className="font-display text-xl font-semibold text-foreground group-hover:text-v4v-gold transition-colors">
              Vibe4Vets
            </span>
            <span className="hidden sm:block text-[10px] uppercase tracking-widest text-muted-foreground">
              Veteran Resource Directory
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  active
                    ? 'bg-primary text-primary-foreground'
                    : 'text-foreground/70 hover:text-foreground hover:bg-muted'
                }`}
              >
                {item.label}
              </Link>
            );
          })}

          {/* Resource Hubs Dropdown */}
          <div
            className="relative"
            onMouseEnter={() => setHubsOpen(true)}
            onMouseLeave={() => setHubsOpen(false)}
          >
            <button
              className={`flex items-center gap-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                isHubActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-foreground/70 hover:text-foreground hover:bg-muted'
              }`}
            >
              Resource Hubs
              <ChevronDown
                className={`h-4 w-4 transition-transform ${hubsOpen ? 'rotate-180' : ''}`}
              />
            </button>

            {/* Dropdown Menu */}
            {hubsOpen && (
              <div className="absolute top-full left-0 mt-1 w-56 rounded-lg border bg-card p-2 shadow-lg">
                {hubItems.map((hub) => (
                  <Link
                    key={hub.href}
                    href={hub.href}
                    className={`flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${
                      pathname === hub.href
                        ? 'bg-muted font-medium'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <span className={`h-2.5 w-2.5 rounded-full ${hub.color}`} />
                    {hub.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </nav>

        {/* Mobile Menu */}
        <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-80">
            <SheetHeader>
              <SheetTitle className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                  <span className="font-display text-sm font-bold text-primary-foreground">V4V</span>
                </div>
                <span className="font-display">Vibe4Vets</span>
              </SheetTitle>
            </SheetHeader>

            <nav className="flex flex-col gap-1 mt-6">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors ${
                      active
                        ? 'bg-primary text-primary-foreground'
                        : 'text-foreground/70 hover:bg-muted hover:text-foreground'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </Link>
                );
              })}

              {/* Mobile Resource Hubs Section */}
              <div className="mt-4 mb-2">
                <div className="flex items-center gap-2 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <Building2 className="h-4 w-4" />
                  Resource Hubs
                </div>
              </div>

              {hubItems.map((hub) => (
                <Link
                  key={hub.href}
                  href={hub.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors ${
                    pathname === hub.href
                      ? 'bg-primary text-primary-foreground'
                      : 'text-foreground/70 hover:bg-muted hover:text-foreground'
                  }`}
                >
                  <span className={`h-3 w-3 rounded-full ${hub.color}`} />
                  {hub.label}
                </Link>
              ))}
            </nav>
          </SheetContent>
        </Sheet>
      </div>

      {/* Gold accent line at bottom */}
      <div className="h-0.5 bg-gradient-to-r from-transparent via-v4v-gold to-transparent opacity-50" />
    </header>
  );
}
