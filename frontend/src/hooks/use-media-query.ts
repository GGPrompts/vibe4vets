import { useEffect, useState } from 'react';

/**
 * Hook to detect media query matches.
 * Returns undefined during SSR/initial hydration, then the actual match value.
 * This prevents hydration mismatches by ensuring server and client start with the same value.
 */
export function useMediaQuery(query: string): boolean | undefined {
  const [matches, setMatches] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}

/**
 * Hook to detect mobile viewport (< 1024px).
 * Returns undefined during SSR/initial hydration, then the actual value.
 * Components should handle undefined (e.g., use fallback or show loading state).
 */
export function useIsMobile(): boolean | undefined {
  const matches = useMediaQuery('(min-width: 1024px)');
  // Return undefined if matches is undefined, otherwise negate it
  return matches === undefined ? undefined : !matches;
}
