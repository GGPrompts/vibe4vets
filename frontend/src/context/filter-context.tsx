'use client';

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import { useResourceCount, type FilterState } from '@/hooks/use-resource-count';
import { api } from '@/lib/api';

interface FilterContextValue {
  filters: FilterState;
  setCategories: (categories: string[]) => void;
  setStates: (states: string[]) => void;
  toggleCategory: (category: string) => void;
  toggleState: (state: string) => void;
  resourceCount: number | null;
  isLoadingCount: boolean;
  totalCount: number | null;
  isLoadingTotal: boolean;
  isEnabled: boolean;
  setEnabled: (enabled: boolean) => void;
}

const FilterContext = createContext<FilterContextValue | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<FilterState>({
    categories: [],
    states: [],
  });
  const [isEnabled, setEnabled] = useState(false);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [isLoadingTotal, setIsLoadingTotal] = useState(false);

  const { count, isLoading } = useResourceCount(filters, isEnabled);

  // Fetch total count once on mount (unfiltered)
  useEffect(() => {
    const fetchTotal = async () => {
      setIsLoadingTotal(true);
      try {
        const result = await api.resources.count({});
        setTotalCount(result.count);
      } catch {
        setTotalCount(null);
      } finally {
        setIsLoadingTotal(false);
      }
    };
    fetchTotal();
  }, []);

  const setCategories = useCallback((categories: string[]) => {
    setFilters((prev) => ({ ...prev, categories }));
  }, []);

  const setStates = useCallback((states: string[]) => {
    setFilters((prev) => ({ ...prev, states }));
  }, []);

  const toggleCategory = useCallback((category: string) => {
    setFilters((prev) => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter((c) => c !== category)
        : [...prev.categories, category],
    }));
  }, []);

  const toggleState = useCallback((state: string) => {
    setFilters((prev) => ({
      ...prev,
      states: prev.states.includes(state)
        ? prev.states.filter((s) => s !== state)
        : [...prev.states, state],
    }));
  }, []);

  return (
    <FilterContext.Provider
      value={{
        filters,
        setCategories,
        setStates,
        toggleCategory,
        toggleState,
        resourceCount: count,
        isLoadingCount: isLoading,
        totalCount,
        isLoadingTotal,
        isEnabled,
        setEnabled,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilterContext() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilterContext must be used within a FilterProvider');
  }
  return context;
}

export function useOptionalFilterContext() {
  return useContext(FilterContext);
}
