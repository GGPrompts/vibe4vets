'use client';

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';

const STORAGE_KEY = 'vibe4vets-magnifier';

interface MagnifierContextValue {
  enabled: boolean;
  zoomLevel: number;
  toggleEnabled: () => void;
  setZoomLevel: (level: number) => void;
  isHydrated: boolean;
}

const MagnifierContext = createContext<MagnifierContextValue | null>(null);

export function MagnifierProvider({ children }: { children: ReactNode }) {
  const [enabled, setEnabled] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(2.0);
  const [isHydrated, setIsHydrated] = useState(false);

  // Hydrate from localStorage on mount (client-side only)
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (typeof parsed.enabled === 'boolean') {
          setEnabled(parsed.enabled);
        }
        if (typeof parsed.zoomLevel === 'number') {
          setZoomLevel(parsed.zoomLevel);
        }
      }
    } catch (e) {
      // Invalid JSON or localStorage not available
      console.warn('Failed to load magnifier settings from localStorage:', e);
    }
    setIsHydrated(true);
  }, []);

  // Persist to localStorage whenever settings change (after hydration)
  useEffect(() => {
    if (isHydrated) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ enabled, zoomLevel }));
      } catch (e) {
        console.warn('Failed to save magnifier settings to localStorage:', e);
      }
    }
  }, [enabled, zoomLevel, isHydrated]);

  const toggleEnabled = useCallback(() => {
    setEnabled((prev) => !prev);
  }, []);

  const handleSetZoomLevel = useCallback((level: number) => {
    setZoomLevel(Math.max(1.5, Math.min(4, level)));
  }, []);

  return (
    <MagnifierContext.Provider
      value={{
        enabled,
        zoomLevel,
        toggleEnabled,
        setZoomLevel: handleSetZoomLevel,
        isHydrated,
      }}
    >
      {children}
    </MagnifierContext.Provider>
  );
}

export function useMagnifier() {
  const context = useContext(MagnifierContext);
  if (!context) {
    throw new Error('useMagnifier must be used within a MagnifierProvider');
  }
  return context;
}

export function useOptionalMagnifier() {
  return useContext(MagnifierContext);
}
