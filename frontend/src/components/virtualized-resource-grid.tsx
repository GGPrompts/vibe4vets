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
}

// Responsive breakpoints (matches Tailwind)
const BREAKPOINTS = {
  sm: 640,
  lg: 1024,
  xl: 1280,
};

// Card heights (approximate, cards are relatively fixed)
const CARD_HEIGHT = 320; // Approximate card height in pixels
const ROW_GAP = 16; // gap-4 = 1rem = 16px

function useResponsiveColumns() {
  const [columns, setColumns] = useState(1);

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

    updateColumns();
    window.addEventListener('resize', updateColumns);
    return () => window.removeEventListener('resize', updateColumns);
  }, []);

  return columns;
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
}: VirtualizedResourceGridProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  const columns = useResponsiveColumns();

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
  });

  const virtualItems = virtualizer.getVirtualItems();

  // Trigger fetchNextPage when scrolling near the bottom
  useEffect(() => {
    if (!fetchNextPage || !hasNextPage || isFetchingNextPage) return;

    const lastItem = virtualItems[virtualItems.length - 1];
    if (!lastItem) return;

    // Trigger when we're within 3 rows of the end
    if (lastItem.index >= rows.length - 3) {
      fetchNextPage();
    }
  }, [virtualItems, rows.length, hasNextPage, isFetchingNextPage, fetchNextPage]);

  // For window-level scrolling, we need to observe when the parent element is near the bottom of the viewport
  const [isNearBottom, setIsNearBottom] = useState(false);

  useEffect(() => {
    if (!fetchNextPage || !hasNextPage || isFetchingNextPage) return;

    const checkNearBottom = () => {
      const el = parentRef.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const windowHeight = window.innerHeight;

      // Check if the bottom of the container is within 1200px of the viewport bottom
      const distanceToBottom = rect.bottom - windowHeight;
      setIsNearBottom(distanceToBottom < 1200);
    };

    checkNearBottom();
    window.addEventListener('scroll', checkNearBottom);
    window.addEventListener('resize', checkNearBottom);

    return () => {
      window.removeEventListener('scroll', checkNearBottom);
      window.removeEventListener('resize', checkNearBottom);
    };
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  useEffect(() => {
    if (isNearBottom && hasNextPage && !isFetchingNextPage && fetchNextPage) {
      fetchNextPage();
    }
  }, [isNearBottom, hasNextPage, isFetchingNextPage, fetchNextPage]);

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
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualRow.size}px`,
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
                          disableAnimation
                            ? false
                            : isNewItem
                              ? { opacity: 0, y: 20 }
                              : false
                        }
                        animate={
                          disableAnimation ? false : { opacity: 1, y: 0 }
                        }
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={
                          disableAnimation
                            ? { duration: 0 }
                            : isNewItem
                              ? {
                                  delay: newItemIndex * 0.02,
                                  layout: { duration: 0.3 },
                                }
                              : { layout: { duration: 0.3 } }
                        }
                        layout={disableAnimation ? false : 'position'}
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
                          enableLayoutId
                        />
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </AnimatePresence>
      </div>
    </LayoutGroup>
  );
}
