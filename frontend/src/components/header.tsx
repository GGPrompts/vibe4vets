'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams, useRouter } from 'next/navigation';
import { useScrollDirection } from '@/hooks/use-scroll-direction';
import { useDebounce } from '@/hooks/use-debounce';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Search, Loader2, Bookmark } from 'lucide-react';
import { SortDropdownHeader, type SortOption } from '@/components/sort-dropdown-header';
import { MagnifierToggle } from '@/components/MagnifierToggle';
import { useOptionalFilterContext } from '@/context/filter-context';
import { useOptionalSavedResources } from '@/context/saved-resources-context';

export function Header() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { isAtTop } = useScrollDirection();
  const filterContext = useOptionalFilterContext();
  const savedContext = useOptionalSavedResources();
  const [isMounted, setIsMounted] = useState(false);

  // Avoid hydration mismatch - badge only renders after mount
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const isSearchPage = pathname === '/search';
  const isHomePage = pathname === '/';

  // Get resource count from filter context (only active on home page, after mount)
  const resourceCount = isMounted && isHomePage && filterContext?.isEnabled ? filterContext.resourceCount : null;
  const isLoadingCount = isMounted && isHomePage && filterContext?.isEnabled ? filterContext.isLoadingCount : false;
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 300);
  const skipDebounceRef = useRef(false);

  // Get current sort from URL
  const query = searchParams.get('q') || '';
  const currentSort = (searchParams.get('sort') as SortOption) || (query ? 'relevance' : 'newest');

  // Sync search query from URL params when on search page
  useEffect(() => {
    if (isSearchPage) {
      setSearchQuery(searchParams.get('q') || '');
    } else {
      setSearchQuery('');
    }
  }, [isSearchPage, searchParams]);

  // Live search: update URL when debounced query changes (only on search page)
  useEffect(() => {
    if (!isSearchPage) return;
    if (skipDebounceRef.current) {
      skipDebounceRef.current = false;
      return;
    }
    // Only update if different from current URL query
    if (debouncedQuery === query) return;

    const params = new URLSearchParams(searchParams.toString());
    if (debouncedQuery) {
      params.set('q', debouncedQuery);
    } else {
      params.delete('q');
    }
    router.push(`/search?${params.toString()}`, { scroll: false });
  }, [debouncedQuery, isSearchPage, query, router, searchParams]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Skip the debounce effect since we're navigating immediately
    skipDebounceRef.current = true;
    const params = new URLSearchParams(searchParams.toString());
    if (searchQuery) {
      params.set('q', searchQuery);
    } else {
      params.delete('q');
    }
    router.push(`/search?${params.toString()}`);
  };

  const handleSortChange = useCallback((newSort: SortOption) => {
    const params = new URLSearchParams(searchParams.toString());
    const defaultSort = query ? 'relevance' : 'newest';

    if (newSort !== defaultSort) {
      params.set('sort', newSort);
    } else {
      params.delete('sort');
    }

    router.push(`/search?${params.toString()}`, { scroll: false });
  }, [router, searchParams, query]);

  // Don't render on admin pages (they have their own layout)
  if (pathname.startsWith('/admin')) {
    return null;
  }

  // Header always visible (no longer hides on scroll)
  const showShadow = !isAtTop;

  return (
    <header
      className={cn(
        'fixed left-0 right-0 top-0 z-50 transition-all duration-300 ease-out',
        'bg-v4v-navy border-b border-[hsl(var(--v4v-navy-light))]',
        showShadow && 'shadow-lg'
      )}
      style={{ paddingRight: 'var(--removed-body-scroll-bar-size, 0px)' }}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-6">
        {/* Logo */}
        <Link href="/" className="flex shrink-0 items-center group" aria-label="Vibe4Vets Home">
          <Image
            src="/brand/vibe4vets-wordmark.png"
            alt="Vibe4Vets"
            width={391}
            height={68}
            priority
            className="h-9 w-auto transition-transform duration-200 group-hover:scale-105 brightness-0 invert"
          />
        </Link>

        {/* Search Bar + Sort */}
        <div className="flex items-center gap-2 mx-4 flex-1 max-w-xl">
          <form onSubmit={handleSearch} className="relative hidden flex-1 md:block">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/60" />
            <Input
              type="text"
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-full rounded-full border-white/20 bg-white/10 pl-9 pr-4 text-sm text-white placeholder:text-white/50 focus:border-[hsl(var(--v4v-gold))] focus:bg-white/15 focus:ring-[hsl(var(--v4v-gold)/0.3)]"
            />
          </form>

          {/* Sort dropdown - only on search page */}
          {isSearchPage && (
            <SortDropdownHeader
              value={currentSort}
              onChange={handleSortChange}
              hasQuery={!!query}
              className="hidden md:block"
            />
          )}
        </div>

        {/* Navigation */}
        <nav className="flex shrink-0 items-center gap-6">
          <MagnifierToggle />
          <Link
            href="/search"
            className={cn(
              "text-base font-medium transition-all duration-200 flex items-center gap-2",
              pathname === '/search'
                ? "text-[hsl(var(--v4v-gold))]"
                : "text-white/80 hover:text-[hsl(var(--v4v-gold))]"
            )}
          >
            Search
            {/* Resource count badge - only on home page */}
            {isHomePage && (isLoadingCount || resourceCount !== null) && (
              <span className="inline-flex items-center justify-center min-w-[2rem] h-6 px-2 text-sm font-medium rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                {isLoadingCount ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  resourceCount?.toLocaleString()
                )}
              </span>
            )}
          </Link>
          <Link
            href="/saved"
            className={cn(
              "text-base font-medium transition-all duration-200 flex items-center gap-2",
              pathname === '/saved'
                ? "text-[hsl(var(--v4v-gold))]"
                : "text-white/80 hover:text-[hsl(var(--v4v-gold))]"
            )}
          >
            <Bookmark className={cn(
              "h-4 w-4 transition-colors",
              isMounted && savedContext && savedContext.count > 0
                ? "text-[hsl(var(--v4v-gold))] fill-[hsl(var(--v4v-gold))]"
                : ""
            )} />
            Saved
            {/* Saved count badge */}
            {isMounted && savedContext && savedContext.count > 0 && (
              <span className="inline-flex items-center justify-center min-w-[1.5rem] h-5 px-1.5 text-xs font-medium rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                {savedContext.count}
              </span>
            )}
          </Link>
          <Link
            href="/admin"
            className="text-base font-medium text-white/80 transition-all duration-200 hover:text-[hsl(var(--v4v-gold))]"
          >
            Admin
          </Link>
        </nav>
      </div>
    </header>
  );
}
