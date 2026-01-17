'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
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
  FixedFiltersSidebar,
  type FilterState,
} from '@/components/filters-sidebar';
import api, { type SearchResponse, type ResourceList, type Resource } from '@/lib/api';
import { Search, Filter } from 'lucide-react';


function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q') || '';

  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [browseResults, setBrowseResults] = useState<ResourceList | null>(null);
  const [lastQuery, setLastQuery] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState(query);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

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

  // Only refetch when query changes, not on filter changes
  // Filters are applied client-side to already-fetched data
  useEffect(() => {
    async function fetchData() {
      // Only show loading skeleton on initial load or query change
      const isQueryChange = query !== lastQuery;
      if (isQueryChange || initialLoading) {
        setInitialLoading(true);
      }
      setError(null);

      try {
        if (query) {
          const results = await api.search.query({
            q: query,
            limit: 50,
          });
          setSearchResults(results);
          setBrowseResults(null);
        } else {
          const results = await api.resources.list({
            limit: 50,
          });
          setBrowseResults(results);
          setSearchResults(null);
        }
        setLastQuery(query);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resources');
      } finally {
        setInitialLoading(false);
      }
    }

    fetchData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]); // Only refetch on query change, filters applied client-side

  // Filter results client-side for multi-select and trust
  const filterResults = <T extends Resource>(resources: T[]) => {
    return resources.filter((resource) => {
      // Category filter
      if (filters.categories.length > 0) {
        const hasCategory = resource.categories.some((c) =>
          filters.categories.includes(c)
        );
        if (!hasCategory) return false;
      }

      // State filter (includes national resources)
      if (filters.states.length > 0) {
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
    <>
      {/* Fixed Filter Sidebar - Desktop */}
      <FixedFiltersSidebar
        filters={filters}
        onFiltersChange={handleFiltersChange}
        resultCount={totalResults}
      />

      {/* Main Content */}
      <div className="flex flex-col space-y-4">
        {/* Sticky Search + Filters Bar (Mobile) */}
        <div className="sticky top-16 z-20 -mx-4 space-y-3 bg-background/95 px-4 pb-3 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-background/80 lg:static lg:z-auto lg:-mx-0 lg:space-y-4 lg:bg-transparent lg:px-0 lg:pb-0 lg:shadow-none lg:backdrop-blur-none">
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
              {initialLoading ? (
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
              <SheetContent side="left" className="w-[90vw] max-w-[20rem]">
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
        </div>

        {/* Results Header - Desktop */}
        <div className="hidden items-center lg:flex">
          <span className="text-muted-foreground">
            {initialLoading ? (
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
        <div>
          {initialLoading ? (
            <div className="grid gap-4 pr-0 sm:grid-cols-2 sm:pr-4 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => (
                <Card key={i} className="h-48 w-full animate-pulse overflow-hidden">
                  <div className="flex h-full flex-col p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <Skeleton className="h-4 w-16 rounded" />
                      <Skeleton className="h-5 w-5 rounded-full" />
                    </div>
                    <Skeleton className="mb-2 h-5 w-3/4 rounded" />
                    <Skeleton className="mb-4 h-4 w-full rounded" />
                    <Skeleton className="h-4 w-2/3 rounded" />
                    <div className="mt-auto flex gap-2">
                      <Skeleton className="h-6 w-20 rounded-full" />
                      <Skeleton className="h-6 w-16 rounded-full" />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : hasResults ? (
            <AnimatePresence mode="popLayout">
              <div className="grid gap-4 pr-0 sm:grid-cols-2 sm:pr-4 lg:grid-cols-3 xl:grid-cols-4">
                {resources.map((resource, index) => (
                  <motion.div
                    key={resource.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: index * 0.03 }}
                    layout
                  >
                    <ResourceCard
                      resource={resource}
                      explanations={explanationsMap.get(resource.id)}
                      variant="link"
                      searchParams={searchParams.toString()}
                    />
                  </motion.div>
                ))}
              </div>
            </AnimatePresence>
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
        </div>
      </div>
    </>
  );
}

function SearchFallback() {
  return (
    <div className="flex flex-col space-y-4">
      {/* Search Bar Skeleton */}
      <Skeleton className="h-14 w-full rounded-lg" />
      <Skeleton className="h-6 w-48" />

      {/* Results Grid Skeleton */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {[...Array(8)].map((_, i) => (
          <Card key={i} className="h-48 w-full animate-pulse overflow-hidden">
            <div className="flex h-full flex-col p-4">
              <div className="mb-2 flex items-center justify-between">
                <Skeleton className="h-4 w-16 rounded" />
                <Skeleton className="h-5 w-5 rounded-full" />
              </div>
              <Skeleton className="mb-2 h-5 w-3/4 rounded" />
              <Skeleton className="mb-4 h-4 w-full rounded" />
              <Skeleton className="h-4 w-2/3 rounded" />
              <div className="mt-auto flex gap-2">
                <Skeleton className="h-6 w-20 rounded-full" />
                <Skeleton className="h-6 w-16 rounded-full" />
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <main className="min-h-screen px-4 pb-6 pt-24 sm:px-6 lg:p-8 lg:pt-24">
      <div className="mx-auto max-w-[1600px]">
        <Suspense fallback={<SearchFallback />}>
          <SearchResults />
        </Suspense>
      </div>
    </main>
  );
}
