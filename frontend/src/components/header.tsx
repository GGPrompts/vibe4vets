'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams, useRouter } from 'next/navigation';
import { useScrollDirection } from '@/hooks/use-scroll-direction';
import { useDebounce } from '@/hooks/use-debounce';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import {
  Search,
  Loader2,
  Bookmark,
  Menu,
  ZoomIn,
  ArrowRight,
} from 'lucide-react';
import { SortDropdownHeader, type SortOption } from '@/components/sort-dropdown-header';
import { useOptionalFilterContext } from '@/context/filter-context';
import { useOptionalSavedResources } from '@/context/saved-resources-context';
import { useOptionalMagnifier } from '@/context/magnifier-context';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

export function Header() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { isAtTop } = useScrollDirection();
  const filterContext = useOptionalFilterContext();
  const savedContext = useOptionalSavedResources();
  const magnifierContext = useOptionalMagnifier();
  const [isMounted, setIsMounted] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(true);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const mobileSearchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setIsMounted(true);
    const checkMobile = () => {
      setIsMobile(window.matchMedia('(pointer: coarse)').matches);
    };
    checkMobile();
    const mediaQuery = window.matchMedia('(pointer: coarse)');
    mediaQuery.addEventListener('change', checkMobile);
    return () => mediaQuery.removeEventListener('change', checkMobile);
  }, []);

  const isSearchPage = pathname === '/search';
  const isHomePage = pathname === '/';

  const resourceCount =
    isMounted && isHomePage && filterContext?.isEnabled
      ? filterContext.resourceCount
      : null;
  const isLoadingCount =
    isMounted && isHomePage && filterContext?.isEnabled
      ? filterContext.isLoadingCount
      : false;
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 300);
  const skipDebounceRef = useRef(false);

  const query = searchParams.get('q') || '';
  const zip = searchParams.get('zip') || '';

  const getDefaultSort = (): SortOption => {
    if (query) return 'relevance';
    if (zip) return 'distance';
    return 'newest';
  };
  const currentSort = (searchParams.get('sort') as SortOption) || getDefaultSort();

  useEffect(() => {
    if (isSearchPage) {
      setSearchQuery(searchParams.get('q') || '');
    } else {
      setSearchQuery('');
    }
  }, [isSearchPage, searchParams]);

  useEffect(() => {
    if (!isSearchPage) return;
    if (skipDebounceRef.current) {
      skipDebounceRef.current = false;
      return;
    }
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
    skipDebounceRef.current = true;
    const params = new URLSearchParams(searchParams.toString());
    if (searchQuery) {
      params.set('q', searchQuery);
    } else {
      params.delete('q');
    }
    router.push(`/search?${params.toString()}`);
    setIsMobileMenuOpen(false);
    setIsSearchExpanded(false);
  };

  const handleSortChange = useCallback(
    (newSort: SortOption) => {
      const params = new URLSearchParams(searchParams.toString());
      const defaultSort = getDefaultSort();

      if (newSort !== defaultSort) {
        params.set('sort', newSort);
      } else {
        params.delete('sort');
      }

      router.push(`/search?${params.toString()}`, { scroll: false });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [router, searchParams, query, zip]
  );

  const handleSearchExpand = () => {
    setIsSearchExpanded(true);
    setTimeout(() => searchInputRef.current?.focus(), 100);
  };

  const handleSearchCollapse = () => {
    if (!searchQuery) {
      setIsSearchExpanded(false);
    }
  };

  // Don't render on admin pages
  if (pathname.startsWith('/admin')) {
    return null;
  }

  const showShadow = !isAtTop;
  const savedCount = isMounted && savedContext ? savedContext.count : 0;
  const magnifierEnabled = magnifierContext?.enabled ?? false;
  const showMagnifier = isMounted && !isMobile && magnifierContext?.isHydrated;

  return (
    <header
      className={cn(
        'fixed left-0 right-0 top-0 z-50 transition-all duration-300 ease-out',
        'bg-v4v-navy',
        showShadow && 'shadow-lg shadow-black/20'
      )}
      style={{ paddingRight: 'var(--removed-body-scroll-bar-size, 0px)' }}
    >
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 md:h-16 md:px-6">
        {/* Logo */}
        <Link
          href="/"
          className="group relative flex shrink-0 items-center"
          aria-label="Vibe4Vets Home"
        >
          <Image
            src="/brand/vibe4vets-wordmark.png"
            alt="Vibe4Vets"
            width={391}
            height={68}
            priority
            className="h-7 w-auto brightness-0 invert transition-all duration-200 group-hover:opacity-90 md:h-8"
          />
        </Link>

        {/* Desktop: Center Search Bar */}
        <div className="hidden flex-1 items-center justify-center px-8 md:flex">
          <form
            onSubmit={handleSearch}
            className={cn(
              'relative flex items-center transition-all duration-300 ease-out',
              isSearchExpanded ? 'w-full max-w-lg' : 'w-auto'
            )}
          >
            {isSearchExpanded ? (
              <>
                <div className="relative w-full">
                  <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50" />
                  <Input
                    ref={searchInputRef}
                    type="text"
                    placeholder="Search veteran resources..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onBlur={handleSearchCollapse}
                    className="h-10 w-full rounded-full border-white/20 bg-white/10 pl-10 pr-12 text-sm text-white placeholder:text-white/40 focus:border-[hsl(var(--v4v-gold))] focus:bg-white/15 focus:ring-1 focus:ring-[hsl(var(--v4v-gold)/0.5)]"
                  />
                  <button
                    type="submit"
                    className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full bg-[hsl(var(--v4v-gold))] p-1.5 text-[hsl(var(--v4v-navy))] transition-all hover:bg-[hsl(var(--v4v-gold-light))]"
                    aria-label="Search"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </>
            ) : (
              <button
                type="button"
                onClick={handleSearchExpand}
                className="flex items-center gap-2.5 rounded-full border border-white/20 bg-white/5 px-4 py-2 text-sm text-white/70 transition-all duration-200 hover:border-white/30 hover:bg-white/10 hover:text-white"
              >
                <Search className="h-4 w-4" />
                <span>Search resources...</span>
                <kbd className="ml-2 hidden rounded bg-white/10 px-1.5 py-0.5 font-mono text-xs text-white/50 lg:inline-block">
                  /
                </kbd>
              </button>
            )}
          </form>

          {/* Sort dropdown - only on search page */}
          {isSearchPage && !isSearchExpanded && (
            <div className="ml-3">
              <SortDropdownHeader
                value={currentSort}
                onChange={handleSortChange}
                hasQuery={!!query}
                hasZip={!!zip}
              />
            </div>
          )}
        </div>

        {/* Desktop Navigation: Icon buttons with tooltips */}
        <nav className="hidden items-center gap-1 md:flex">
          {/* Search link with optional resource count badge */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Link
                href="/search"
                className={cn(
                  'relative flex h-10 items-center justify-center gap-2 rounded-full px-4 text-sm font-medium transition-all duration-200',
                  pathname === '/search'
                    ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                )}
              >
                <Search className="h-4 w-4" />
                <span>Search</span>
                {isHomePage && (isLoadingCount || resourceCount !== null) && (
                  <span className="inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))] px-1.5 text-xs font-semibold text-[hsl(var(--v4v-navy))]">
                    {isLoadingCount ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      resourceCount?.toLocaleString()
                    )}
                  </span>
                )}
              </Link>
            </TooltipTrigger>
            <TooltipContent side="bottom" sideOffset={8}>
              Browse all resources
            </TooltipContent>
          </Tooltip>

          {/* Saved link with badge */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Link
                href="/saved"
                className={cn(
                  'relative flex h-10 items-center justify-center gap-2 rounded-full px-4 text-sm font-medium transition-all duration-200',
                  pathname === '/saved'
                    ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                )}
              >
                <Bookmark
                  className={cn(
                    'h-4 w-4 transition-colors',
                    savedCount > 0 && 'fill-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-gold))]'
                  )}
                />
                <span>Saved</span>
                {savedCount > 0 && (
                  <span className="inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))] px-1.5 text-xs font-semibold text-[hsl(var(--v4v-navy))]">
                    {savedCount}
                  </span>
                )}
              </Link>
            </TooltipTrigger>
            <TooltipContent side="bottom" sideOffset={8}>
              {savedCount > 0 ? `${savedCount} saved resources` : 'No saved resources'}
            </TooltipContent>
          </Tooltip>

          {/* Magnifier toggle */}
          {showMagnifier && (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  onClick={() => magnifierContext?.toggleEnabled()}
                  aria-pressed={magnifierEnabled}
                  aria-label={magnifierEnabled ? 'Disable magnifier' : 'Enable magnifier'}
                  className={cn(
                    'flex h-10 w-10 items-center justify-center rounded-full transition-all duration-200',
                    magnifierEnabled
                      ? 'bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]'
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                  )}
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom" sideOffset={8}>
                {magnifierEnabled ? 'Disable magnifier (Alt+M)' : 'Enable magnifier (Alt+M)'}
              </TooltipContent>
            </Tooltip>
          )}
        </nav>

        {/* Mobile: Menu button + Sheet */}
        <div className="flex items-center gap-2 md:hidden">
          {/* Quick search icon for mobile */}
          <Link
            href="/search"
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-full transition-colors',
              pathname === '/search'
                ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                : 'text-white/80 hover:bg-white/10'
            )}
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
          </Link>

          {/* Saved icon with badge */}
          <Link
            href="/saved"
            className={cn(
              'relative flex h-10 w-10 items-center justify-center rounded-full transition-colors',
              pathname === '/saved'
                ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                : 'text-white/80 hover:bg-white/10'
            )}
            aria-label="Saved resources"
          >
            <Bookmark
              className={cn(
                'h-5 w-5',
                savedCount > 0 && 'fill-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-gold))]'
              )}
            />
            {savedCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))] px-1 text-[10px] font-bold text-[hsl(var(--v4v-navy))]">
                {savedCount}
              </span>
            )}
          </Link>

          {/* Menu button */}
          <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
            <SheetTrigger asChild>
              <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/10 hover:text-white"
                aria-label="Open menu"
              >
                <Menu className="h-5 w-5" />
              </button>
            </SheetTrigger>
            <SheetContent
              side="right"
              className="w-full border-l-0 bg-[hsl(var(--v4v-navy))] p-0 sm:max-w-sm"
            >
              <SheetHeader className="border-b border-white/10 px-6 py-4">
                <div className="flex items-center justify-between">
                  <SheetTitle className="text-lg font-semibold text-white">
                    Menu
                  </SheetTitle>
                </div>
              </SheetHeader>

              <div className="flex flex-col gap-6 p-6">
                {/* Mobile search */}
                <form onSubmit={handleSearch} className="relative">
                  <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50" />
                  <Input
                    ref={mobileSearchInputRef}
                    type="text"
                    placeholder="Search resources..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="h-12 w-full rounded-xl border-white/20 bg-white/10 pl-10 pr-4 text-base text-white placeholder:text-white/40 focus:border-[hsl(var(--v4v-gold))] focus:bg-white/15 focus:ring-1 focus:ring-[hsl(var(--v4v-gold)/0.5)]"
                  />
                </form>

                {/* Mobile sort (only on search page) */}
                {isSearchPage && (
                  <div className="space-y-2">
                    <p className="text-xs font-medium uppercase tracking-wider text-white/50">
                      Sort by
                    </p>
                    <SortDropdownHeader
                      value={currentSort}
                      onChange={(sort) => {
                        handleSortChange(sort);
                        setIsMobileMenuOpen(false);
                      }}
                      hasQuery={!!query}
                      hasZip={!!zip}
                      className="w-full [&_button]:w-full [&_button]:justify-center"
                    />
                  </div>
                )}

                {/* Mobile nav links */}
                <nav className="flex flex-col gap-1">
                  <p className="mb-2 text-xs font-medium uppercase tracking-wider text-white/50">
                    Navigation
                  </p>
                  <Link
                    href="/search"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center gap-3 rounded-xl px-4 py-3 text-base font-medium transition-colors',
                      pathname === '/search'
                        ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                        : 'text-white/80 hover:bg-white/10 hover:text-white'
                    )}
                  >
                    <Search className="h-5 w-5" />
                    Search
                    {isHomePage && resourceCount !== null && (
                      <span className="ml-auto rounded-full bg-[hsl(var(--v4v-gold))] px-2 py-0.5 text-xs font-semibold text-[hsl(var(--v4v-navy))]">
                        {resourceCount?.toLocaleString()}
                      </span>
                    )}
                  </Link>
                  <Link
                    href="/saved"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center gap-3 rounded-xl px-4 py-3 text-base font-medium transition-colors',
                      pathname === '/saved'
                        ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                        : 'text-white/80 hover:bg-white/10 hover:text-white'
                    )}
                  >
                    <Bookmark
                      className={cn(
                        'h-5 w-5',
                        savedCount > 0 && 'fill-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-gold))]'
                      )}
                    />
                    Saved
                    {savedCount > 0 && (
                      <span className="ml-auto rounded-full bg-[hsl(var(--v4v-gold))] px-2 py-0.5 text-xs font-semibold text-[hsl(var(--v4v-navy))]">
                        {savedCount}
                      </span>
                    )}
                  </Link>
                  <Link
                    href="/about"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center gap-3 rounded-xl px-4 py-3 text-base font-medium transition-colors',
                      pathname === '/about'
                        ? 'bg-white/15 text-[hsl(var(--v4v-gold))]'
                        : 'text-white/80 hover:bg-white/10 hover:text-white'
                    )}
                  >
                    About
                  </Link>
                </nav>
              </div>

              {/* Footer */}
              <div className="absolute bottom-0 left-0 right-0 border-t border-white/10 bg-white/5 px-6 py-4">
                <p className="text-center text-xs text-white/40">
                  Helping veterans find resources
                </p>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Keyboard shortcut handler for "/" to open search */}
      <KeyboardShortcuts
        onSearchShortcut={() => {
          if (window.innerWidth >= 768) {
            handleSearchExpand();
          } else {
            setIsMobileMenuOpen(true);
            setTimeout(() => mobileSearchInputRef.current?.focus(), 300);
          }
        }}
      />
    </header>
  );
}

// Keyboard shortcut component
function KeyboardShortcuts({ onSearchShortcut }: { onSearchShortcut: () => void }) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // "/" to focus search (only if not in an input/textarea)
      if (
        e.key === '/' &&
        !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)
      ) {
        e.preventDefault();
        onSearchShortcut();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onSearchShortcut]);

  return null;
}
