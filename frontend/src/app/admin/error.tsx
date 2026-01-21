'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function AdminError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Admin error:', error);
  }, [error]);

  return (
    <div className="min-h-[50vh] flex items-center justify-center px-6 py-16">
      <div className="flex flex-col items-center text-center max-w-md">
        <div className="rounded-full bg-destructive/10 p-4 mb-6">
          <AlertTriangle className="h-10 w-10 text-destructive" />
        </div>

        <h2 className="font-display text-xl font-semibold text-foreground sm:text-2xl">
          Admin section error
        </h2>

        <p className="mt-3 text-muted-foreground">
          Something went wrong in the admin area. Try refreshing or go back to the main admin page.
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
            <Link href="/admin" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Admin home
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
