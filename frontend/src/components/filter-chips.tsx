'use client';

import { X, Briefcase, GraduationCap, Home, Scale, Globe, MapPin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { CATEGORIES, STATES, SCOPES, type FilterState } from '@/components/filters-sidebar';

interface FilterChipsProps {
  filters: FilterState;
  onRemoveCategory: (category: string) => void;
  onRemoveState: (state: string) => void;
  onClearScope: () => void;
  onClearAll: () => void;
  className?: string;
}

// Match the card badge styling from resource-card.tsx
const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.1)] text-[hsl(var(--v4v-employment))] border-[hsl(var(--v4v-employment)/0.3)]',
  training: 'bg-[hsl(var(--v4v-training)/0.1)] text-[hsl(var(--v4v-training))] border-[hsl(var(--v4v-training)/0.3)]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.1)] text-[hsl(var(--v4v-housing))] border-[hsl(var(--v4v-housing)/0.3)]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.1)] text-[hsl(var(--v4v-legal))] border-[hsl(var(--v4v-legal)/0.3)]',
};

const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: GraduationCap,
  housing: Home,
  legal: Scale,
};

export function FilterChips({
  filters,
  onRemoveCategory,
  onRemoveState,
  onClearScope,
  onClearAll,
  className,
}: FilterChipsProps) {
  const hasFilters =
    filters.categories.length > 0 ||
    filters.states.length > 0 ||
    filters.scope !== 'all';

  if (!hasFilters) return null;

  const getCategoryLabel = (value: string) =>
    CATEGORIES.find((c) => c.value === value)?.label || value;

  const getStateLabel = (value: string) =>
    STATES.find((s) => s.value === value)?.label || value;

  const getScopeLabel = (value: string) =>
    SCOPES.find((s) => s.value === value)?.label || value;

  const totalChips =
    filters.categories.length +
    filters.states.length +
    (filters.scope !== 'all' ? 1 : 0);

  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      {/* Category chips - styled like card badges */}
      {filters.categories.map((category) => {
        const Icon = categoryIcons[category] || Briefcase;
        return (
          <Badge
            key={`cat-${category}`}
            variant="outline"
            className={cn(
              'cursor-pointer gap-1 border font-medium transition-opacity hover:opacity-80',
              categoryBadgeStyles[category]
            )}
            onClick={() => onRemoveCategory(category)}
          >
            <Icon className="h-3 w-3" />
            <span className="capitalize">{getCategoryLabel(category)}</span>
            <X className="h-3 w-3 ml-0.5" />
          </Badge>
        );
      })}

      {/* State chips - gold styling like location badges */}
      {filters.states.map((state) => (
        <Badge
          key={`state-${state}`}
          variant="outline"
          className="cursor-pointer gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.08)] text-[hsl(var(--v4v-gold))] font-medium transition-opacity hover:opacity-80"
          onClick={() => onRemoveState(state)}
        >
          <MapPin className="h-3 w-3" />
          {getStateLabel(state)}
          <X className="h-3 w-3 ml-0.5" />
        </Badge>
      ))}

      {/* Scope chip - gold styling */}
      {filters.scope !== 'all' && (
        <Badge
          variant="outline"
          className="cursor-pointer gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.08)] text-[hsl(var(--v4v-gold))] font-medium transition-opacity hover:opacity-80"
          onClick={onClearScope}
        >
          <Globe className="h-3 w-3" />
          {getScopeLabel(filters.scope)}
          <X className="h-3 w-3 ml-0.5" />
        </Badge>
      )}

      {/* Clear all - only show if more than one filter */}
      {totalChips > 1 && (
        <button
          onClick={onClearAll}
          className="text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
        >
          Clear all
        </button>
      )}
    </div>
  );
}
