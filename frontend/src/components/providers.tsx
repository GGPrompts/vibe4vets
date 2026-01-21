"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { FilterProvider } from "@/context/filter-context";
import { SavedResourcesProvider } from "@/context/saved-resources-context";
import { MagnifierProvider } from "@/context/magnifier-context";

export function Providers({ children }: { children: React.ReactNode }) {
  // Create QueryClient inside useState to ensure it's created once per client
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <MagnifierProvider>
        <SavedResourcesProvider>
          <FilterProvider>{children}</FilterProvider>
        </SavedResourcesProvider>
      </MagnifierProvider>
    </QueryClientProvider>
  );
}
