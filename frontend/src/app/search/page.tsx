'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { ResourceCard } from '@/components/resource-card';
import {
  FiltersSidebar,
  type FilterState,
} from '@/components/filters-sidebar';
import api, { type SearchResponse, type ResourceList, type Resource } from '@/lib/api';
import {
  Search,
  Filter,
  ChevronRight,
  PanelLeftClose,
} from 'lucide-react';


function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q') || '';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [browseResults, setBrowseResults] = useState<ResourceList | null>(null);
  const [searchInput, setSearchInput] = useState(query);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  // Sidebar collapse state with localStorage persistence
  const [leftCollapsed, setLeftCollapsed] = useState(false);

  // Load collapsed state from localStorage on mount
  useEffect(() => {
    const savedLeft = localStorage.getItem('v4v-left-collapsed');
    if (savedLeft !== null) setLeftCollapsed(savedLeft === 'true');
  }, []);

  // Persist collapsed state to localStorage
  const toggleLeftCollapsed = () => {
    const newValue = !leftCollapsed;
    setLeftCollapsed(newValue);
    localStorage.setItem('v4v-left-collapsed', String(newValue));
  };

  // Initialize filters from URL params
  const [filters, setFilters] = useState<FilterState>(() => {
    const categoryParam = searchParams.get('category');
    const stateParam = searchParams.get('state');
    const scopeParam = searchParams.get('scope');
    const minTrustParam = searchParams.get('minTrust');

    return {
      categories: categoryParam ? categoryParam.split(',') : [],
      states: stateParam ? stateParam.split(',') : [],
      scope: scopeParam || 'all',
      minTrust: minTrustParam ? parseInt(minTrustParam, 10) : 0,
    };
  });

  // Sync filters to URL
  const updateURL = useCallback(
    (newFilters: FilterState, newQuery?: string) => {
      const params = new URLSearchParams();

      const q = newQuery ?? searchInput;
      if (q) params.set('q', q);
      if (newFilters.categories.length > 0) {
        params.set('category', newFilters.categories.join(','));
      }
      if (newFilters.states.length > 0) {
        params.set('state', newFilters.states.join(','));
      }
      if (newFilters.scope !== 'all') {
        params.set('scope', newFilters.scope);
      }
      if (newFilters.minTrust > 0) {
        params.set('minTrust', String(newFilters.minTrust));
      }

      router.push(`/search?${params.toString()}`, { scroll: false });
    },
    [router, searchInput]
  );

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    updateURL(newFilters);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateURL(filters, searchInput);
  };

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        // Build API params from filters
        const category = filters.categories.length === 1 ? filters.categories[0] : undefined;
        const state = filters.states.length === 1 ? filters.states[0] : undefined;

        if (query) {
          const results = await api.search.query({
            q: query,
            category,
            state,
            limit: 50,
          });
          setSearchResults(results);
          setBrowseResults(null);
        } else {
          const results = await api.resources.list({
            category,
            state,
            limit: 50,
          });
          setBrowseResults(results);
          setSearchResults(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resources');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [query, filters.categories, filters.states]);

  // Filter results client-side for multi-select and trust
  const filterResults = <T extends Resource>(resources: T[]) => {
    return resources.filter((resource) => {
      // Category filter (if multiple selected)
      if (filters.categories.length > 1) {
        const hasCategory = resource.categories.some((c) =>
          filters.categories.includes(c)
        );
        if (!hasCategory) return false;
      }

      // State filter (if multiple selected)
      if (filters.states.length > 1) {
        const matchesState =
          resource.scope === 'national' ||
          resource.states.some((s) => filters.states.includes(s));
        if (!matchesState) return false;
      }

      // Scope filter
      if (filters.scope !== 'all') {
        if (filters.scope === 'national' && resource.scope !== 'national') return false;
        if (filters.scope === 'state' && resource.scope === 'national') return false;
      }

      // Trust filter
      if (filters.minTrust > 0) {
        const trustScore =
          resource.trust.freshness_score * resource.trust.reliability_score * 100;
        if (trustScore < filters.minTrust) return false;
      }

      return true;
    });
  };

  const resources = searchResults
    ? filterResults(searchResults.results.map((r) => r.resource))
    : filterResults(browseResults?.resources || []);

  const explanationsMap = searchResults
    ? new Map(searchResults.results.map((r) => [r.resource.id, r.explanations]))
    : new Map();

  const totalResults = resources.length;
  const hasResults = totalResults > 0;

  return (
    <div
      className="relative grid h-[calc(100vh-140px)] gap-6 transition-all duration-300 ease-in-out lg:grid-cols-[280px_1fr]"
      style={{
        gridTemplateColumns: `${leftCollapsed ? '0px' : '280px'} 1fr`,
      }}
    >
      {/* Collapsed Left Edge Button */}
      {leftCollapsed && (
        <button
          onClick={toggleLeftCollapsed}
          className="fixed left-2 top-1/2 z-30 hidden -translate-y-1/2 rounded-r-lg border border-l-0 bg-background p-2 shadow-md transition-colors hover:bg-muted lg:block"
          aria-label="Show filters"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      )}

      {/* Filter Sidebar - Desktop */}
      <div
        className={`sticky top-6 hidden h-fit max-h-[calc(100vh-160px)] overflow-hidden transition-all duration-300 ease-in-out lg:block ${
          leftCollapsed ? 'w-0 opacity-0' : 'w-[280px] opacity-100'
        }`}
      >
        <Card className="h-full overflow-hidden">
          {/* Clickable Header */}
          <button
            onClick={toggleLeftCollapsed}
            className="flex w-full items-center justify-between border-b px-5 py-3 text-left transition-colors hover:bg-muted/50"
            aria-label="Collapse filters"
          >
            <span className="flex items-center gap-2 text-sm font-semibold">
              <Filter className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
              Filters
            </span>
            <PanelLeftClose className="h-4 w-4 text-muted-foreground" />
          </button>
          <ScrollArea className="h-[calc(100%-52px)] p-5 pr-4">
            <FiltersSidebar
              filters={filters}
              onFiltersChange={handleFiltersChange}
              resultCount={totalResults}
              hideHeader
            />
          </ScrollArea>
        </Card>
      </div>

      {/* Main Content */}
      <div className="flex flex-col space-y-4">
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="relative">
          <div className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2">
            <Search className="h-5 w-5 text-muted-foreground" />
          </div>
          <Input
            type="text"
            placeholder="Search for resources..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="search-glow w-full rounded-lg py-6 pl-12 pr-28 text-base shadow-sm"
          />
          <Button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md px-5 font-semibold"
          >
            Search
          </Button>
        </form>

        {/* Mobile Filter Button */}
        <div className="flex items-center justify-between lg:hidden">
          <span className="text-sm text-muted-foreground">
            {loading ? (
              <Skeleton className="inline-block h-4 w-24" />
            ) : (
              <>
                <strong>{totalResults}</strong> results
              </>
            )}
          </span>
          <Sheet open={mobileFiltersOpen} onOpenChange={setMobileFiltersOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="mr-2 h-4 w-4" />
                Filters
                {(filters.categories.length > 0 ||
                  filters.states.length > 0 ||
                  filters.scope !== 'all' ||
                  filters.minTrust > 0) && (
                  <span className="ml-2 rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
                    {filters.categories.length +
                      filters.states.length +
                      (filters.scope !== 'all' ? 1 : 0) +
                      (filters.minTrust > 0 ? 1 : 0)}
                  </span>
                )}
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <SheetHeader>
                <SheetTitle>Filters</SheetTitle>
              </SheetHeader>
              <ScrollArea className="mt-6 h-[calc(100vh-100px)]">
                <FiltersSidebar
                  filters={filters}
                  onFiltersChange={(newFilters) => {
                    handleFiltersChange(newFilters);
                    setMobileFiltersOpen(false);
                  }}
                  resultCount={totalResults}
                  hideHeader
                />
              </ScrollArea>
            </SheetContent>
          </Sheet>
        </div>

        {/* Results Header - Desktop */}
        <div className="hidden items-center lg:flex">
          <span className="text-muted-foreground">
            {loading ? (
              <Skeleton className="inline-block h-4 w-48" />
            ) : error ? (
              <span className="text-destructive">{error}</span>
            ) : (
              <>
                {query ? (
                  <>
                    Found <strong>{totalResults}</strong> results for &quot;{query}&quot;
                  </>
                ) : (
                  <>
                    Showing <strong>{totalResults}</strong> resources
                  </>
                )}
              </>
            )}
          </span>
        </div>

        {/* Results Grid */}
        <ScrollArea className="flex-1">
          {loading ? (
            <div className="grid gap-4 pr-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => (
                <Skeleton key={i} className="h-48 w-full rounded-lg" />
              ))}
            </div>
          ) : hasResults ? (
            <div className="grid gap-4 pr-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {resources.map((resource) => (
                <ResourceCard
                  key={resource.id}
                  resource={resource}
                  explanations={explanationsMap.get(resource.id)}
                  variant="link"
                  searchParams={searchParams.toString()}
                />
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <p className="text-lg text-muted-foreground">
                No resources found matching your criteria.
              </p>
              <Button
                variant="outline"
                className="mt-4"
                onClick={() =>
                  handleFiltersChange({
                    categories: [],
                    states: [],
                    scope: 'all',
                    minTrust: 0,
                  })
                }
              >
                Clear Filters
              </Button>
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
}

function SearchFallback() {
  return (
    <div className="grid h-[calc(100vh-140px)] gap-6 lg:grid-cols-[280px_1fr]">
      {/* Filter Sidebar Skeleton */}
      <div className="hidden lg:block">
        <Skeleton className="h-[500px] w-full rounded-lg" />
      </div>

      {/* Main Content Skeleton */}
      <div className="space-y-4">
        <Skeleton className="h-14 w-full rounded-lg" />
        <Skeleton className="h-6 w-48" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg" />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <main className="min-h-screen p-6 pt-24 lg:p-8 lg:pt-24">
      <div className="mx-auto max-w-[1600px]">
        <Suspense fallback={<SearchFallback />}>
          <SearchResults />
        </Suspense>
      </div>
    </main>
  );
}
