'use client';

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';

const STORAGE_KEY = 'vibe4vets-saved-resources';

interface SavedResourcesContextValue {
  savedIds: string[];
  isSaved: (id: string) => boolean;
  toggleSaved: (id: string) => void;
  addSaved: (id: string) => void;
  removeSaved: (id: string) => void;
  clearAll: () => void;
  count: number;
  isHydrated: boolean;
}

const SavedResourcesContext = createContext<SavedResourcesContextValue | null>(null);

export function SavedResourcesProvider({ children }: { children: ReactNode }) {
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [isHydrated, setIsHydrated] = useState(false);

  // Hydrate from localStorage on mount (client-side only)
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setSavedIds(parsed);
        }
      }
    } catch (e) {
      // Invalid JSON or localStorage not available, use empty array
      console.warn('Failed to load saved resources from localStorage:', e);
    }
    setIsHydrated(true);
  }, []);

  // Persist to localStorage whenever savedIds changes (after hydration)
  useEffect(() => {
    if (isHydrated) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(savedIds));
      } catch (e) {
        console.warn('Failed to save resources to localStorage:', e);
      }
    }
  }, [savedIds, isHydrated]);

  const isSaved = useCallback((id: string) => {
    return savedIds.includes(id);
  }, [savedIds]);

  const toggleSaved = useCallback((id: string) => {
    setSavedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((savedId) => savedId !== id);
      }
      return [...prev, id];
    });
  }, []);

  const addSaved = useCallback((id: string) => {
    setSavedIds((prev) => {
      if (prev.includes(id)) {
        return prev;
      }
      return [...prev, id];
    });
  }, []);

  const removeSaved = useCallback((id: string) => {
    setSavedIds((prev) => prev.filter((savedId) => savedId !== id));
  }, []);

  const clearAll = useCallback(() => {
    setSavedIds([]);
  }, []);

  return (
    <SavedResourcesContext.Provider
      value={{
        savedIds,
        isSaved,
        toggleSaved,
        addSaved,
        removeSaved,
        clearAll,
        count: savedIds.length,
        isHydrated,
      }}
    >
      {children}
    </SavedResourcesContext.Provider>
  );
}

export function useSavedResources() {
  const context = useContext(SavedResourcesContext);
  if (!context) {
    throw new Error('useSavedResources must be used within a SavedResourcesProvider');
  }
  return context;
}

export function useOptionalSavedResources() {
  return useContext(SavedResourcesContext);
}
