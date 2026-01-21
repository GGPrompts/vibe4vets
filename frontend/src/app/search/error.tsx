'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, Search } from 'lucide-react';
import Link from 'next/link';

export default function SearchError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Search error:', error);
  }, [error]);

  return (
    <div className="min-h-[50vh] flex items-center justify-center px-6 py-16">
      <div className="flex flex-col items-center text-center max-w-md">
        <div className="rounded-full bg-destructive/10 p-4 mb-6">
          <AlertTriangle className="h-10 w-10 text-destructive" />
        </div>

        <h2 className="font-display text-xl font-semibold text-foreground sm:text-2xl">
          Search failed
        </h2>

        <p className="mt-3 text-muted-foreground">
          We couldn&apos;t complete your search. Try again or start a new search.
        </p>

        {error.digest && (
          <p className="mt-2 text-sm text-muted-foreground/70 font-mono">
            Error ID: {error.digest}
          </p>
        )}

        <div className="mt-6 flex flex-col sm:flex-row gap-3">
          <Button onClick={reset} size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Try again
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link href="/search" className="gap-2">
              <Search className="h-4 w-4" />
              New search
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
