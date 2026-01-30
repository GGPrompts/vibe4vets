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
  // Tag filtering
  tags: string[];
  setTags: (tags: string[]) => void;
  toggleTag: (tag: string) => void;
  // Resource count
  resourceCount: number | null;
  isLoadingCount: boolean;
  totalCount: number | null;
  isLoadingTotal: boolean;
  isEnabled: boolean;
  setEnabled: (enabled: boolean) => void;
  // Sidebar state - allows header to open the filter sidebar (desktop)
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  openSidebar: () => void;
  // Mobile filter sheet state - shared between header and search page
  mobileFiltersOpen: boolean;
  setMobileFiltersOpen: (open: boolean) => void;
  openMobileFilters: () => void;
}

const FilterContext = createContext<FilterContextValue | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<FilterState>({
    categories: [],
    states: [],
  });
  const [tags, setTagsState] = useState<string[]>([]);
  const [isEnabled, setEnabled] = useState(false);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [isLoadingTotal, setIsLoadingTotal] = useState(false);

  // Sidebar collapsed state - initialized from localStorage
  const [sidebarCollapsed, setSidebarCollapsedState] = useState(true);

  // Initialize from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('v4v-filters-collapsed');
    if (stored !== null) {
      setSidebarCollapsedState(stored === 'true');
    }
  }, []);

  const setSidebarCollapsed = useCallback((collapsed: boolean) => {
    setSidebarCollapsedState(collapsed);
    localStorage.setItem('v4v-filters-collapsed', String(collapsed));
  }, []);

  const openSidebar = useCallback(() => {
    setSidebarCollapsed(false);
  }, [setSidebarCollapsed]);

  // Mobile filter sheet state
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const openMobileFilters = useCallback(() => {
    setMobileFiltersOpen(true);
  }, []);

  const { count, isLoading } = useResourceCount(filters, isEnabled);

  // Fetch total count once on mount (unfiltered)
  useEffect(() => {
    let mounted = true;

    const fetchTotal = async () => {
      setIsLoadingTotal(true);
      try {
        const result = await api.resources.count({});
        if (mounted) {
          setTotalCount(result.count);
        }
      } catch {
        if (mounted) {
          setTotalCount(null);
        }
      } finally {
        if (mounted) {
          setIsLoadingTotal(false);
        }
      }
    };
    fetchTotal();

    return () => {
      mounted = false;
    };
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

  const setTags = useCallback((newTags: string[]) => {
    setTagsState(newTags);
  }, []);

  const toggleTag = useCallback((tag: string) => {
    setTagsState((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  }, []);

  return (
    <FilterContext.Provider
      value={{
        filters,
        setCategories,
        setStates,
        toggleCategory,
        toggleState,
        tags,
        setTags,
        toggleTag,
        resourceCount: count,
        isLoadingCount: isLoading,
        totalCount,
        isLoadingTotal,
        isEnabled,
        setEnabled,
        sidebarCollapsed,
        setSidebarCollapsed,
        openSidebar,
        mobileFiltersOpen,
        setMobileFiltersOpen,
        openMobileFilters,
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
