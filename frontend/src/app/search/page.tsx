'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useIsMobile } from '@/hooks/use-media-query';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
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
import { ResourceDetailPanel } from '@/components/resource-detail-panel';
import api, {
  type SearchResponse,
  type ResourceList,
  type Resource,
  type MatchExplanation,
} from '@/lib/api';
import { Search, SearchX, Filter, X, Briefcase, Home, Scale, GraduationCap, Lightbulb } from 'lucide-react';

interface SelectedResource {
  resource: Resource;
  explanations?: MatchExplanation[];
}

function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q') || '';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [browseResults, setBrowseResults] = useState<ResourceList | null>(null);
  const [selectedResource, setSelectedResource] = useState<SelectedResource | null>(null);
  const [searchInput, setSearchInput] = useState(query);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const isMobile = useIsMobile();

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

  const handleResourceClick = (resource: Resource) => {
    setSelectedResource({
      resource,
      explanations: explanationsMap.get(resource.id),
    });
  };

  const totalResults = resources.length;
  const hasResults = totalResults > 0;

  return (
    <div className="grid h-[calc(100vh-140px)] gap-6 lg:grid-cols-[280px_1fr_400px]">
      {/* Filter Sidebar - Desktop */}
      <Card className="sticky top-6 hidden h-fit max-h-[calc(100vh-160px)] overflow-hidden p-5 lg:block">
        <ScrollArea className="h-full pr-4">
          <FiltersSidebar
            filters={filters}
            onFiltersChange={handleFiltersChange}
            resultCount={totalResults}
          />
        </ScrollArea>
      </Card>

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
                />
              </ScrollArea>
            </SheetContent>
          </Sheet>
        </div>

        {/* Results Header - Desktop */}
        <div className="hidden items-center justify-between lg:flex">
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
          {selectedResource && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedResource(null)}
              className="lg:hidden xl:flex"
            >
              <X className="mr-2 h-4 w-4" />
              Close Preview
            </Button>
          )}
        </div>

        {/* Results Grid */}
        <ScrollArea className="flex-1">
          {loading ? (
            <div className="grid gap-4 pr-4 sm:grid-cols-2">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-48 w-full rounded-lg" />
              ))}
            </div>
          ) : hasResults ? (
            <div className="grid gap-4 pr-4 sm:grid-cols-2">
              {resources.map((resource) => (
                <ResourceCard
                  key={resource.id}
                  resource={resource}
                  explanations={explanationsMap.get(resource.id)}
                  variant="selectable"
                  selected={selectedResource?.resource.id === resource.id}
                  onClick={() => handleResourceClick(resource)}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-[hsl(var(--border))] bg-white p-8 sm:p-12">
              {/* Icon and Heading */}
              <div className="text-center">
                <SearchX className="mx-auto mb-4 h-12 w-12 text-[hsl(var(--muted-foreground))]" />
                <h3 className="font-display text-xl text-[hsl(var(--v4v-navy))]">
                  No resources found
                </h3>
                <p className="mx-auto mt-2 max-w-md text-[hsl(var(--muted-foreground))]">
                  {query
                    ? `We couldn't find any resources matching "${query}" with your current filters.`
                    : "We couldn't find any resources matching your current filters."}
                </p>
              </div>

              {/* Suggestions */}
              <div className="mx-auto mt-6 max-w-md">
                <div className="flex items-start gap-2 rounded-lg bg-[hsl(var(--v4v-gold)/0.1)] p-4">
                  <Lightbulb className="mt-0.5 h-5 w-5 flex-shrink-0 text-[hsl(var(--v4v-gold-dark))]" />
                  <div className="text-sm text-[hsl(var(--v4v-navy))]">
                    <p className="font-medium">Try these suggestions:</p>
                    <ul className="mt-1 list-inside list-disc space-y-1 text-[hsl(var(--muted-foreground))]">
                      {query && <li>Check your spelling or try different keywords</li>}
                      <li>Remove some filters to broaden your search</li>
                      <li>Browse resources by category below</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Quick Links to Hubs */}
              <div className="mt-8">
                <p className="mb-4 text-center text-sm font-medium text-[hsl(var(--muted-foreground))]">
                  Browse by category
                </p>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <Link
                    href="/hubs/employment"
                    className="flex flex-col items-center gap-2 rounded-lg border border-[hsl(var(--border))] p-4 transition-colors hover:border-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.05)]"
                  >
                    <Briefcase className="h-6 w-6 text-[hsl(var(--v4v-navy))]" />
                    <span className="text-sm font-medium text-[hsl(var(--v4v-navy))]">Employment</span>
                  </Link>
                  <Link
                    href="/hubs/housing"
                    className="flex flex-col items-center gap-2 rounded-lg border border-[hsl(var(--border))] p-4 transition-colors hover:border-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.05)]"
                  >
                    <Home className="h-6 w-6 text-[hsl(var(--v4v-navy))]" />
                    <span className="text-sm font-medium text-[hsl(var(--v4v-navy))]">Housing</span>
                  </Link>
                  <Link
                    href="/hubs/legal"
                    className="flex flex-col items-center gap-2 rounded-lg border border-[hsl(var(--border))] p-4 transition-colors hover:border-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.05)]"
                  >
                    <Scale className="h-6 w-6 text-[hsl(var(--v4v-navy))]" />
                    <span className="text-sm font-medium text-[hsl(var(--v4v-navy))]">Legal</span>
                  </Link>
                  <Link
                    href="/hubs/training"
                    className="flex flex-col items-center gap-2 rounded-lg border border-[hsl(var(--border))] p-4 transition-colors hover:border-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.05)]"
                  >
                    <GraduationCap className="h-6 w-6 text-[hsl(var(--v4v-navy))]" />
                    <span className="text-sm font-medium text-[hsl(var(--v4v-navy))]">Training</span>
                  </Link>
                </div>
              </div>

              {/* Clear Filters Button */}
              {(filters.categories.length > 0 ||
                filters.states.length > 0 ||
                filters.scope !== 'all' ||
                filters.minTrust > 0) && (
                <div className="mt-6 text-center">
                  <Button
                    variant="outline"
                    onClick={() =>
                      handleFiltersChange({
                        categories: [],
                        states: [],
                        scope: 'all',
                        minTrust: 0,
                      })
                    }
                  >
                    <X className="mr-2 h-4 w-4" />
                    Clear All Filters
                  </Button>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Detail Panel - Desktop */}
      <Card className="sticky top-6 hidden h-fit max-h-[calc(100vh-160px)] overflow-hidden lg:block">
        <ResourceDetailPanel
          resource={selectedResource?.resource || null}
          explanations={selectedResource?.explanations}
        />
      </Card>

      {/* Detail Panel - Mobile (Sheet) - Only render on mobile */}
      {isMobile && selectedResource && (
        <Sheet
          open={!!selectedResource}
          onOpenChange={(open) => !open && setSelectedResource(null)}
        >
          <SheetContent side="bottom" className="h-[80vh]">
            <SheetHeader className="sr-only">
              <SheetTitle>Resource Details</SheetTitle>
            </SheetHeader>
            <ResourceDetailPanel
              resource={selectedResource.resource}
              explanations={selectedResource.explanations}
              onClose={() => setSelectedResource(null)}
            />
          </SheetContent>
        </Sheet>
      )}
    </div>
  );
}

function SearchFallback() {
  return (
    <div className="grid h-[calc(100vh-140px)] gap-6 lg:grid-cols-[280px_1fr_400px]">
      {/* Filter Sidebar Skeleton */}
      <div className="hidden lg:block">
        <Skeleton className="h-[500px] w-full rounded-lg" />
      </div>

      {/* Main Content Skeleton */}
      <div className="space-y-4">
        <Skeleton className="h-14 w-full rounded-lg" />
        <Skeleton className="h-6 w-48" />
        <div className="grid gap-4 sm:grid-cols-2">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg" />
          ))}
        </div>
      </div>

      {/* Detail Panel Skeleton */}
      <div className="hidden lg:block">
        <Skeleton className="h-[400px] w-full rounded-lg" />
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <main className="min-h-screen p-6 lg:p-8">
      <div className="mx-auto max-w-[1600px]">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <Link href="/">
            <h1 className="text-2xl font-bold">Vibe4Vets</h1>
          </Link>
        </div>

        <Suspense fallback={<SearchFallback />}>
          <SearchResults />
        </Suspense>
      </div>
    </main>
  );
}
