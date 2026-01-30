'use client';

import { useMemo } from 'react';
import { MapPin, Globe } from 'lucide-react';
import { ResourceCard } from '@/components/resource-card';
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
 * All loaded items are displayed - infinite scroll handles pagination.
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

  const renderSection = (
    title: string,
    icon: typeof MapPin,
    sectionResources: Resource[],
    totalCount: number
  ) => {
    if (sectionResources.length === 0) return null;

    const Icon = icon;

    return (
      <section className="space-y-4">
        {/* Section Header - non-interactive, just informational */}
        <div
          className="relative z-20 flex w-full items-center justify-between rounded-lg bg-muted/50 px-4 py-3"
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
        </div>

        {/* Section Content - show all loaded items, infinite scroll handles pagination */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {sectionResources.map((resource) => (
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
        localResources.length
      )}

      {/* National Section */}
      {renderSection(
        'Available Nationwide',
        Globe,
        nationalResources,
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
