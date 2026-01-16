'use client';

import { useEffect, useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { ResourceCard } from '@/components/resource-card';
import { Skeleton } from '@/components/ui/skeleton';
import api, { type Resource } from '@/lib/api';

interface DiscoveryFeedProps {
  category?: string;
  state?: string;
}

interface DateGroup {
  label: string;
  resources: Resource[];
}

function isWithinDays(dateStr: string, days: number): boolean {
  const date = new Date(dateStr);
  const now = new Date();
  const diffTime = now.getTime() - date.getTime();
  const diffDays = diffTime / (1000 * 60 * 60 * 24);
  return diffDays <= days;
}

function groupResourcesByDate(resources: Resource[]): DateGroup[] {
  const thisWeek: Resource[] = [];
  const last30Days: Resource[] = [];
  const older: Resource[] = [];

  resources.forEach((resource) => {
    const createdAt = resource.created_at;
    if (isWithinDays(createdAt, 7)) {
      thisWeek.push(resource);
    } else if (isWithinDays(createdAt, 30)) {
      last30Days.push(resource);
    } else {
      older.push(resource);
    }
  });

  const groups: DateGroup[] = [];

  if (thisWeek.length > 0) {
    groups.push({ label: 'Added this week', resources: thisWeek });
  }
  if (last30Days.length > 0) {
    groups.push({ label: 'Added in the last 30 days', resources: last30Days });
  }
  if (older.length > 0) {
    groups.push({ label: 'More resources', resources: older });
  }

  return groups;
}


export function DiscoveryFeed({ category, state }: DiscoveryFeedProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [groups, setGroups] = useState<DateGroup[]>([]);

  useEffect(() => {
    async function fetchResources() {
      setLoading(true);
      setError(null);

      try {
        const result = await api.resources.list({
          category,
          state,
          limit: 50,
        });

        // Sort by created_at descending (newest first)
        const sortedResources = [...result.resources].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );

        const dateGroups = groupResourcesByDate(sortedResources);
        setGroups(dateGroups);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resources');
      } finally {
        setLoading(false);
      }
    }

    fetchResources();
  }, [category, state]);

  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <Skeleton className="mb-4 h-8 w-48" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-48 w-full rounded-lg" />
            ))}
          </div>
        </div>
        <div>
          <Skeleton className="mb-4 h-8 w-48" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-48 w-full rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-8 text-center">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  if (groups.length === 0) {
    return (
      <div className="rounded-xl border border-[hsl(var(--border))] bg-white p-12 text-center">
        <FolderOpen className="mx-auto mb-4 h-12 w-12 text-[hsl(var(--muted-foreground))]" />
        <h3 className="font-display text-xl text-[hsl(var(--v4v-navy))]">
          No resources found
        </h3>
        <p className="mt-2 text-[hsl(var(--muted-foreground))]">
          Try adjusting your filters to find resources.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      {groups.map((group) => (
        <div key={group.label}>
          <div className="mb-6">
            <div className="editorial-divider mb-3" />
            <h2 className="font-display text-2xl text-[hsl(var(--v4v-navy))]">
              {group.label}
            </h2>
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              {group.resources.length} resource{group.resources.length !== 1 ? 's' : ''}
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {group.resources.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
