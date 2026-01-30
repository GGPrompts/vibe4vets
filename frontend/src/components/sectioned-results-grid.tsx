'use client';

import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, MapPin, Globe } from 'lucide-react';
import { ResourceCard } from '@/components/resource-card';
import { Button } from '@/components/ui/button';
import type { Resource, MatchExplanation } from '@/lib/api';

interface SectionedResultsGridProps {
  resources: Resource[];
  explanationsMap: Map<string, MatchExplanation[]>;
  distanceMap?: Map<string, number>;
  onResourceClick: (resource: Resource, explanations?: MatchExplanation[]) => void;
  /** Enable layoutId for shared element transitions */
  enableLayoutId?: boolean;
  /** Location label for the "Near You" section (e.g., zip code or state) */
  locationLabel?: string;
}

/**
 * Groups resources into "Near You" (local/state) and "Nationwide" (national) sections.
 * Displays each section with a header showing the count.
 */
export function SectionedResultsGrid({
  resources,
  explanationsMap,
  distanceMap,
  onResourceClick,
  enableLayoutId = true,
  locationLabel,
}: SectionedResultsGridProps) {
  // Group resources by scope
  const { localResources, nationalResources } = useMemo(() => {
    const local: Resource[] = [];
    const national: Resource[] = [];

    for (const resource of resources) {
      if (resource.scope === 'national') {
        national.push(resource);
      } else {
        // 'local' or 'state' scope goes in local section
        local.push(resource);
      }
    }

    return { localResources: local, nationalResources: national };
  }, [resources]);

  // Track collapsed state for each section
  const [localCollapsed, setLocalCollapsed] = useState(false);
  const [nationalCollapsed, setNationalCollapsed] = useState(false);

  // Initial items to show before "Load more"
  const INITIAL_ITEMS = 12;
  const [localShowAll, setLocalShowAll] = useState(false);
  const [nationalShowAll, setNationalShowAll] = useState(false);

  const displayedLocalResources = localShowAll
    ? localResources
    : localResources.slice(0, INITIAL_ITEMS);
  const displayedNationalResources = nationalShowAll
    ? nationalResources
    : nationalResources.slice(0, INITIAL_ITEMS);

  const hasMoreLocal = localResources.length > INITIAL_ITEMS;
  const hasMoreNational = nationalResources.length > INITIAL_ITEMS;

  const renderSection = (
    title: string,
    icon: typeof MapPin,
    sectionResources: Resource[],
    displayedResources: Resource[],
    isCollapsed: boolean,
    setCollapsed: (value: boolean) => void,
    showAll: boolean,
    setShowAll: (value: boolean) => void,
    hasMore: boolean,
    totalCount: number
  ) => {
    if (sectionResources.length === 0) return null;

    const Icon = icon;

    return (
      <section className="space-y-4">
        {/* Section Header */}
        <button
          onClick={() => setCollapsed(!isCollapsed)}
          className="flex w-full items-center justify-between rounded-lg bg-muted/50 px-4 py-3 transition-colors hover:bg-muted"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div className="text-left">
              <h2 className="text-lg font-semibold text-foreground">
                {title}
              </h2>
              <p className="text-sm text-muted-foreground">
                {totalCount} {totalCount === 1 ? 'resource' : 'resources'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            {isCollapsed ? (
              <ChevronDown className="h-5 w-5" />
            ) : (
              <ChevronUp className="h-5 w-5" />
            )}
          </div>
        </button>

        {/* Section Content */}
        <AnimatePresence initial={false}>
          {!isCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {displayedResources.map((resource) => (
                  <ResourceCard
                    key={resource.id}
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
                ))}
              </div>

              {/* Load More Button */}
              {hasMore && (
                <div className="mt-4 flex justify-center">
                  <Button
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowAll(!showAll);
                    }}
                  >
                    {showAll
                      ? `Show less`
                      : `Load more (${totalCount - INITIAL_ITEMS} more)`}
                  </Button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    );
  };

  // Build local section title with location label
  const localTitle = locationLabel
    ? `Near You (${locationLabel})`
    : 'Near You';

  return (
    <div className="space-y-8">
      {/* Local/State Section - shown first */}
      {renderSection(
        localTitle,
        MapPin,
        localResources,
        displayedLocalResources,
        localCollapsed,
        setLocalCollapsed,
        localShowAll,
        setLocalShowAll,
        hasMoreLocal,
        localResources.length
      )}

      {/* National Section */}
      {renderSection(
        'Available Nationwide',
        Globe,
        nationalResources,
        displayedNationalResources,
        nationalCollapsed,
        setNationalCollapsed,
        nationalShowAll,
        setNationalShowAll,
        hasMoreNational,
        nationalResources.length
      )}

      {/* Empty State */}
      {resources.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-lg text-muted-foreground">
            No resources found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
}
