'use client';

import { useEffect, useState } from 'react';
import { useQueries } from '@tanstack/react-query';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { ResourceCard } from '@/components/resource-card';
import { ExportDropdown } from '@/components/export-dropdown';
import { useSavedResources } from '@/context/saved-resources-context';
import api, { type Resource } from '@/lib/api';
import { Bookmark, Trash2, ArrowLeft, AlertCircle, Info } from 'lucide-react';

export default function SavedPage() {
  const { savedIds, clearAll, isHydrated, count } = useSavedResources();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Fetch full resource data for each saved ID
  const resourceQueries = useQueries({
    queries: savedIds.map((id) => ({
      queryKey: ['resource', id],
      queryFn: () => api.resources.get(id),
      enabled: isHydrated && mounted,
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    })),
  });

  // Extract successfully loaded resources
  const resources: Resource[] = resourceQueries
    .filter((query) => query.isSuccess && query.data)
    .map((query) => query.data as Resource);

  const isLoading = !isHydrated || !mounted || resourceQueries.some((q) => q.isLoading);
  const hasResources = resources.length > 0;

  // Show loading skeleton during hydration
  if (!mounted || !isHydrated) {
    return (
      <main className="grid-background min-h-screen px-4 pb-6 pt-24 sm:px-6 lg:p-8 lg:pt-24">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8">
            <Skeleton className="mb-2 h-8 w-64" />
            <Skeleton className="h-5 w-96" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="h-48 w-full animate-pulse" />
            ))}
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="grid-background min-h-screen px-4 pb-6 pt-24 sm:px-6 lg:p-8 lg:pt-24">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <Link
                  href="/search"
                  className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Search
                </Link>
              </div>
              <h1 className="font-display flex items-center gap-3 text-3xl font-bold text-[hsl(var(--v4v-navy))] dark:text-foreground">
                <Bookmark className="h-8 w-8 text-[hsl(var(--v4v-gold))] fill-[hsl(var(--v4v-gold))]" />
                My Saved Resources
              </h1>
              <p className="mt-2 text-muted-foreground">
                {count === 0
                  ? 'No resources saved yet'
                  : `${count} resource${count !== 1 ? 's' : ''} saved to this device`}
              </p>
            </div>

            {/* Actions */}
            {hasResources && (
              <div className="flex flex-wrap items-center gap-2">
                <ExportDropdown resources={resources} />

                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Clear All
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Clear all saved resources?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will remove all {count} saved resources from this device. This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={clearAll} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                        Clear All
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            )}
          </div>

          {/* Device storage notice */}
          <div className="mt-4 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            <p>
              Saved resources are stored only on this device. Clear your browser data and they&apos;ll be removed.
              Use the export options above to keep a copy.
            </p>
          </div>
        </div>

        {/* Content */}
        {isLoading && savedIds.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {savedIds.map((id) => (
              <Card key={id} className="h-48 w-full animate-pulse">
                <div className="flex h-full flex-col p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <Skeleton className="h-4 w-16 rounded" />
                    <Skeleton className="h-5 w-5 rounded-full" />
                  </div>
                  <Skeleton className="mb-2 h-5 w-3/4 rounded" />
                  <Skeleton className="mb-4 h-4 w-full rounded" />
                  <Skeleton className="h-4 w-2/3 rounded" />
                </div>
              </Card>
            ))}
          </div>
        ) : hasResources ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {resources.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/10 py-16 text-center">
            <Bookmark className="mb-4 h-12 w-12 text-muted-foreground/40" />
            <h2 className="mb-2 text-xl font-semibold text-muted-foreground">No saved resources yet</h2>
            <p className="mb-6 max-w-md text-muted-foreground">
              Click the bookmark icon on any resource to save it for later.
              Saved resources are stored on this device only.
            </p>
            <Button asChild>
              <Link href="/search">Browse Resources</Link>
            </Button>
          </div>
        )}

        {/* Error handling for failed resource fetches */}
        {resourceQueries.some((q) => q.isError) && (
          <div className="mt-4 flex items-start gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <p>
              Some resources couldn&apos;t be loaded. They may have been removed or are temporarily unavailable.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
