'use client';

import {
  Suspense,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
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
import { ResourceDetailModal } from '@/components/resource-detail-modal';
import { VirtualizedResourceGrid } from '@/components/virtualized-resource-grid';
import { ProgramCard } from '@/components/ProgramCard';
import { ResourceCard } from '@/components/resource-card';
import {
  FiltersSidebar,
  FixedFiltersSidebar,
  type FilterState,
} from '@/components/filters-sidebar';
import { FilterChips } from '@/components/filter-chips';
import type { SortOption } from '@/components/sort-dropdown';
import api, { type Resource, type MatchExplanation, type Program } from '@/lib/api';
import { useOptionalFilterContext } from '@/context/filter-context';

// Helper type for grouped display
interface ProgramGroup {
  type: 'program';
  program: Program;
  resources: Resource[];
}

interface StandaloneResource {
  type: 'standalone';
  resource: Resource;
}

type DisplayItem = ProgramGroup | StandaloneResource;

// Group resources by program_id for hierarchical display
function groupResourcesByProgram(resources: Resource[]): DisplayItem[] {
  const programMap = new Map<string, { program: Program; resources: Resource[] }>();
  const standalone: Resource[] = [];

  for (const resource of resources) {
    if (resource.program_id && resource.program) {
      const existing = programMap.get(resource.program_id);
      if (existing) {
        existing.resources.push(resource);
      } else {
        programMap.set(resource.program_id, {
          program: resource.program,
          resources: [resource],
        });
      }
    } else {
      standalone.push(resource);
    }
  }

  const items: DisplayItem[] = [];

  // Add program groups (only if they have 2+ resources to make grouping worthwhile)
  for (const [, group] of programMap) {
    if (group.resources.length >= 2) {
      items.push({
        type: 'program',
        program: group.program,
        resources: group.resources,
      });
    } else {
      // Single-resource programs render as standalone
      standalone.push(...group.resources);
    }
  }

  // Add standalone resources
  for (const resource of standalone) {
    items.push({ type: 'standalone', resource });
  }

  return items;
}
import { useResourcesInfinite } from '@/lib/hooks/useResourcesInfinite';
import { useAnalytics } from '@/lib/useAnalytics';
import { useIsMobile } from '@/hooks/use-media-query';
import { useReducedMotion } from '@/hooks/use-reduced-motion';
import { Filter, Loader2 } from 'lucide-react';
import { BackToTop } from '@/components/BackToTop';


function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { trackSearch, trackFilter, trackResourceView } = useAnalytics();
  const query = searchParams.get('q') || '';
  const selectedResourceId = searchParams.get('resource');

  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const isMobile = useIsMobile();
  const prefersReducedMotion = useReducedMotion();

  // Sidebar collapsed state from context (allows header to open sidebar)
  const filterContext = useOptionalFilterContext();
  const sidebarCollapsed = filterContext?.sidebarCollapsed ?? true;
  const setSidebarCollapsed = filterContext?.setSidebarCollapsed ?? (() => {});

  // Modal state
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [selectedExplanations, setSelectedExplanations] = useState<MatchExplanation[] | undefined>(undefined);
  // Track which resource is animating back to grid (for z-index during exit animation)
  const [animatingResourceId, setAnimatingResourceId] = useState<string | null>(null);

  // Initialize filters from URL params
  // Supports both formats: state=VA,NC (comma-separated) and state=VA&state=NC (multiple params)
  const [filters, setFilters] = useState<FilterState>(() => {
    // Get all 'category' params (handles both ?category=a&category=b and ?category=a,b)
    const categoryParams = searchParams.getAll('category');
    const categories = categoryParams.length > 0
      ? categoryParams.flatMap((p) => p.split(','))
      : [];

    // Get all 'state' params (handles both ?state=VA&state=NC and ?state=VA,NC)
    const stateParams = searchParams.getAll('state');
    const states = stateParams.length > 0
      ? stateParams.flatMap((p) => p.split(','))
      : [];

    const scopeParam = searchParams.get('scope');
    const minTrustParam = searchParams.get('minTrust');
    const zipParam = searchParams.get('zip');
    const radiusParam = searchParams.get('radius');

    return {
      categories,
      states,
      scope: scopeParam || 'all',
      minTrust: minTrustParam ? parseInt(minTrustParam, 10) : 0,
      zip: zipParam || undefined,
      radius: radiusParam ? parseInt(radiusParam, 10) : undefined,
    };
  });

  // Get sort from URL params (header controls this now)
  const sortParam = searchParams.get('sort') as SortOption;
  const getDefaultSort = (): SortOption => {
    if (query) return 'relevance';
    if (filters.zip) return 'distance';
    return 'newest';
  };
  const sort: SortOption = (sortParam && ['relevance', 'newest', 'alpha', 'shuffle', 'distance'].includes(sortParam))
    ? sortParam
    : getDefaultSort();

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
      // Zip code location filter
      if (newFilters.zip) {
        params.set('zip', newFilters.zip);
        if (newFilters.radius && newFilters.radius !== 25) {
          params.set('radius', String(newFilters.radius));
        }
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

  const handleClearZip = () => {
    const newFilters = { ...filters, zip: undefined, radius: undefined };
    handleFiltersChange(newFilters);
  };

  const handleClearAll = () => {
    const newFilters = {
      categories: [],
      states: [],
      scope: 'all',
      minTrust: 0,
      zip: undefined,
      radius: undefined,
    };
    handleFiltersChange(newFilters);
  };

  // Modal handlers with shallow routing
  const openResourceModal = useCallback(
    (resource: Resource, explanations?: MatchExplanation[]) => {
      // Track resource view analytics
      trackResourceView(resource.id, resource.categories[0], resource.states[0]);

      // For reduced motion users, navigate to full page instead of modal
      if (prefersReducedMotion) {
        const from = searchParams.toString();
        router.push(`/resources/${resource.id}${from ? `?from=${encodeURIComponent(from)}` : ''}`);
        return;
      }

      setSelectedResource(resource);
      setSelectedExplanations(explanations);

      // Update URL with shallow routing (no navigation)
      const params = new URLSearchParams(searchParams.toString());
      params.set('resource', resource.id);
      router.push(`/search?${params.toString()}`, { scroll: false });
    },
    [router, searchParams, trackResourceView, prefersReducedMotion]
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

  // Nearby mode: useQuery when zip code is active (no text search)
  const nearbyQuery = useQuery({
    queryKey: ['nearby', filters.zip, filters.radius, filters.categories, filters.scope],
    queryFn: async () => {
      return api.resources.nearby({
        zip: filters.zip!,
        radius: filters.radius || 25,
        categories: filters.categories.length > 0 ? filters.categories.join(',') : undefined,
        scope: filters.scope !== 'all' ? filters.scope : undefined,
        limit: 100,
      });
    },
    enabled: !!filters.zip && !query,
  });

  // Determine which data source to use
  const isSearchMode = !!query;
  const isNearbyMode = !!filters.zip && !query;
  const searchResults = searchQuery.data;
  const nearbyResults = nearbyQuery.data;

  // Flatten browse pages into single array
  const browseResources = useMemo(() => {
    if (!browseQuery.data?.pages) return [];
    return browseQuery.data.pages.flatMap((page) => page.resources);
  }, [browseQuery.data?.pages]);

  // Get total from first page (server returns filtered total)
  const browseTotal = browseQuery.data?.pages[0]?.total ?? 0;

  // Track previously rendered resource IDs to only animate new items
  const previousResourceIdsRef = useRef<Set<string>>(new Set());
  const currentBrowseResourceIds = useMemo(
    () => new Set(browseResources.map((r) => r.id)),
    [browseResources]
  );
  const newResourceIds = useMemo(() => {
    const newIds = new Set<string>();
    currentBrowseResourceIds.forEach((id) => {
      if (!previousResourceIdsRef.current.has(id)) newIds.add(id);
    });
    return newIds;
  }, [currentBrowseResourceIds]);
  const newResourceIndexById = useMemo(() => {
    const indexById = new Map<string, number>();
    let index = 0;
    newResourceIds.forEach((id) => {
      indexById.set(id, index++);
    });
    return indexById;
  }, [newResourceIds]);
  useEffect(() => {
    previousResourceIdsRef.current = currentBrowseResourceIds;
  }, [currentBrowseResourceIds]);

  // Distance map for nearby results
  const distanceMap = useMemo(() => {
    if (!nearbyResults?.resources) return new Map<string, number>();
    return new Map(
      nearbyResults.resources.map((r) => [r.resource.id, r.distance_miles])
    );
  }, [nearbyResults]);

  // Extract resources from nearby results
  const nearbyResources = useMemo(() => {
    if (!nearbyResults?.resources) return [];
    return nearbyResults.resources.map((r) => r.resource);
  }, [nearbyResults]);

  // Loading states
  const initialLoading = isSearchMode
    ? searchQuery.isLoading
    : isNearbyMode
      ? nearbyQuery.isLoading
      : browseQuery.isLoading;
  const error = isSearchMode
    ? (searchQuery.error instanceof Error ? searchQuery.error.message : null)
    : isNearbyMode
      ? (nearbyQuery.error instanceof Error ? nearbyQuery.error.message : null)
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
  const sortResults = <T extends Resource>(resources: T[], distMap?: Map<string, number>) => {
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
      case 'distance':
        // Sort by distance if we have distance data
        if (distMap && distMap.size > 0) {
          sorted.sort((a, b) => {
            const distA = distMap.get(a.id) ?? Infinity;
            const distB = distMap.get(b.id) ?? Infinity;
            return distA - distB;
          });
        }
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
    } else if (isNearbyMode) {
      // Nearby mode: apply trust filter, then sort
      // If sort is 'distance', API already sorted - keep order
      // Otherwise, apply the requested sort (alpha, newest, etc.)
      const filtered = applyTrustFilter(nearbyResources);
      if (sort === 'distance') {
        return filtered; // Already sorted by distance from API
      }
      return sortResults(filtered, distanceMap);
    } else {
      // Browse mode: server-side filtering already applied, just trust + sort
      return sortResults(applyTrustFilter(browseResources));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSearchMode, isNearbyMode, searchResults, nearbyResources, browseResources, filters, sort, distanceMap]);

  const explanationsMap = useMemo(() => {
    if (!searchResults) return new Map<string, MatchExplanation[]>();
    return new Map(searchResults.results.map((r) => [r.resource.id, r.explanations]));
  }, [searchResults]);

  // Group resources by program for hierarchical display
  const groupedItems = useMemo(() => {
    return groupResourcesByProgram(resources);
  }, [resources]);

  // Check if we have any program groups (to decide whether to use grouped vs flat view)
  const hasProgramGroups = groupedItems.some((item) => item.type === 'program');

  // For browse mode, use server total; for search mode, use filtered count
  const totalResults = isSearchMode
    ? resources.length
    : isNearbyMode
      ? (nearbyResults?.total ?? 0)
      : browseTotal;
  const displayedCount = resources.length;
  const hasResults = displayedCount > 0;

  // Infinite scroll helpers
  const { fetchNextPage, hasNextPage, isFetchingNextPage } = browseQuery;
  const restoreScrollYRef = useRef<number | null>(null);
  const loadMoreSentinelRef = useRef<HTMLDivElement | null>(null);
  const disableGridMotionRef = useRef(false);
  const [disableGridMotion, setDisableGridMotion] = useState(false);

  const handleLoadMore = useCallback(async () => {
    restoreScrollYRef.current = window.scrollY;
    disableGridMotionRef.current = true;
    setDisableGridMotion(true);
    await fetchNextPage();
  }, [fetchNextPage]);

  // Restore scroll after the DOM commits the newly appended items.
  useLayoutEffect(() => {
    const restoreY = restoreScrollYRef.current;
    if (restoreY === null) return;
    if (isFetchingNextPage) return;

    requestAnimationFrame(() => {
      const currentY = window.scrollY;
      if (Math.abs(currentY - restoreY) > 10) {
        window.scrollTo({ top: restoreY });
      }
      restoreScrollYRef.current = null;
    });
  }, [isFetchingNextPage]);

  // Turn animations back on shortly after pagination settles.
  useEffect(() => {
    if (isFetchingNextPage) return;
    if (!disableGridMotionRef.current) return;

    const t = window.setTimeout(() => {
      disableGridMotionRef.current = false;
      setDisableGridMotion(false);
    }, 150);

    return () => window.clearTimeout(t);
  }, [isFetchingNextPage]);

  // Background prefetch: load the next page when the user is near the bottom.
  // Desktop only - on mobile, use the explicit "Load more" button.
  useEffect(() => {
    if (isSearchMode) return;
    if (isMobile) return; // On mobile, use button instead of auto-fetch
    if (!hasNextPage) return;
    if (isFetchingNextPage) return;

    const el = loadMoreSentinelRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const isIntersecting = entries.some((entry) => entry.isIntersecting);
        if (!isIntersecting) return;
        if (!hasNextPage) return;
        if (isFetchingNextPage) return;
        restoreScrollYRef.current = window.scrollY;
        disableGridMotionRef.current = true;
        setDisableGridMotion(true);
        fetchNextPage();
      },
      { root: null, rootMargin: '1200px 0px', threshold: 0 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetchingNextPage, isMobile, isSearchMode]);

  // Track sidebar expanded state for transform (desktop only)
  const sidebarExpanded = !sidebarCollapsed && !isMobile;

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="flex gap-6">
        {/* Fixed Filter Sidebar - Desktop (renders spacer + fixed sidebar) */}
        <FixedFiltersSidebar
          filters={filters}
          onFiltersChange={handleFiltersChange}
          resultCount={totalResults}
          isCollapsed={sidebarCollapsed}
          onCollapsedChange={setSidebarCollapsed}
        />

        {/* Main Content - shifts right when sidebar expands (GPU-accelerated) */}
        <div
          className="flex min-w-0 flex-1 flex-col space-y-4 transition-transform duration-200 ease-out"
          style={{
            transform: sidebarExpanded ? 'translateX(232px)' : undefined,
            paddingRight: sidebarExpanded ? 200 : undefined,  // Slightly less than transform to keep cards wider
          }}
        >
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
                  ) : isNearbyMode ? (
                    <>
                      <strong>{displayedCount}</strong> resources within <strong>{filters.radius || 25}</strong> miles of <strong>{filters.zip}</strong>
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
              onClearZip={handleClearZip}
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
            <>
              {/* Grouped View (when program groups exist) or Virtualized Grid */}
              {hasProgramGroups ? (
                <div className="space-y-4">
                  {groupedItems.map((item) => {
                    if (item.type === 'program') {
                      return (
                        <ProgramCard
                          key={item.program.id}
                          program={item.program}
                          resources={item.resources}
                          explanationsMap={explanationsMap}
                          distanceMap={isNearbyMode ? distanceMap : undefined}
                          onResourceClick={openResourceModal}
                        />
                      );
                    } else {
                      return (
                        <ResourceCard
                          key={item.resource.id}
                          resource={item.resource}
                          explanations={explanationsMap.get(item.resource.id)}
                          variant="modal"
                          onClick={() =>
                            openResourceModal(
                              item.resource,
                              explanationsMap.get(item.resource.id)
                            )
                          }
                          distance={isNearbyMode ? distanceMap.get(item.resource.id) : undefined}
                          enableLayoutId={true}
                        />
                      );
                    }
                  })}
                </div>
              ) : (
                /* Virtualized Grid (flat view for ungrouped resources) */
                <VirtualizedResourceGrid
                  resources={resources}
                  explanationsMap={explanationsMap}
                  selectedResourceId={selectedResource?.id}
                  animatingResourceId={animatingResourceId}
                  onResourceClick={openResourceModal}
                  hasNextPage={!isSearchMode && !isNearbyMode && hasNextPage}
                  isFetchingNextPage={isFetchingNextPage}
                  fetchNextPage={handleLoadMore}
                  disableAnimation={disableGridMotion}
                  newResourceIds={newResourceIds}
                  newResourceIndexById={newResourceIndexById}
                  distanceMap={isNearbyMode ? distanceMap : undefined}
                  enableLayoutId={true}
                />
              )}

              {/* Load More Button - mobile only (desktop uses auto-fetch) */}
              {!isSearchMode && hasNextPage && isMobile && (
                <div className="mt-6 flex justify-center">
                  <Button
                    onClick={handleLoadMore}
                    disabled={isFetchingNextPage}
                    className="w-full"
                    size="lg"
                  >
                    {isFetchingNextPage ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      `Load More (${totalResults - displayedCount} remaining)`
                    )}
                  </Button>
                </div>
              )}

              {/* Loading indicator for desktop auto-fetch */}
              {!isSearchMode && isFetchingNextPage && !isMobile && (
                <div className="mt-6 flex justify-center">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              )}

              {!isSearchMode && hasNextPage && <div ref={loadMoreSentinelRef} className="h-px w-full" />}
            </>
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

    {/* Resource Detail Modal - outside transformed container to avoid stacking context issues */}
    <ResourceDetailModal
      resource={selectedResource}
      explanations={selectedExplanations}
      isOpen={!!selectedResource}
      onClose={closeResourceModal}
      enableLayoutId={true}
    />
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
    <main className="grid-background min-h-screen pb-6 pt-24">
      <Suspense fallback={<div className="mx-auto max-w-[1600px] px-4 sm:px-6 lg:px-8"><SearchFallback /></div>}>
        <SearchResults />
      </Suspense>

      {/* Back to top button */}
      <BackToTop />
    </main>
  );
}
