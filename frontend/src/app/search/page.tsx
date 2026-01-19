'use client';

import { Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
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
import { ResourceDetailModal } from '@/components/resource-detail-modal';
import {
  FiltersSidebar,
  FixedFiltersSidebar,
  type FilterState,
} from '@/components/filters-sidebar';
import { FilterChips } from '@/components/filter-chips';
import type { SortOption } from '@/components/sort-dropdown';
import api, { type Resource, type MatchExplanation } from '@/lib/api';
import { useResourcesInfinite } from '@/lib/hooks/useResourcesInfinite';
import { useAnalytics } from '@/lib/useAnalytics';
import { Filter, Loader2 } from 'lucide-react';


function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { trackSearch, trackFilter, trackResourceView } = useAnalytics();
  const query = searchParams.get('q') || '';
  const selectedResourceId = searchParams.get('resource');

  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  // Modal state
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [selectedExplanations, setSelectedExplanations] = useState<MatchExplanation[] | undefined>(undefined);
  // Track which resource is animating back to grid (for z-index during exit animation)
  const [animatingResourceId, setAnimatingResourceId] = useState<string | null>(null);

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

  // Get sort from URL params (header controls this now)
  const sortParam = searchParams.get('sort') as SortOption;
  const sort: SortOption = (sortParam && ['relevance', 'newest', 'alpha'].includes(sortParam))
    ? sortParam
    : (query ? 'relevance' : 'newest');

  // Sync filters to URL (preserves existing query and sort params)
  const updateURL = useCallback(
    (newFilters: FilterState) => {
      const params = new URLSearchParams();

      if (query) params.set('q', query);
      if (newFilters.categories.length > 0) {
        params.set('category', newFilters.categories.join(','));
      }
      if (newFilters.states.length > 0) {
        params.set('state', newFilters.states.join(','));
      }
      if (newFilters.scope !== 'all') {
        params.set('scope', newFilters.scope);
      }
      // Preserve sort from URL (header controls this)
      const currentSort = searchParams.get('sort');
      if (currentSort) {
        params.set('sort', currentSort);
      }

      router.push(`/search?${params.toString()}`, { scroll: false });
    },
    [router, query, searchParams]
  );

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    updateURL(newFilters);
    // Track filter usage analytics
    trackFilter(newFilters.categories[0], newFilters.states[0]);
  };

  // Filter chip handlers
  const handleRemoveCategory = (category: string) => {
    const newFilters = {
      ...filters,
      categories: filters.categories.filter((c) => c !== category),
    };
    handleFiltersChange(newFilters);
  };

  const handleRemoveState = (state: string) => {
    const newFilters = {
      ...filters,
      states: filters.states.filter((s) => s !== state),
    };
    handleFiltersChange(newFilters);
  };

  const handleClearScope = () => {
    const newFilters = { ...filters, scope: 'all' };
    handleFiltersChange(newFilters);
  };

  const handleClearAll = () => {
    const newFilters = {
      categories: [],
      states: [],
      scope: 'all',
      minTrust: 0,
    };
    handleFiltersChange(newFilters);
  };

  // Modal handlers with shallow routing
  const openResourceModal = useCallback(
    (resource: Resource, explanations?: MatchExplanation[]) => {
      setSelectedResource(resource);
      setSelectedExplanations(explanations);

      // Track resource view analytics
      trackResourceView(resource.id, resource.categories[0], resource.states[0]);

      // Update URL with shallow routing (no navigation)
      const params = new URLSearchParams(searchParams.toString());
      params.set('resource', resource.id);
      router.push(`/search?${params.toString()}`, { scroll: false });
    },
    [router, searchParams, trackResourceView]
  );

  const closeResourceModal = useCallback(() => {
    // Set animating ID to maintain z-index during exit animation
    const closingId = selectedResource?.id ?? selectedResourceId;
    setAnimatingResourceId(closingId ?? null);
    setSelectedResource(null);
    setSelectedExplanations(undefined);

    // Clear animating state after animation completes (match modal transition duration)
    setTimeout(() => {
      setAnimatingResourceId(null);
    }, 350); // Slightly longer than spring animation

    // Remove resource param from URL
    const params = new URLSearchParams(searchParams.toString());
    params.delete('resource');
    router.push(`/search?${params.toString()}`, { scroll: false });
  }, [router, searchParams, selectedResource, selectedResourceId]);

  // ========== DATA FETCHING ==========
  // Browse mode: useInfiniteQuery with server-side filtering
  const browseQuery = useResourcesInfinite({
    categories: filters.categories,
    states: filters.states,
    scope: filters.scope,
  });

  // Search mode: useQuery (still fetches all for now, search API doesn't support pagination yet)
  const searchQuery = useQuery({
    queryKey: ['search', query, filters],
    queryFn: async () => {
      const results = await api.search.query({
        q: query,
        limit: 500,
      });
      // Track search analytics on new query
      trackSearch(query, filters.categories[0], filters.states[0]);
      return results;
    },
    enabled: !!query,
  });

  // Determine which data source to use
  const isSearchMode = !!query;
  const searchResults = searchQuery.data;

  // Flatten browse pages into single array
  const browseResources = useMemo(() => {
    if (!browseQuery.data?.pages) return [];
    return browseQuery.data.pages.flatMap((page) => page.resources);
  }, [browseQuery.data?.pages]);

  // Get total from first page (server returns filtered total)
  const browseTotal = browseQuery.data?.pages[0]?.total ?? 0;

  // Loading states
  const initialLoading = isSearchMode ? searchQuery.isLoading : browseQuery.isLoading;
  const error = isSearchMode
    ? (searchQuery.error instanceof Error ? searchQuery.error.message : null)
    : (browseQuery.error instanceof Error ? browseQuery.error.message : null);

  // Sync selected resource from URL on mount and when data loads
  useEffect(() => {
    if (
      selectedResourceId &&
      !selectedResource &&
      !initialLoading &&
      // Don't re-select a resource that's currently animating closed
      animatingResourceId !== selectedResourceId
    ) {
      // Find the resource in current results
      const allResources = isSearchMode
        ? (searchResults?.results.map((r) => r.resource) ?? [])
        : browseResources;

      const resource = allResources.find((r) => r.id === selectedResourceId);
      if (resource) {
        const explanations = isSearchMode
          ? searchResults?.results.find((r) => r.resource.id === selectedResourceId)?.explanations
          : undefined;
        setSelectedResource(resource);
        setSelectedExplanations(explanations);
      }
    }
  }, [selectedResourceId, selectedResource, initialLoading, isSearchMode, searchResults, browseResources, animatingResourceId]);

  // Client-side trust filter (server doesn't support minTrust yet)
  const applyTrustFilter = (resources: Resource[]) => {
    if (filters.minTrust <= 0) return resources;
    return resources.filter((resource) => {
      const trustScore =
        resource.trust.freshness_score * resource.trust.reliability_score * 100;
      return trustScore >= filters.minTrust;
    });
  };

  // Client-side filtering for search mode (server doesn't filter search results)
  const filterSearchResults = (resources: Resource[]) => {
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

      return true;
    });
  };

  // Sort results
  const sortResults = <T extends Resource>(resources: T[]) => {
    const sorted = [...resources];
    switch (sort) {
      case 'newest':
        sorted.sort((a, b) => {
          const dateA = new Date(a.created_at || 0).getTime();
          const dateB = new Date(b.created_at || 0).getTime();
          return dateB - dateA;
        });
        break;
      case 'alpha':
        sorted.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'relevance':
      default:
        // Keep original order (API returns by relevance for search)
        break;
    }
    return sorted;
  };

  // Compute final resources list
  const resources = useMemo(() => {
    if (isSearchMode) {
      // Search mode: client-side filtering + sorting + trust filter
      const searchResources = searchResults?.results.map((r) => r.resource) ?? [];
      return sortResults(applyTrustFilter(filterSearchResults(searchResources)));
    } else {
      // Browse mode: server-side filtering already applied, just trust + sort
      return sortResults(applyTrustFilter(browseResources));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSearchMode, searchResults, browseResources, filters, sort]);

  const explanationsMap = useMemo(() => {
    if (!searchResults) return new Map<string, MatchExplanation[]>();
    return new Map(searchResults.results.map((r) => [r.resource.id, r.explanations]));
  }, [searchResults]);

  // For browse mode, use server total; for search mode, use filtered count
  const totalResults = isSearchMode ? resources.length : browseTotal;
  const displayedCount = resources.length;
  const hasResults = displayedCount > 0;

  // Infinite scroll helpers
  const { fetchNextPage, hasNextPage, isFetchingNextPage } = browseQuery;

  return (
    <div className="flex gap-6">
      {/* Fixed Filter Sidebar - Desktop (renders spacer + fixed sidebar) */}
      <FixedFiltersSidebar
        filters={filters}
        onFiltersChange={handleFiltersChange}
        resultCount={totalResults}
      />

      {/* Main Content */}
      <div className="flex min-w-0 flex-1 flex-col space-y-4">
        {/* Results Header with chips and sort */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          {/* Left side: Result count + Filter chips */}
          <div className="flex flex-1 flex-wrap items-center gap-2">
            <span className="shrink-0 text-muted-foreground">
              {initialLoading ? (
                <Skeleton className="inline-block h-4 w-32" />
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
                      Showing <strong>{displayedCount}</strong> of <strong>{totalResults}</strong> resources
                    </>
                  )}
                </>
              )}
            </span>

            {/* Filter chips - next to result count */}
            <FilterChips
              filters={filters}
              onRemoveCategory={handleRemoveCategory}
              onRemoveState={handleRemoveState}
              onClearScope={handleClearScope}
              onClearAll={handleClearAll}
            />
          </div>

          {/* Right side: Mobile Filter Button */}
          <div className="flex shrink-0 items-center gap-2">
            {/* Mobile Filter Button */}
            <Sheet open={mobileFiltersOpen} onOpenChange={setMobileFiltersOpen}>
              <SheetTrigger asChild>
                <Button variant="outline" size="sm" className="lg:hidden">
                  <Filter className="mr-2 h-4 w-4" />
                  Filters
                  {(filters.categories.length > 0 ||
                    filters.states.length > 0 ||
                    filters.scope !== 'all') && (
                    <span className="ml-2 rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
                      {filters.categories.length +
                        filters.states.length +
                        (filters.scope !== 'all' ? 1 : 0)}
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
            <LayoutGroup>
              <AnimatePresence mode="popLayout">
                <div className="grid gap-4 pr-0 sm:grid-cols-2 sm:pr-4 lg:grid-cols-3 xl:grid-cols-4" style={{ isolation: 'isolate' }}>
                  {resources.map((resource, index) => {
                    // Card needs elevated z-index when selected OR when it's the one being animated back during modal close
                    const isCardAnimating = selectedResource?.id === resource.id || animatingResourceId === resource.id;
                    return (
                    <motion.div
                      key={resource.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ delay: index * 0.03, layout: { duration: 0.3 } }}
                      layout
                      style={{ position: 'relative', willChange: 'transform', zIndex: isCardAnimating ? 100 : undefined }}
                      whileHover={{ zIndex: 50, transition: { duration: 0 } }}
                      whileTap={{ zIndex: 50 }}
                      layoutId={`card-wrapper-${resource.id}`}
                    >
                      <ResourceCard
                        resource={resource}
                        explanations={explanationsMap.get(resource.id)}
                        variant="modal"
                        onClick={() =>
                          openResourceModal(resource, explanationsMap.get(resource.id))
                        }
                        enableLayoutId
                      />
                    </motion.div>
                    );
                  })}
                </div>
              </AnimatePresence>

              {/* Load More Button - browse mode only */}
              {!isSearchMode && hasNextPage && (
                <div className="mt-6 flex justify-center">
                  <Button
                    onClick={() => fetchNextPage()}
                    disabled={isFetchingNextPage}
                    variant="outline"
                    size="lg"
                  >
                    {isFetchingNextPage ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      `Load More (${displayedCount} of ${totalResults})`
                    )}
                  </Button>
                </div>
              )}

              {/* Resource Detail Modal */}
              <ResourceDetailModal
                resource={selectedResource}
                explanations={selectedExplanations}
                isOpen={!!selectedResource}
                onClose={closeResourceModal}
              />
            </LayoutGroup>
          ) : (
            <div className="py-12 text-center">
              <p className="text-lg text-muted-foreground">
                No resources found matching your criteria.
              </p>
              <Button
                variant="outline"
                className="mt-4"
                onClick={handleClearAll}
              >
                Clear Filters
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
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
    <main className="grid-background min-h-screen px-4 pb-6 pt-24 sm:px-6 lg:p-8 lg:pt-24">
      <div className="mx-auto max-w-[1600px]">
        <Suspense fallback={<SearchFallback />}>
          <SearchResults />
        </Suspense>
      </div>
    </main>
  );
}
