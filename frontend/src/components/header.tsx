'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams, useRouter } from 'next/navigation';
import { useScrollDirection } from '@/hooks/use-scroll-direction';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

interface HeaderProps {
  variant?: 'default' | 'transparent';
}

export function Header({ variant = 'default' }: HeaderProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { scrollDirection, isAtTop } = useScrollDirection();

  const isSearchPage = pathname === '/search';
  const isDiscoverPage = pathname === '/discover';
  const showSearchBar = isSearchPage || isDiscoverPage;
  const [searchQuery, setSearchQuery] = useState('');

  // Sync search query from URL params when on search page
  useEffect(() => {
    if (isSearchPage) {
      setSearchQuery(searchParams.get('q') || '');
      return;
    }

    if (!showSearchBar) return;
    setSearchQuery('');
  }, [isSearchPage, searchParams, showSearchBar]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (searchQuery) {
      params.set('q', searchQuery);
    } else {
      params.delete('q');
    }
    router.push(`/search?${params.toString()}`);
  };

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
      style={{ paddingRight: 'var(--removed-body-scroll-bar-size, 0px)' }}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-6">
        {/* Logo */}
        <Link href="/" className="flex shrink-0 items-center gap-3" aria-label="Vibe4Vets Home">
          <Image
            src="/brand/vibe4vets-logo.png"
            alt="Vibe4Vets"
            width={851}
            height={273}
            priority
            className="h-8 w-auto"
            sizes="128px"
          />
        </Link>

        {/* Search Bar - Only on /search and /discover */}
        {showSearchBar && (
          <form onSubmit={handleSearch} className="relative mx-4 hidden max-w-md flex-1 md:block">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-full rounded-full bg-white/10 pl-9 pr-4 text-sm text-white placeholder:text-white/50 focus:bg-white/20"
            />
          </form>
        )}

        {/* Navigation */}
        <nav className="flex shrink-0 items-center gap-6">
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
