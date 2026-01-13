'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { SearchBar } from '@/components/search-bar';
import { ResourceCard } from '@/components/resource-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import api, { type SearchResponse, type ResourceList } from '@/lib/api';

function SearchResults() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || 'all';
  const state = searchParams.get('state') || 'all';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [browseResults, setBrowseResults] = useState<ResourceList | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        if (query) {
          // Perform search
          const results = await api.search.query({
            q: query,
            category: category !== 'all' ? category : undefined,
            state: state !== 'all' ? state : undefined,
            limit: 20,
          });
          setSearchResults(results);
          setBrowseResults(null);
        } else {
          // Browse mode - list resources with filters
          const results = await api.resources.list({
            category: category !== 'all' ? category : undefined,
            state: state !== 'all' ? state : undefined,
            limit: 20,
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
  }, [query, category, state]);

  const hasResults =
    (searchResults && searchResults.results.length > 0) ||
    (browseResults && browseResults.resources.length > 0);
  const totalResults = searchResults?.total || browseResults?.total || 0;

  return (
    <>
      {/* Search Bar */}
      <div className="mb-8">
        <SearchBar
          initialQuery={query}
          initialCategory={category}
          initialState={state}
        />
      </div>

      {/* Results Header */}
      <div className="mb-4">
        {loading ? (
          <Skeleton className="h-6 w-48" />
        ) : error ? (
          <p className="text-destructive">{error}</p>
        ) : (
          <p className="text-muted-foreground">
            {query ? (
              <>
                Found <strong>{totalResults}</strong> results for &quot;{query}&quot;
              </>
            ) : (
              <>
                Showing <strong>{totalResults}</strong>{' '}
                {category !== 'all' ? `${category} ` : ''}resources
                {state !== 'all' ? ` in ${state}` : ''}
              </>
            )}
          </p>
        )}
      </div>

      {/* Results Grid */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="h-48 w-full rounded-lg" />
            </div>
          ))}
        </div>
      ) : hasResults ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {searchResults
            ? searchResults.results.map((result) => (
                <ResourceCard
                  key={result.resource.id}
                  resource={result.resource}
                  explanations={result.explanations}
                />
              ))
            : browseResults?.resources.map((resource) => (
                <ResourceCard key={resource.id} resource={resource} />
              ))}
        </div>
      ) : (
        <div className="py-12 text-center">
          <p className="text-lg text-muted-foreground">
            No resources found matching your criteria.
          </p>
          <Button asChild className="mt-4">
            <Link href="/">Clear Filters</Link>
          </Button>
        </div>
      )}
    </>
  );
}

function SearchFallback() {
  return (
    <>
      <div className="mb-8">
        <Skeleton className="h-14 w-full rounded-full" />
        <div className="mt-4 flex justify-center gap-4">
          <Skeleton className="h-10 w-[180px]" />
          <Skeleton className="h-10 w-[180px]" />
        </div>
      </div>
      <Skeleton className="mb-4 h-6 w-48" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full rounded-lg" />
        ))}
      </div>
    </>
  );
}

export default function SearchPage() {
  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
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
