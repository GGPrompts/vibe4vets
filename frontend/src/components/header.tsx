'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams, useRouter } from 'next/navigation';
import { useScrollDirection } from '@/hooks/use-scroll-direction';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

export function Header() {
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
        'fixed left-0 right-0 top-0 z-50 transition-all duration-300 ease-out',
        isHidden && '-translate-y-full',
        'bg-[hsl(var(--v4v-navy))] border-b border-[hsl(var(--v4v-navy-light))]',
        showShadow && 'shadow-lg'
      )}
      style={{ paddingRight: 'var(--removed-body-scroll-bar-size, 0px)' }}
    >
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-6">
        {/* Logo */}
        <Link href="/" className="flex shrink-0 items-center gap-3 group" aria-label="Vibe4Vets Home">
          <Image
            src="/brand/vibe4vets-logo.png"
            alt="Vibe4Vets"
            width={851}
            height={273}
            priority
            className="h-8 w-auto transition-transform duration-200 group-hover:scale-105"
            sizes="(max-width: 768px) 140px, 180px"
          />
        </Link>

        {/* Search Bar - Only on /search and /discover */}
        {showSearchBar && (
          <form onSubmit={handleSearch} className="relative mx-4 hidden max-w-md flex-1 md:block">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
            <Input
              type="text"
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 w-full rounded-full border-white/20 bg-white/10 pl-9 pr-4 text-sm text-white placeholder:text-white/50 focus:border-[hsl(var(--v4v-gold)/0.5)] focus:bg-white/15 focus:ring-[hsl(var(--v4v-gold)/0.2)]"
            />
          </form>
        )}

        {/* Navigation */}
        <nav className="flex shrink-0 items-center gap-5">
          <Link
            href="/search"
            className={cn(
              "text-sm font-medium transition-all duration-200",
              pathname === '/search'
                ? "text-[hsl(var(--v4v-gold))]"
                : "text-white/70 hover:text-[hsl(var(--v4v-gold))]"
            )}
          >
            Search
          </Link>
          <Link
            href="/discover"
            className={cn(
              "text-sm font-medium transition-all duration-200",
              pathname === '/discover'
                ? "text-[hsl(var(--v4v-gold))]"
                : "text-white/70 hover:text-[hsl(var(--v4v-gold))]"
            )}
          >
            Fresh Finds
          </Link>
          <Link
            href="/admin"
            className="text-sm font-medium text-white/70 transition-all duration-200 hover:text-[hsl(var(--v4v-gold))]"
          >
            Admin
          </Link>
        </nav>
      </div>
    </header>
  );
}
