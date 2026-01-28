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
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Search, Loader2, Bookmark, Menu, X, ChevronRight } from 'lucide-react';
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchExpanded, setSearchExpanded] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const mobileSearchInputRef = useRef<HTMLInputElement>(null);

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
    setMobileMenuOpen(false);
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

  const MobileNavLink = ({ href, children, onClick }: { href: string; children: React.ReactNode; onClick?: () => void }) => {
    const isActive = pathname === href;
    return (
      <Link
        href={href}
        onClick={onClick}
        className={cn(
          "flex items-center justify-between px-4 py-4 rounded-xl transition-all duration-200",
          "text-lg font-medium",
          isActive
            ? "bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold))]"
            : "text-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.05)]"
        )}
      >
        {children}
        <ChevronRight className={cn(
          "w-5 h-5 transition-transform duration-200",
          isActive ? "text-[hsl(var(--v4v-gold))]" : "text-[hsl(var(--v4v-navy-muted))]"
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
            <div className="flex h-16 items-center justify-between gap-4">
              {/* Logo with dramatic hover */}
              <Link
                href="/"
                className="flex shrink-0 items-center group relative"
                aria-label="Vibe4Vets Home"
              >
                {/* Glow effect on hover */}
                <div className="absolute -inset-3 rounded-xl bg-[hsl(var(--v4v-gold)/0.15)] opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl" />
                <Image
                  src="/brand/vibe4vets-wordmark.png"
                  alt="Vibe4Vets"
                  width={391}
                  height={68}
                  priority
                  className="relative h-8 sm:h-9 w-auto transition-all duration-300 group-hover:scale-105 brightness-0 invert"
                />
              </Link>

              {/* Desktop Search Bar - Expandable */}
              <div className="hidden md:flex items-center gap-3 flex-1 max-w-xl mx-8">
                <div className={cn(
                  "relative flex-1 transition-all duration-300 ease-out",
                  searchExpanded ? "opacity-100" : "opacity-100"
                )}>
                  <form onSubmit={handleSearch} className="relative group">
                    <div className={cn(
                      "absolute inset-0 rounded-full transition-all duration-300",
                      "bg-gradient-to-r from-[hsl(var(--v4v-gold)/0.3)] to-[hsl(var(--v4v-gold-light)/0.2)]",
                      "opacity-0 group-focus-within:opacity-100 blur-md"
                    )} />
                    <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50 transition-colors group-focus-within:text-[hsl(var(--v4v-gold))]" />
                    <Input
                      ref={searchInputRef}
                      type="text"
                      placeholder="Search veteran resources..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className={cn(
                        "relative h-11 w-full rounded-full pl-11 pr-4",
                        "bg-white/10 border-white/20 text-white placeholder:text-white/40",
                        "transition-all duration-300",
                        "focus:bg-white/15 focus:border-[hsl(var(--v4v-gold)/0.5)]",
                        "focus:ring-2 focus:ring-[hsl(var(--v4v-gold)/0.25)] focus:ring-offset-0"
                      )}
                    />
                  </form>
                </div>

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
              <nav className="hidden md:flex items-center gap-6">
                <NavLink href="/search">
                  <span className="flex items-center gap-2">
                    Search
                    {isHomePage && (isLoadingCount || resourceCount !== null) && (
                      <span className="inline-flex items-center justify-center min-w-[2rem] h-6 px-2 text-sm font-semibold rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                        {isLoadingCount ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
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
                      <span className="inline-flex items-center justify-center min-w-[1.5rem] h-5 px-1.5 text-xs font-semibold rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                        {savedCount}
                      </span>
                    )}
                  </span>
                </NavLink>

                <MagnifierToggle />
              </nav>

              {/* Mobile Controls */}
              <div className="flex md:hidden items-center gap-2">
                {/* Mobile Search Button */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSearchExpanded(!searchExpanded)}
                  className={cn(
                    "h-10 w-10 rounded-full",
                    "text-white/80 hover:text-[hsl(var(--v4v-gold))] hover:bg-white/10",
                    searchExpanded && "bg-white/10 text-[hsl(var(--v4v-gold))]"
                  )}
                  aria-label={searchExpanded ? "Close search" : "Open search"}
                >
                  {searchExpanded ? <X className="h-5 w-5" /> : <Search className="h-5 w-5" />}
                </Button>

                {/* Mobile Menu Button */}
                <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
                  <SheetTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 rounded-full text-white/80 hover:text-[hsl(var(--v4v-gold))] hover:bg-white/10"
                      aria-label="Open menu"
                    >
                      <Menu className="h-5 w-5" />
                    </Button>
                  </SheetTrigger>

                  <SheetContent
                    side="right"
                    className="w-full sm:w-80 bg-gradient-to-b from-white to-[hsl(var(--v4v-bg-base))] border-l-0 p-0"
                  >
                    {/* Mobile menu header */}
                    <div className="bg-v4v-navy p-6 pb-8">
                      <SheetHeader>
                        <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
                      </SheetHeader>
                      <Image
                        src="/brand/vibe4vets-wordmark.png"
                        alt="Vibe4Vets"
                        width={391}
                        height={68}
                        className="h-8 w-auto brightness-0 invert"
                      />
                      {/* Decorative gold line */}
                      <div className="mt-6 h-0.5 w-16 bg-gradient-to-r from-[hsl(var(--v4v-gold))] to-transparent rounded-full" />
                    </div>

                    {/* Mobile Search */}
                    <div className="p-6 border-b border-[hsl(var(--border))]">
                      <form onSubmit={handleSearch} className="relative">
                        <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[hsl(var(--v4v-navy-muted))]" />
                        <Input
                          ref={mobileSearchInputRef}
                          type="text"
                          placeholder="Search resources..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className={cn(
                            "h-12 w-full rounded-xl pl-11 pr-4",
                            "bg-white border-[hsl(var(--border))]",
                            "text-[hsl(var(--v4v-navy))] placeholder:text-[hsl(var(--v4v-navy-muted))]",
                            "focus:border-[hsl(var(--v4v-gold))] focus:ring-2 focus:ring-[hsl(var(--v4v-gold)/0.2)]"
                          )}
                        />
                        <Button
                          type="submit"
                          size="sm"
                          className="absolute right-2 top-1/2 -translate-y-1/2 h-8 px-3 rounded-lg bg-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy-light))] text-white"
                        >
                          Go
                        </Button>
                      </form>
                    </div>

                    {/* Mobile Navigation Links */}
                    <nav className="p-4 space-y-2">
                      <MobileNavLink href="/search" onClick={() => setMobileMenuOpen(false)}>
                        <span className="flex items-center gap-3">
                          <Search className="w-5 h-5" />
                          Search
                          {resourceCount !== null && (
                            <span className="text-sm font-medium text-[hsl(var(--v4v-navy-muted))]">
                              ({resourceCount.toLocaleString()})
                            </span>
                          )}
                        </span>
                      </MobileNavLink>

                      <MobileNavLink href="/saved" onClick={() => setMobileMenuOpen(false)}>
                        <span className="flex items-center gap-3">
                          <Bookmark className={cn(
                            "w-5 h-5",
                            savedCount > 0 && "text-[hsl(var(--v4v-gold))] fill-[hsl(var(--v4v-gold))]"
                          )} />
                          Saved
                          {savedCount > 0 && (
                            <span className="inline-flex items-center justify-center min-w-[1.5rem] h-5 px-1.5 text-xs font-semibold rounded-full bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
                              {savedCount}
                            </span>
                          )}
                        </span>
                      </MobileNavLink>
                    </nav>

                    {/* Sort dropdown for mobile on search page */}
                    {isSearchPage && (
                      <div className="px-6 pb-6">
                        <p className="text-xs font-medium text-[hsl(var(--v4v-navy-muted))] uppercase tracking-wider mb-3">
                          Sort Results
                        </p>
                        <SortDropdownHeader
                          value={currentSort}
                          onChange={(newSort) => {
                            handleSortChange(newSort);
                            setMobileMenuOpen(false);
                          }}
                          hasQuery={!!query}
                          hasZip={!!zip}
                          className="w-full"
                        />
                      </div>
                    )}

                    {/* Bottom accent */}
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[hsl(var(--v4v-gold))] via-[hsl(var(--v4v-gold-light))] to-[hsl(var(--v4v-gold))]" />
                  </SheetContent>
                </Sheet>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Search Dropdown */}
        <div className={cn(
          "md:hidden overflow-hidden transition-all duration-300 ease-out bg-v4v-navy border-b border-white/10",
          searchExpanded ? "max-h-24 opacity-100" : "max-h-0 opacity-0"
        )}>
          <div className="px-4 py-4">
            <form onSubmit={handleSearch} className="relative">
              <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50" />
              <Input
                type="text"
                placeholder="Search veteran resources..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={cn(
                  "h-11 w-full rounded-full pl-11 pr-20",
                  "bg-white/10 border-white/20 text-white placeholder:text-white/40",
                  "focus:bg-white/15 focus:border-[hsl(var(--v4v-gold)/0.5)]",
                  "focus:ring-2 focus:ring-[hsl(var(--v4v-gold)/0.25)]"
                )}
                autoFocus={searchExpanded}
              />
              <Button
                type="submit"
                size="sm"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-7 px-4 rounded-full bg-[hsl(var(--v4v-gold))] hover:bg-[hsl(var(--v4v-gold-light))] text-[hsl(var(--v4v-navy))] font-semibold"
              >
                Search
              </Button>
            </form>
          </div>
        </div>
      </header>

      {/* Spacer for fixed header */}
      <div className={cn(
        "transition-all duration-300",
        searchExpanded ? "h-[calc(4rem+1px+60px+4px)]" : "h-[calc(4rem+4px)]"
      )} />
    </>
  );
}
