'use client';

import { X, Briefcase, GraduationCap, Home, Scale, Globe, MapPin, UtensilsCrossed, Award, Brain, HeartHandshake, HeartPulse, School, Wallet, Tag } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { CATEGORIES, STATES, SCOPES, type FilterState } from '@/components/filters-sidebar';

interface FilterChipsProps {
  filters: FilterState;
  onRemoveCategory: (category: string) => void;
  onRemoveState: (state: string) => void;
  onClearScope: () => void;
  onClearZip?: () => void;
  onRemoveTag?: (tag: string) => void;
  onClearAll: () => void;
  className?: string;
}

// Higher contrast badge styling for filter chips on light backgrounds
const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment))] text-white border-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training))] text-white border-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing))] text-white border-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal))] text-white border-[hsl(var(--v4v-legal))]',
  food: 'bg-[hsl(var(--v4v-food))] text-white border-[hsl(var(--v4v-food))]',
  benefits: 'bg-[hsl(var(--v4v-benefits))] text-white border-[hsl(var(--v4v-benefits))]',
  mentalHealth: 'bg-[hsl(var(--v4v-mentalHealth))] text-white border-[hsl(var(--v4v-mentalHealth))]',
  supportServices: 'bg-[hsl(var(--v4v-supportServices))] text-white border-[hsl(var(--v4v-supportServices))]',
  healthcare: 'bg-[hsl(var(--v4v-healthcare))] text-white border-[hsl(var(--v4v-healthcare))]',
  education: 'bg-[hsl(var(--v4v-education))] text-white border-[hsl(var(--v4v-education))]',
  financial: 'bg-[hsl(var(--v4v-financial))] text-white border-[hsl(var(--v4v-financial))]',
};

const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: GraduationCap,
  housing: Home,
  legal: Scale,
  food: UtensilsCrossed,
  benefits: Award,
  mentalHealth: Brain,
  supportServices: HeartHandshake,
  healthcare: HeartPulse,
  education: School,
  financial: Wallet,
};

// Convert tag ID to display name
function getTagDisplayName(tag: string): string {
  const specialCases: Record<string, string> = {
    'hud-vash': 'HUD-VASH',
    'ssvf': 'SSVF',
    'section-8': 'Section 8',
    'va-appeals': 'VA Appeals',
    'gi-bill': 'GI Bill',
    'gi-bill-approved': 'GI Bill Approved',
    'vre-approved': 'VR&E Approved',
    'vso': 'VSO',
    'cvso': 'CVSO',
    'ptsd-treatment': 'PTSD Treatment',
    'mst': 'MST',
  };
  if (specialCases[tag]) return specialCases[tag];
  return tag.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

export function FilterChips({
  filters,
  onRemoveCategory,
  onRemoveState,
  onClearScope,
  onClearZip,
  onRemoveTag,
  onClearAll,
  className,
}: FilterChipsProps) {
  const hasTags = (filters.tags?.length ?? 0) > 0;
  const hasFilters =
    filters.categories.length > 0 ||
    filters.states.length > 0 ||
    filters.scope !== 'all' ||
    !!filters.zip ||
    hasTags;

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
    (filters.scope !== 'all' ? 1 : 0) +
    (filters.zip ? 1 : 0) +
    (filters.tags?.length ?? 0);

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

      {/* State chips - high contrast gold styling */}
      {filters.states.map((state) => (
        <Badge
          key={`state-${state}`}
          variant="outline"
          className="cursor-pointer gap-1 border-[hsl(var(--v4v-gold-dark))] bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))] font-medium transition-opacity hover:opacity-80"
          onClick={() => onRemoveState(state)}
        >
          <MapPin className="h-3 w-3" />
          {getStateLabel(state)}
          <X className="h-3 w-3 ml-0.5" />
        </Badge>
      ))}

      {/* Scope chip - high contrast gold styling */}
      {filters.scope !== 'all' && (
        <Badge
          variant="outline"
          className="cursor-pointer gap-1 border-[hsl(var(--v4v-gold-dark))] bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))] font-medium transition-opacity hover:opacity-80"
          onClick={onClearScope}
        >
          <Globe className="h-3 w-3" />
          {getScopeLabel(filters.scope)}
          <X className="h-3 w-3 ml-0.5" />
        </Badge>
      )}

      {/* Zip code chip - emerald styling for proximity search */}
      {filters.zip && onClearZip && (
        <Badge
          variant="outline"
          className="cursor-pointer gap-1 border-emerald-600 bg-emerald-500 text-white font-medium transition-opacity hover:opacity-80"
          onClick={onClearZip}
        >
          <MapPin className="h-3 w-3" />
          Near {filters.zip} ({filters.radius || 25} mi)
          <X className="h-3 w-3 ml-0.5" />
        </Badge>
      )}

      {/* Tag chips - teal styling */}
      {filters.tags?.map((tag) => (
        <Badge
          key={`tag-${tag}`}
          variant="outline"
          className="cursor-pointer gap-1 border-teal-600 bg-teal-500 text-white font-medium transition-opacity hover:opacity-80"
          onClick={() => onRemoveTag?.(tag)}
        >
          <Tag className="h-3 w-3" />
          {getTagDisplayName(tag)}
          <X className="h-3 w-3 ml-0.5" />
        </Badge>
      ))}

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
