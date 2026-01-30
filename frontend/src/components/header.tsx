'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams, useRouter } from 'next/navigation';
import { useScrollDirection } from '@/hooks/use-scroll-direction';
import { useDebounce } from '@/hooks/use-debounce';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Loader2, Bookmark, Menu, X } from 'lucide-react';
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
  const [searchExpanded, setSearchExpanded] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const isSearchPage = pathname === '/search';
  const isHomePage = pathname === '/';

  const resourceCount = isMounted && isHomePage && filterContext?.isEnabled ? filterContext.resourceCount : null;
  const isLoadingCount = isMounted && isHomePage && filterContext?.isEnabled ? filterContext.isLoadingCount : false;
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 300);
  const skipDebounceRef = useRef(false);
  const isTypingRef = useRef(false);

  const query = searchParams.get('q') || '';
  const zip = searchParams.get('zip') || '';
  const getDefaultSort = (): SortOption => {
    if (query) return 'relevance';
    if (zip) return 'distance';
    return 'newest';
  };
  const currentSort = (searchParams.get('sort') as SortOption) || getDefaultSort();

  // Sync search query from URL only on initial load or when navigating to search page
  // Don't sync while user is actively typing (prevents dropped keystrokes)
  useEffect(() => {
    if (isTypingRef.current) return; // Don't overwrite while typing
    if (isSearchPage) {
      setSearchQuery(searchParams.get('q') || '');
    } else {
      setSearchQuery('');
    }
  }, [isSearchPage, searchParams]);

  // Push debounced query to URL
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

    // Clear typing flag after URL update settles
    setTimeout(() => {
      isTypingRef.current = false;
    }, 100);
  }, [debouncedQuery, isSearchPage, query, router, searchParams]);

  // Track when user is typing
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    isTypingRef.current = true;
    setSearchQuery(e.target.value);
  }, []);

  // Focus search input when expanded
  useEffect(() => {
    if (searchExpanded && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [searchExpanded]);

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
    setSearchExpanded(false);
  };

  const handleSortChange = useCallback((newSort: SortOption) => {
    const params = new URLSearchParams(searchParams.toString());
    const defaultSort = getDefaultSort();

    if (newSort !== defaultSort) {
      params.set('sort', newSort);
    } else {
      params.delete('sort');
    }

    router.push(`/search?${params.toString()}`, { scroll: false });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, searchParams, query, zip]);

  // Open filter sidebar (from context)
  const handleOpenFilters = () => {
    filterContext?.openSidebar();
    // Navigate to search page if not already there
    if (!isSearchPage) {
      router.push('/search');
    }
  };

  // Don't render on admin pages
  if (pathname.startsWith('/admin')) {
    return null;
  }

  const showShadow = !isAtTop;
  const savedCount = isMounted && savedContext ? savedContext.count : 0;

  const NavLink = ({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) => {
    const isActive = pathname === href;
    return (
      <Link
        href={href}
        className={cn(
          "relative group px-1 py-2 text-base font-medium transition-colors duration-200",
          isActive
            ? "text-[hsl(var(--v4v-gold))]"
            : "text-white/80 hover:text-white",
          className
        )}
      >
        {children}
        {/* Gold underline accent */}
        <span className={cn(
          "absolute -bottom-1 left-0 h-0.5 bg-gradient-to-r from-[hsl(var(--v4v-gold))] to-[hsl(var(--v4v-gold-light))]",
          "transition-all duration-300 ease-out",
          isActive ? "w-full" : "w-0 group-hover:w-full"
        )} />
      </Link>
    );
  };

  return (
    <>
      <header
        className={cn(
          'fixed left-0 right-0 top-0 z-50 transition-all duration-300 ease-out',
          showShadow && 'shadow-xl shadow-black/20'
        )}
        style={{ paddingRight: 'var(--removed-body-scroll-bar-size, 0px)' }}
      >
        {/* Gold accent line at top */}
        <div className="h-1 w-full bg-gradient-to-r from-[hsl(var(--v4v-gold))] via-[hsl(var(--v4v-gold-light))] to-[hsl(var(--v4v-gold))]" />

        {/* Main header bar */}
        <div className="bg-v4v-navy border-b border-white/10">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-14 items-center justify-between gap-3">

              {/* Left section: Filter button (mobile) + Logo */}
              <div className="flex items-center gap-2">
                {/* Mobile Filter Button - opens sidebar */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleOpenFilters}
                  className="h-9 w-9 rounded-lg md:hidden text-white/80 hover:text-[hsl(var(--v4v-gold))] hover:bg-white/10"
                  aria-label="Open filters"
                >
                  <Menu className="h-5 w-5" />
                </Button>

                {/* Logo */}
                <Link
                  href="/"
                  className="flex shrink-0 items-center group relative overflow-visible"
                  aria-label="VRD.ai Home"
                >
                  <div className="absolute -inset-2 rounded-lg bg-[hsl(var(--v4v-gold)/0.15)] opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-lg" />
                  <Image
                    src="/vrd-logo.png"
                    alt="VRD.ai"
                    width={400}
                    height={150}
                    priority
                    className="relative h-16 sm:h-20 w-auto transition-all duration-300 group-hover:scale-105 -my-6"
                  />
                </Link>
              </div>

              {/* Desktop Search Bar */}
              <div className="hidden md:flex items-center gap-3 flex-1 max-w-xl mx-6">
                <form onSubmit={handleSearch} className="relative flex-1 group">
                  <div className={cn(
                    "absolute inset-0 rounded-full transition-all duration-300",
                    "bg-gradient-to-r from-[hsl(var(--v4v-gold)/0.3)] to-[hsl(var(--v4v-gold-light)/0.2)]",
                    "opacity-0 group-focus-within:opacity-100 blur-md"
                  )} />
                  <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50 transition-colors group-focus-within:text-[hsl(var(--v4v-gold))]" />
                  <Input
                    ref={searchInputRef}
                    type="text"
                    placeholder="Search Veteran resources..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                    className={cn(
                      "relative h-10 w-full rounded-full pl-10 pr-4",
                      "bg-white/10 border-white/20 text-white placeholder:text-white/40",
                      "transition-all duration-300",
                      "focus:bg-white/15 focus:border-[hsl(var(--v4v-gold)/0.5)]",
                      "focus:ring-2 focus:ring-[hsl(var(--v4v-gold)/0.25)] focus:ring-offset-0"
                    )}
                  />
                </form>

                {/* Sort dropdown - search page only */}
                {isSearchPage && (
                  <SortDropdownHeader
                    value={currentSort}
                    onChange={handleSortChange}
                    hasQuery={!!query}
                    hasZip={!!zip}
                  />
                )}
              </div>

              {/* Desktop Navigation */}
              <nav className="hidden md:flex items-center gap-5">
                <NavLink href="/search">
                  <span className="flex items-center gap-2">
                    Search
                    {isHomePage && (isLoadingCount || resourceCount !== null) && (
                      <span className="inline-flex items-center justify-center min-w-[1.75rem] h-5 px-1.5 text-xs font-semibold rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                        {isLoadingCount ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          resourceCount?.toLocaleString()
                        )}
                      </span>
                    )}
                  </span>
                </NavLink>

                <NavLink href="/saved">
                  <span className="flex items-center gap-2">
                    <Bookmark className={cn(
                      "h-4 w-4 transition-all duration-200",
                      savedCount > 0
                        ? "text-[hsl(var(--v4v-gold))] fill-[hsl(var(--v4v-gold))]"
                        : ""
                    )} />
                    Saved
                    {savedCount > 0 && (
                      <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 text-xs font-semibold rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                        {savedCount}
                      </span>
                    )}
                  </span>
                </NavLink>

                <MagnifierToggle />
              </nav>

              {/* Mobile Right Controls: Search + Saved */}
              <div className="flex md:hidden items-center gap-1">
                {/* Mobile Search Toggle */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSearchExpanded(!searchExpanded)}
                  className={cn(
                    "h-9 w-9 rounded-lg",
                    "text-white/80 hover:text-[hsl(var(--v4v-gold))] hover:bg-white/10",
                    searchExpanded && "bg-white/10 text-[hsl(var(--v4v-gold))]"
                  )}
                  aria-label={searchExpanded ? "Close search" : "Open search"}
                >
                  {searchExpanded ? <X className="h-5 w-5" /> : <Search className="h-5 w-5" />}
                </Button>

                {/* Mobile Saved Link */}
                <Link
                  href="/saved"
                  className={cn(
                    "relative h-9 w-9 rounded-lg flex items-center justify-center",
                    "text-white/80 hover:text-[hsl(var(--v4v-gold))] hover:bg-white/10 transition-colors",
                    pathname === '/saved' && "text-[hsl(var(--v4v-gold))]"
                  )}
                  aria-label="Saved resources"
                >
                  <Bookmark className={cn(
                    "h-5 w-5",
                    savedCount > 0 && "fill-current"
                  )} />
                  {savedCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center min-w-[1rem] h-4 px-1 text-[10px] font-bold rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                      {savedCount}
                    </span>
                  )}
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Search Dropdown */}
        <div className={cn(
          "md:hidden overflow-hidden transition-all duration-300 ease-out bg-v4v-navy border-b border-white/10",
          searchExpanded ? "max-h-20 opacity-100" : "max-h-0 opacity-0"
        )}>
          <div className="px-4 py-3">
            <form onSubmit={handleSearch} className="relative">
              <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50" />
              <Input
                type="text"
                placeholder="Search Veteran resources..."
                value={searchQuery}
                onChange={handleSearchChange}
                className={cn(
                  "h-10 w-full rounded-full pl-10 pr-20",
                  "bg-white/10 border-white/20 text-white placeholder:text-white/40",
                  "focus:bg-white/15 focus:border-[hsl(var(--v4v-gold)/0.5)]",
                  "focus:ring-2 focus:ring-[hsl(var(--v4v-gold)/0.25)]"
                )}
                autoFocus={searchExpanded}
              />
              <Button
                type="submit"
                size="sm"
                className="absolute right-1.5 top-1/2 -translate-y-1/2 h-7 px-3 rounded-full bg-[hsl(var(--v4v-gold))] hover:bg-[hsl(var(--v4v-gold-light))] text-[hsl(var(--v4v-navy))] font-semibold text-xs"
              >
                Search
              </Button>
            </form>
          </div>
        </div>
      </header>
    </>
  );
}
