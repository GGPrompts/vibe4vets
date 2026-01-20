import { useState, useEffect } from 'react';
import { useDebounce } from './use-debounce';
import { api } from '@/lib/api';

export interface FilterState {
  categories: string[];
  states: string[];
}

export function useResourceCount(filters: FilterState, enabled: boolean = true) {
  const [count, setCount] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Debounce filters to avoid excessive API calls
  const debouncedFilters = useDebounce(filters, 300);

  useEffect(() => {
    if (!enabled) {
      setCount(null);
      setIsLoading(false);
      return;
    }

    const fetchCount = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const params: { categories?: string; states?: string } = {};
        if (debouncedFilters.categories.length > 0) {
          params.categories = debouncedFilters.categories.join(',');
        }
        if (debouncedFilters.states.length > 0) {
          params.states = debouncedFilters.states.join(',');
        }

        const result = await api.resources.count(params);
        setCount(result.count);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch count'));
        setCount(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCount();
  }, [debouncedFilters, enabled]);

  return { count, isLoading, error };
}
