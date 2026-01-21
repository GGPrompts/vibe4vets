'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console in development
    console.error('Application error:', error);
  }, [error]);

  return (
    <main className="min-h-screen flex items-center justify-center bg-background px-6 py-16">
      <div className="flex flex-col items-center text-center max-w-md">
        <div className="rounded-full bg-destructive/10 p-4 mb-6">
          <AlertTriangle className="h-12 w-12 text-destructive" />
        </div>

        <h1 className="font-display text-2xl font-semibold text-foreground sm:text-3xl">
          Something went wrong
        </h1>

        <p className="mt-4 text-muted-foreground">
          We encountered an unexpected error. This has been logged and we&apos;ll look into it.
        </p>

        {error.digest && (
          <p className="mt-2 text-sm text-muted-foreground/70 font-mono">
            Error ID: {error.digest}
          </p>
        )}

        <div className="mt-8 flex flex-col sm:flex-row gap-3">
          <Button onClick={reset} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Try again
          </Button>
          <Button variant="outline" asChild>
            <Link href="/" className="gap-2">
              <Home className="h-4 w-4" />
              Go home
            </Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
