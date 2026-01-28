'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { ResourceCard } from '@/components/resource-card';
import type { Resource, MatchExplanation } from '@/lib/api';

interface VirtualizedResourceGridProps {
  resources: Resource[];
  explanationsMap: Map<string, MatchExplanation[]>;
  selectedResourceId?: string | null;
  animatingResourceId?: string | null;
  onResourceClick: (resource: Resource, explanations?: MatchExplanation[]) => void;
  hasNextPage?: boolean;
  isFetchingNextPage?: boolean;
  fetchNextPage?: () => void;
  /** Whether to disable entrance animations (e.g., during pagination) */
  disableAnimation?: boolean;
  /** Set of newly loaded resource IDs for staggered animation */
  newResourceIds?: Set<string>;
  /** Map of new resource ID to its index within the new batch */
  newResourceIndexById?: Map<string, number>;
  /** Map of resource ID to distance in miles (for nearby search) */
  distanceMap?: Map<string, number>;
  /** Whether to enable layoutId for shared element transitions (disable when sidebar expanded) */
  enableLayoutId?: boolean;
}

// Responsive breakpoints (matches Tailwind)
const BREAKPOINTS = {
  sm: 640,
  lg: 1024,
  xl: 1280,
};

// Card heights - estimate for virtualization (actual height measured dynamically)
const CARD_HEIGHT = 300; // Approximate card height
const ROW_GAP = 16; // gap-4 = 1rem = 16px

function useResponsiveColumns() {
  const [columns, setColumns] = useState(1);
  const [isResizing, setIsResizing] = useState(false);
  const resizeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    function updateColumns() {
      const width = window.innerWidth;
      if (width >= BREAKPOINTS.xl) {
        setColumns(4);
      } else if (width >= BREAKPOINTS.lg) {
        setColumns(3);
      } else if (width >= BREAKPOINTS.sm) {
        setColumns(2);
      } else {
        setColumns(1);
      }
    }

    function handleResize() {
      // Mark as resizing to disable animations
      setIsResizing(true);
      updateColumns();

      // Clear existing timeout
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }

      // Re-enable animations after resize settles
      resizeTimeoutRef.current = setTimeout(() => {
        setIsResizing(false);
      }, 150);
    }

    updateColumns();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, []);

  return { columns, isResizing };
}

export function VirtualizedResourceGrid({
  resources,
  explanationsMap,
  selectedResourceId,
  animatingResourceId,
  onResourceClick,
  hasNextPage = false,
  isFetchingNextPage = false,
  fetchNextPage,
  disableAnimation = false,
  newResourceIds,
  newResourceIndexById,
  distanceMap,
  enableLayoutId = true,
}: VirtualizedResourceGridProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  const { columns, isResizing } = useResponsiveColumns();

  // Disable all animations during resize to prevent lag
  const shouldDisableAnimation = disableAnimation || isResizing;

  // Group resources into rows based on column count
  const rows = useMemo(() => {
    const result: Resource[][] = [];
    for (let i = 0; i < resources.length; i += columns) {
      result.push(resources.slice(i, i + columns));
    }
    return result;
  }, [resources, columns]);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => CARD_HEIGHT + ROW_GAP,
    overscan: 5, // Render 5 extra rows above/below viewport for smooth scrolling
    measureElement: (element) => {
      // Measure actual row height for variable-height cards
      return element.getBoundingClientRect().height + ROW_GAP;
    },
  });

  const virtualItems = virtualizer.getVirtualItems();

  // Track if user has scrolled (don't auto-fetch on initial load)
  const hasScrolledRef = useRef(false);

  useEffect(() => {
    const onScroll = () => {
      if (window.scrollY > 100) {
        hasScrolledRef.current = true;
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Single fetch trigger: IntersectionObserver on a sentinel element
  // This is more reliable than measuring container bounds
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!fetchNextPage || !hasNextPage || isFetchingNextPage) return;

    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const isIntersecting = entries[0]?.isIntersecting;
        // Only auto-fetch if user has scrolled down
        if (isIntersecting && hasScrolledRef.current && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { root: null, rootMargin: '400px 0px', threshold: 0 }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  return (
    <LayoutGroup>
      <div
        ref={parentRef}
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        <AnimatePresence mode="popLayout">
          {virtualItems.map((virtualRow) => {
            const rowResources = rows[virtualRow.index];
            if (!rowResources) return null;

            return (
              <div
                key={virtualRow.key}
                data-index={virtualRow.index}
                ref={virtualizer.measureElement}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                <div
                  className="grid gap-4 pr-0 sm:pr-4"
                  style={{
                    gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
                  }}
                >
                  {rowResources.map((resource) => {
                    const isCardAnimating =
                      selectedResourceId === resource.id ||
                      animatingResourceId === resource.id;
                    const isNewItem = newResourceIds?.has(resource.id) ?? false;
                    const newItemIndex = isNewItem
                      ? (newResourceIndexById?.get(resource.id) ?? 0)
                      : 0;

                    return (
                      <motion.div
                        key={resource.id}
                        initial={
                          shouldDisableAnimation
                            ? false
                            : isNewItem
                              ? { opacity: 0, y: 20 }
                              : false
                        }
                        animate={
                          shouldDisableAnimation ? false : { opacity: 1, y: 0 }
                        }
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={
                          shouldDisableAnimation
                            ? { duration: 0 }
                            : isNewItem
                              ? {
                                  delay: newItemIndex * 0.02,
                                  layout: { duration: 0.3 },
                                }
                              : { layout: { duration: 0.3 } }
                        }
                        layout={shouldDisableAnimation ? false : 'position'}
                        style={{
                          position: 'relative',
                          willChange: 'transform',
                          zIndex: isCardAnimating ? 100 : undefined,
                        }}
                        whileHover={{ zIndex: 50, transition: { duration: 0 } }}
                        whileTap={{ zIndex: 50 }}
                        layoutId={`card-wrapper-${resource.id}`}
                      >
                        <ResourceCard
                          resource={resource}
                          explanations={explanationsMap.get(resource.id)}
                          variant="modal"
                          onClick={() =>
                            onResourceClick(
                              resource,
                              explanationsMap.get(resource.id)
                            )
                          }
                          enableLayoutId={enableLayoutId}
                          distance={distanceMap?.get(resource.id)}
                        />
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </AnimatePresence>
        {/* Sentinel for infinite scroll - triggers fetch when visible */}
        {hasNextPage && (
          <div
            ref={sentinelRef}
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              width: '100%',
              height: '1px',
            }}
          />
        )}
      </div>
    </LayoutGroup>
  );
}
