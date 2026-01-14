'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useScrollDirection } from '@/hooks/use-scroll-direction';
import { cn } from '@/lib/utils';

interface HeaderProps {
  variant?: 'default' | 'transparent';
}

export function Header({ variant = 'default' }: HeaderProps) {
  const pathname = usePathname();
  const { scrollDirection, isAtTop } = useScrollDirection();

  // Don't render on admin pages (they have their own layout)
  if (pathname.startsWith('/admin')) {
    return null;
  }

  const isHidden = scrollDirection === 'down' && !isAtTop;
  const showShadow = !isAtTop;

  return (
    <header
      className={cn(
        'fixed left-0 right-0 top-0 z-50 transition-transform duration-300 ease-out',
        isHidden && '-translate-y-full',
        variant === 'default' && 'bg-[hsl(var(--v4v-navy))]',
        variant === 'transparent' && !showShadow && 'bg-transparent',
        variant === 'transparent' && showShadow && 'bg-[hsl(var(--v4v-navy))]',
        showShadow && 'shadow-lg'
      )}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <span className="font-display text-xl text-white">Vibe4Vets</span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-6">
          <Link
            href="/search"
            className="text-sm font-medium text-white/80 transition-colors hover:text-[hsl(var(--v4v-gold))]"
          >
            Search
          </Link>
          <Link
            href="/discover"
            className="text-sm font-medium text-white/80 transition-colors hover:text-[hsl(var(--v4v-gold))]"
          >
            Fresh Finds
          </Link>
          <Link
            href="/admin"
            className="text-sm font-medium text-white/80 transition-colors hover:text-[hsl(var(--v4v-gold))]"
          >
            Admin
          </Link>
        </nav>
      </div>
    </header>
  );
}
