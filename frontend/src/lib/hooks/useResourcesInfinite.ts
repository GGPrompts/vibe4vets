'use client';

import { useInfiniteQuery } from '@tanstack/react-query';
import api, { type ResourceList } from '@/lib/api';

export interface ResourceFilters {
  categories?: string[];
  states?: string[];
  scope?: string;
  tags?: string[];
}

const PAGE_SIZE = 50;

/**
 * Fetches resources with infinite scrolling and server-side filtering.
 */
export function useResourcesInfinite(filters: ResourceFilters) {
  return useInfiniteQuery({
    queryKey: ['resources', filters],
    queryFn: async ({ pageParam = 0 }): Promise<ResourceList> => {
      const params: Record<string, string | number> = {
        limit: PAGE_SIZE,
        offset: pageParam,
      };

      // Server-side filtering with comma-separated values
      if (filters.categories && filters.categories.length > 0) {
        params.categories = filters.categories.join(',');
      }
      if (filters.states && filters.states.length > 0) {
        params.states = filters.states.join(',');
      }
      if (filters.scope && filters.scope !== 'all') {
        params.scope = filters.scope;
      }
      if (filters.tags && filters.tags.length > 0) {
        params.tags = filters.tags.join(',');
      }

      console.log('[useResourcesInfinite] Fetching with params:', params);
      return api.resources.list(params);
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage, _allPages, lastPageParam) => {
      // If we got fewer results than page size, we've reached the end
      if (lastPage.resources.length < PAGE_SIZE) {
        return undefined;
      }
      // Otherwise, return the next offset
      return lastPageParam + PAGE_SIZE;
    },
    // Keep previous data visible while loading next page
    placeholderData: (previousData) => previousData,
  });
}
