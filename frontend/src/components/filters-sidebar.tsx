'use client';

import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Filter, X, Briefcase, GraduationCap, Home, Scale, UtensilsCrossed, FileCheck, ChevronDown, PanelLeft, PanelLeftClose, Search, MapPin, Brain, HeartHandshake, HeartPulse, School, Wallet, Users, Check, Tag, ArrowUpDown, Clock, ArrowDownAZ, Sparkles, Shuffle, ShieldCheck } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { ZipCodeInput } from '@/components/ZipCodeInput';
import api from '@/lib/api';

export const CATEGORIES = [
  { value: 'employment', label: 'Employment', icon: Briefcase },
  { value: 'training', label: 'Training', icon: GraduationCap },
  { value: 'housing', label: 'Housing', icon: Home },
  { value: 'legal', label: 'Legal', icon: Scale },
  { value: 'food', label: 'Food', icon: UtensilsCrossed },
  { value: 'benefits', label: 'Benefits', icon: FileCheck },
  { value: 'mentalHealth', label: 'Mental Health', icon: Brain },
  { value: 'supportServices', label: 'Support Services', icon: HeartHandshake },
  { value: 'healthcare', label: 'Healthcare', icon: HeartPulse },
  { value: 'education', label: 'Education', icon: School },
  { value: 'financial', label: 'Financial', icon: Wallet },
  { value: 'family', label: 'Family', icon: Users },
] as const;

export const STATES = [
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AS', label: 'American Samoa' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DC', label: 'District of Columbia' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'GU', label: 'Guam' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MP', label: 'Northern Mariana Islands' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'PR', label: 'Puerto Rico' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VI', label: 'U.S. Virgin Islands' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' },
] as const;

export interface FilterState {
  categories: string[];
  states: string[];
  scope: string;
  minTrust: number;
  zip?: string;
  radius?: number;
  tags?: string[];
  // Geolocation coordinates (used when "Use my location" is clicked)
  lat?: number;
  lng?: number;
}

export type SortOption = 'official' | 'relevance' | 'newest' | 'alpha' | 'shuffle' | 'distance';

const SORT_OPTIONS: { value: SortOption; label: string; icon: React.ElementType; description: string }[] = [
  { value: 'official', label: 'Official First', icon: ShieldCheck, description: 'VA, DOL, HUD resources first' },
  { value: 'relevance', label: 'Relevance', icon: Sparkles, description: 'Best matches first' },
  { value: 'distance', label: 'Distance', icon: MapPin, description: 'Closest to you' },
  { value: 'newest', label: 'Newest', icon: Clock, description: 'Recently added' },
  { value: 'alpha', label: 'A-Z', icon: ArrowDownAZ, description: 'Alphabetical order' },
  { value: 'shuffle', label: 'Shuffle', icon: Shuffle, description: 'Randomized order' },
];

interface FiltersSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  resultCount?: number;
  hideHeader?: boolean;
  // Mobile sort controls (optional - only shown when provided)
  sort?: SortOption;
  onSortChange?: (sort: SortOption) => void;
  hasQuery?: boolean;
  hasZip?: boolean;
}

const categoryColors: Record<string, string> = {
  employment: 'text-[hsl(var(--v4v-employment))]',
  training: 'text-[hsl(var(--v4v-training))]',
  housing: 'text-[hsl(var(--v4v-housing))]',
  legal: 'text-[hsl(var(--v4v-legal))]',
  food: 'text-[hsl(var(--v4v-food))]',
  benefits: 'text-[hsl(var(--v4v-benefits))]',
  mentalHealth: 'text-[hsl(var(--v4v-mentalHealth))]',
  supportServices: 'text-[hsl(var(--v4v-supportServices))]',
  healthcare: 'text-[hsl(var(--v4v-healthcare))]',
  education: 'text-[hsl(var(--v4v-education))]',
  financial: 'text-[hsl(var(--v4v-financial))]',
  family: 'text-[hsl(var(--v4v-family))]',
};

const categoryAccents: Record<string, string> = {
  employment: 'border-l-[hsl(var(--v4v-employment))] bg-[hsl(var(--v4v-employment)/0.04)]',
  training: 'border-l-[hsl(var(--v4v-training))] bg-[hsl(var(--v4v-training)/0.04)]',
  housing: 'border-l-[hsl(var(--v4v-housing))] bg-[hsl(var(--v4v-housing)/0.04)]',
  legal: 'border-l-[hsl(var(--v4v-legal))] bg-[hsl(var(--v4v-legal)/0.04)]',
  food: 'border-l-[hsl(var(--v4v-food))] bg-[hsl(var(--v4v-food)/0.04)]',
  benefits: 'border-l-[hsl(var(--v4v-benefits))] bg-[hsl(var(--v4v-benefits)/0.04)]',
  mentalHealth: 'border-l-[hsl(var(--v4v-mentalHealth))] bg-[hsl(var(--v4v-mentalHealth)/0.04)]',
  supportServices: 'border-l-[hsl(var(--v4v-supportServices))] bg-[hsl(var(--v4v-supportServices)/0.04)]',
  healthcare: 'border-l-[hsl(var(--v4v-healthcare))] bg-[hsl(var(--v4v-healthcare)/0.04)]',
  education: 'border-l-[hsl(var(--v4v-education))] bg-[hsl(var(--v4v-education)/0.04)]',
  financial: 'border-l-[hsl(var(--v4v-financial))] bg-[hsl(var(--v4v-financial)/0.04)]',
  family: 'border-l-[hsl(var(--v4v-family))] bg-[hsl(var(--v4v-family)/0.04)]',
};

const categoryIconBg: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.1)]',
  training: 'bg-[hsl(var(--v4v-training)/0.1)]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.1)]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.1)]',
  food: 'bg-[hsl(var(--v4v-food)/0.1)]',
  benefits: 'bg-[hsl(var(--v4v-benefits)/0.1)]',
  mentalHealth: 'bg-[hsl(var(--v4v-mentalHealth)/0.1)]',
  supportServices: 'bg-[hsl(var(--v4v-supportServices)/0.1)]',
  healthcare: 'bg-[hsl(var(--v4v-healthcare)/0.1)]',
  education: 'bg-[hsl(var(--v4v-education)/0.1)]',
  financial: 'bg-[hsl(var(--v4v-financial)/0.1)]',
  family: 'bg-[hsl(var(--v4v-family)/0.1)]',
};

interface CollapsibleSectionProps {
  title: string;
  badge?: React.ReactNode;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function CollapsibleSection({
  title,
  badge,
  isOpen,
  onToggle,
  children,
}: CollapsibleSectionProps) {
  return (
    <div>
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full min-h-[32px] items-center justify-between py-1.5 text-left"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-medium">{title}</h4>
          {badge}
        </div>
        <ChevronDown
          className={cn(
            'h-4 w-4 text-muted-foreground transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
        />
      </button>
      <div
        className={cn(
          'grid transition-all duration-200 ease-in-out',
          isOpen ? 'mt-2 grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        )}
      >
        <div className="overflow-hidden">{children}</div>
      </div>
    </div>
  );
}

interface CategoryWithTagsProps {
  category: typeof CATEGORIES[number];
  isSelected: boolean;
  isTagsExpanded: boolean;
  selectedTags: string[];
  onTagsToggle: () => void;
  onTagToggle: (tagId: string) => void;
  // Filters for dynamic tag loading
  filterContext?: {
    states?: string[];
    zip?: string;
    radius?: number;
    scope?: string;
  };
}

function CategoryWithTags({
  category,
  isSelected,
  isTagsExpanded,
  selectedTags,
  onTagsToggle,
  onTagToggle,
  filterContext,
}: CategoryWithTagsProps) {
  const Icon = category.icon;

  // Check if we have active filters that should trigger empty tag filtering
  const hasActiveFilters = Boolean(
    filterContext?.states?.length || filterContext?.zip || filterContext?.scope
  );

  // Fetch tags for this category when expanded, filtering out empty tags if filters are active
  const { data: categoryTags, isLoading } = useQuery({
    queryKey: ['taxonomy', 'tags', category.value, filterContext?.states, filterContext?.zip, filterContext?.scope],
    queryFn: () => api.taxonomy.getCategoryTags(category.value, {
      states: filterContext?.states,
      zip: filterContext?.zip,
      radius: filterContext?.radius,
      scope: filterContext?.scope,
      filterEmpty: hasActiveFilters,
    }),
    staleTime: 1000 * 60 * 5, // Cache for 5 min when filtering (shorter since it depends on filters)
    enabled: isSelected && isTagsExpanded,
  });

  // Count selected tags in this category
  const selectedTagCount = useMemo(() => {
    if (!categoryTags) return 0;
    const categoryTagIds = categoryTags.flat_tags.map((t) => t.id);
    return selectedTags.filter((tagId) => categoryTagIds.includes(tagId)).length;
  }, [categoryTags, selectedTags]);

  return (
    <div>
      <div
        className={cn(
          'flex min-h-[36px] items-center space-x-2 rounded-lg border-l-2 px-2 transition-all duration-200',
          isSelected
            ? categoryAccents[category.value]
            : 'border-l-transparent hover:bg-muted/50'
        )}
      >
        <RadioGroupItem
          value={category.value}
          id={`category-${category.value}`}
          className={isSelected ? categoryColors[category.value] : ''}
        />
        <Label
          htmlFor={`category-${category.value}`}
          className={cn(
            'flex flex-1 min-h-[36px] cursor-pointer items-center gap-2 text-sm',
            isSelected ? categoryColors[category.value] : ''
          )}
        >
          <span className={cn(
            'flex h-5 w-5 items-center justify-center rounded-md transition-colors',
            isSelected ? categoryIconBg[category.value] : 'bg-muted/50'
          )}>
            <Icon className="h-3 w-3" />
          </span>
          {category.label}
        </Label>
        {/* Tag expand button - only show when category is selected */}
        {isSelected && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              onTagsToggle();
            }}
            className={cn(
              'flex items-center gap-1 rounded px-1.5 py-0.5 text-xs transition-colors',
              isTagsExpanded
                ? 'bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold-dark))]'
                : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
            )}
          >
            <Tag className="h-3 w-3" />
            {selectedTagCount > 0 && (
              <span className="font-medium">{selectedTagCount}</span>
            )}
            <ChevronDown
              className={cn(
                'h-3 w-3 transition-transform duration-200',
                isTagsExpanded && 'rotate-180'
              )}
            />
          </button>
        )}
      </div>

      {/* Expandable tag section */}
      {isSelected && (
        <div
          className={cn(
            'grid transition-all duration-200 ease-in-out',
            isTagsExpanded
              ? 'grid-rows-[1fr] opacity-100'
              : 'grid-rows-[0fr] opacity-0'
          )}
        >
          <div className="overflow-hidden">
            <div className={cn(
              'ml-6 mt-2 mb-2 rounded-lg border-l-2 pl-3 py-2',
              categoryAccents[category.value]
            )}>
              {isLoading ? (
                <div className="flex flex-wrap gap-1.5">
                  <Skeleton className="h-6 w-16" />
                  <Skeleton className="h-6 w-20" />
                  <Skeleton className="h-6 w-14" />
                </div>
              ) : categoryTags ? (
                <div className="space-y-3">
                  {categoryTags.groups.map((group) => (
                    <div key={group.group}>
                      <div className="text-[10px] font-medium text-muted-foreground mb-1.5 uppercase tracking-wide">
                        {group.group.replace(/_/g, ' ')}
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {group.tags.map((tag) => {
                          const isTagSelected = selectedTags.includes(tag.id);
                          return (
                            <button
                              key={tag.id}
                              type="button"
                              onClick={() => onTagToggle(tag.id)}
                              className={cn(
                                'inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] transition-all text-foreground',
                                isTagSelected
                                  ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.15)] font-medium'
                                  : 'border-border bg-background hover:bg-muted/50'
                              )}
                            >
                              <span
                                className={cn(
                                  'flex h-2.5 w-2.5 items-center justify-center rounded-sm border',
                                  isTagSelected
                                    ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold))]'
                                    : 'border-input bg-background'
                                )}
                              >
                                {isTagSelected && <Check className="h-1.5 w-1.5 text-white" />}
                              </span>
                              {tag.name}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-muted-foreground">No tags available</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function FiltersSidebar({
  filters,
  onFiltersChange,
  resultCount,
  hideHeader = false,
  sort,
  onSortChange,
  hasQuery = false,
  hasZip = false,
}: FiltersSidebarProps) {
  // Collapsible section state - categories open by default
  // States section opens if states are pre-selected (e.g., from landing page URL)
  const [categoriesOpen, setCategoriesOpen] = useState(true);
  const [zipOpen, setZipOpen] = useState(filters.zip ? true : false);
  const [statesOpen, setStatesOpen] = useState(filters.states.length > 0);
  const [stateSearch, setStateSearch] = useState('');
  // Track which categories have expanded tag sections
  const [expandedCategoryTags, setExpandedCategoryTags] = useState<Set<string>>(
    new Set()
  );

  // Auto-expand states section when states are pre-selected (e.g., from URL navigation)
  useEffect(() => {
    if (filters.states.length > 0 && !statesOpen) {
      setStatesOpen(true);
    }
  }, [filters.states.length]); // eslint-disable-line react-hooks/exhaustive-deps

  // Clear state search when section collapses
  const handleStatesToggle = () => {
    if (statesOpen) {
      setStateSearch('');
    }
    setStatesOpen(!statesOpen);
  };

  // Filter states based on search query
  const filteredStates = STATES.filter((state) =>
    state.label.toLowerCase().includes(stateSearch.toLowerCase()) ||
    state.value.toLowerCase().includes(stateSearch.toLowerCase())
  );

  // Count location as 1 if either zip OR geolocation is active (they're mutually exclusive)
  const hasLocation = filters.zip || (filters.lat !== undefined && filters.lng !== undefined);
  const activeFilterCount =
    filters.categories.length +
    filters.states.length +
    (filters.scope !== 'all' ? 1 : 0) +
    (hasLocation ? 1 : 0) +
    (filters.tags?.length ?? 0);

  // Single-select category handler - clears tags when category changes
  const handleCategoryChange = (category: string) => {
    // If selecting the same category, deselect it (allow "no category" state)
    const currentCategory = filters.categories[0];
    if (category === currentCategory) {
      // Clear category and tags
      onFiltersChange({ ...filters, categories: [], tags: [] });
    } else {
      // Change category and clear tags (tags are category-specific)
      onFiltersChange({ ...filters, categories: [category], tags: [] });
    }
    // Collapse any expanded tag sections when category changes
    setExpandedCategoryTags(new Set());
  };

  const handleStateToggle = (state: string) => {
    const newStates = filters.states.includes(state)
      ? filters.states.filter((s) => s !== state)
      : [...filters.states, state];
    onFiltersChange({ ...filters, states: newStates });
  };

  const handleZipChange = (zip: string) => {
    // When ZIP is entered, clear states and geolocation since ZIP is more specific
    onFiltersChange({
      ...filters,
      zip: zip || undefined,
      lat: undefined,
      lng: undefined,
      states: zip ? [] : filters.states,
    });
  };

  const handleRadiusChange = (radius: number) => {
    onFiltersChange({ ...filters, radius });
  };

  const handleGeolocation = (lat: number, lng: number) => {
    // When using geolocation, clear zip and states
    onFiltersChange({
      ...filters,
      lat,
      lng,
      zip: undefined,
      states: [],
    });
  };

  const handleClearZip = () => {
    onFiltersChange({ ...filters, zip: undefined, radius: undefined, lat: undefined, lng: undefined });
  };

  const handleTagsChange = (newTags: string[]) => {
    const newFilters = { ...filters, tags: newTags };
    onFiltersChange(newFilters);
  };

  const toggleCategoryTags = (categoryValue: string) => {
    setExpandedCategoryTags((prev) => {
      const next = new Set(prev);
      if (next.has(categoryValue)) {
        next.delete(categoryValue);
      } else {
        next.add(categoryValue);
      }
      return next;
    });
  };

  const toggleTag = (tagId: string) => {
    const newTags = (filters.tags || []).includes(tagId)
      ? (filters.tags || []).filter((t) => t !== tagId)
      : [...(filters.tags || []), tagId];
    handleTagsChange(newTags);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      categories: [],
      states: [],
      scope: 'all',
      minTrust: 0, // Keep for API compatibility
      zip: undefined,
      radius: undefined,
      lat: undefined,
      lng: undefined,
      tags: [],
    });
  };

  // Filter sort options based on context
  const availableSortOptions = SORT_OPTIONS.filter((opt) => {
    if (opt.value === 'relevance' && !hasQuery) return false;
    if (opt.value === 'distance' && !hasZip) return false;
    return true;
  });

  return (
    <div className="space-y-3 pb-8">
      {/* Header - can be hidden when parent provides its own */}
      {!hideHeader && (
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Filter className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
            Filters
          </h3>
          {resultCount !== undefined && (
            <Badge variant="secondary" className="text-xs">
              {resultCount} results
            </Badge>
          )}
        </div>
      )}

      {/* Sort section - only shown on mobile when props provided */}
      {sort && onSortChange && (
        <>
          <div className="space-y-2">
            <h4 className="flex items-center gap-2 text-sm font-medium">
              <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
              Sort by
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {availableSortOptions.map((option) => {
                const isSelected = sort === option.value;
                const Icon = option.icon;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => onSortChange(option.value)}
                    className={cn(
                      'inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-all',
                      isSelected
                        ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold-dark))] font-medium'
                        : 'border-border bg-background hover:bg-muted/50'
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {option.label}
                  </button>
                );
              })}
            </div>
          </div>
          <Separator />
        </>
      )}

      <Button
        variant="ghost"
        size="sm"
        onClick={clearAllFilters}
        className={cn(
          'h-auto w-full justify-start px-0 py-0.5 text-sm text-muted-foreground hover:text-foreground',
          activeFilterCount === 0 && 'invisible'
        )}
      >
        <X className="mr-1 h-3 w-3" />
        Clear all ({activeFilterCount})
      </Button>

      <Separator />

      {/* Categories - Single Select */}
      <CollapsibleSection
        title="Category"
        badge={
          filters.categories.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {CATEGORIES.find((c) => c.value === filters.categories[0])?.label}
            </Badge>
          )
        }
        isOpen={categoriesOpen}
        onToggle={() => setCategoriesOpen(!categoriesOpen)}
      >
        <RadioGroup
          value={filters.categories[0] || ''}
          onValueChange={handleCategoryChange}
          className="space-y-1"
        >
          {CATEGORIES.map((category) => {
            const isSelected = filters.categories[0] === category.value;
            const isTagsExpanded = expandedCategoryTags.has(category.value);
            return (
              <CategoryWithTags
                key={category.value}
                category={category}
                isSelected={isSelected}
                isTagsExpanded={isTagsExpanded}
                selectedTags={filters.tags || []}
                onTagsToggle={() => toggleCategoryTags(category.value)}
                onTagToggle={toggleTag}
                filterContext={{
                  states: filters.states,
                  zip: filters.zip,
                  radius: filters.radius,
                  scope: filters.scope,
                }}
              />
            );
          })}
        </RadioGroup>
      </CollapsibleSection>

      <Separator />


      {/* Near ZIP / Location - location-based search */}
      <CollapsibleSection
        title="Location"
        badge={
          (filters.zip || (filters.lat !== undefined && filters.lng !== undefined)) && (
            <Badge variant="outline" className="text-xs">
              {filters.zip ? filters.zip : 'GPS'}
            </Badge>
          )
        }
        isOpen={zipOpen}
        onToggle={() => setZipOpen(!zipOpen)}
      >
        <div className="space-y-3">
          <ZipCodeInput
            zip={filters.zip || ''}
            radius={filters.radius || 100}
            onZipChange={handleZipChange}
            onRadiusChange={handleRadiusChange}
            onGeolocation={handleGeolocation}
            onClear={handleClearZip}
            showGeolocation
            isUsingGeolocation={filters.lat !== undefined && filters.lng !== undefined}
            compact
          />
          <p className="text-xs text-muted-foreground">
            Find resources closest to you. Results show distance and sort by proximity.
          </p>
        </div>
      </CollapsibleSection>

      <Separator />

      {/* States - at bottom since it's the longest list */}
      <CollapsibleSection
        title="States"
        badge={
          filters.states.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {filters.states.length}
            </Badge>
          )
        }
        isOpen={statesOpen}
        onToggle={handleStatesToggle}
      >
        {/* Selected states as removable chips */}
        {filters.states.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-1.5">
            {filters.states.map((stateCode) => {
              const stateInfo = STATES.find((s) => s.value === stateCode);
              return (
                <Badge
                  key={stateCode}
                  variant="secondary"
                  className="gap-1 pl-2 pr-1 py-1 bg-[hsl(var(--v4v-navy)/0.1)] text-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.2)] cursor-pointer"
                  onClick={() => handleStateToggle(stateCode)}
                >
                  {stateInfo?.label || stateCode}
                  <X className="h-3 w-3 ml-0.5" />
                </Badge>
              );
            })}
          </div>
        )}

        {/* State search input */}
        <div className="relative mb-2">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search states..."
            value={stateSearch}
            onChange={(e) => setStateSearch(e.target.value)}
            className="h-9 pl-8 text-sm bg-muted/50"
          />
        </div>
        <ScrollArea className="h-48 rounded-lg border bg-card/50 p-2">
          <div className="space-y-0.5">
            {filteredStates.length === 0 ? (
              <div className="flex items-center justify-center h-20 text-sm text-muted-foreground">
                No states match &ldquo;{stateSearch}&rdquo;
              </div>
            ) : (
              filteredStates.map((state) => {
                const isChecked = filters.states.includes(state.value);
                return (
                  <div
                    key={state.value}
                    className={cn(
                      'flex min-h-[44px] items-center space-x-2 rounded-md border-l-2 px-2 transition-all duration-200',
                      isChecked
                        ? 'border-l-[hsl(var(--v4v-navy))] bg-[hsl(var(--v4v-navy)/0.06)]'
                        : 'border-l-transparent hover:bg-muted/50'
                    )}
                  >
                    <Checkbox
                      id={`state-${state.value}`}
                      checked={isChecked}
                      onCheckedChange={() => handleStateToggle(state.value)}
                    />
                    <Label
                      htmlFor={`state-${state.value}`}
                      className={cn(
                        'flex flex-1 min-h-[44px] cursor-pointer items-center text-sm',
                        isChecked && 'font-medium text-[hsl(var(--v4v-navy))]'
                      )}
                    >
                      {state.label}
                    </Label>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>
      </CollapsibleSection>
    </div>
  );
}

// Icon mapping for collapsed state with category colors
const FILTER_ICONS = [
  {
    key: 'filter',
    icon: Filter,
    label: 'Filters',
    color: 'text-[hsl(var(--v4v-gold))]',
    bg: 'bg-[hsl(var(--v4v-gold)/0.1)]',
  },
  {
    key: 'employment',
    icon: Briefcase,
    label: 'Employment',
    color: 'text-[hsl(var(--v4v-employment))]',
    bg: 'bg-[hsl(var(--v4v-employment)/0.1)]',
  },
  {
    key: 'training',
    icon: GraduationCap,
    label: 'Training',
    color: 'text-[hsl(var(--v4v-training))]',
    bg: 'bg-[hsl(var(--v4v-training)/0.1)]',
  },
  {
    key: 'housing',
    icon: Home,
    label: 'Housing',
    color: 'text-[hsl(var(--v4v-housing))]',
    bg: 'bg-[hsl(var(--v4v-housing)/0.1)]',
  },
  {
    key: 'legal',
    icon: Scale,
    label: 'Legal',
    color: 'text-[hsl(var(--v4v-legal))]',
    bg: 'bg-[hsl(var(--v4v-legal)/0.1)]',
  },
  {
    key: 'food',
    icon: UtensilsCrossed,
    label: 'Food',
    color: 'text-[hsl(var(--v4v-food))]',
    bg: 'bg-[hsl(var(--v4v-food)/0.1)]',
  },
  {
    key: 'benefits',
    icon: FileCheck,
    label: 'Benefits',
    color: 'text-[hsl(var(--v4v-benefits))]',
    bg: 'bg-[hsl(var(--v4v-benefits)/0.1)]',
  },
  {
    key: 'mentalHealth',
    icon: Brain,
    label: 'Mental Health',
    color: 'text-[hsl(var(--v4v-mentalHealth))]',
    bg: 'bg-[hsl(var(--v4v-mentalHealth)/0.1)]',
  },
  {
    key: 'supportServices',
    icon: HeartHandshake,
    label: 'Support',
    color: 'text-[hsl(var(--v4v-supportServices))]',
    bg: 'bg-[hsl(var(--v4v-supportServices)/0.1)]',
  },
  {
    key: 'healthcare',
    icon: HeartPulse,
    label: 'Healthcare',
    color: 'text-[hsl(var(--v4v-healthcare))]',
    bg: 'bg-[hsl(var(--v4v-healthcare)/0.1)]',
  },
  {
    key: 'education',
    icon: School,
    label: 'Education',
    color: 'text-[hsl(var(--v4v-education))]',
    bg: 'bg-[hsl(var(--v4v-education)/0.1)]',
  },
  {
    key: 'financial',
    icon: Wallet,
    label: 'Financial',
    color: 'text-[hsl(var(--v4v-financial))]',
    bg: 'bg-[hsl(var(--v4v-financial)/0.1)]',
  },
  {
    key: 'family',
    icon: Users,
    label: 'Family',
    color: 'text-[hsl(var(--v4v-family))]',
    bg: 'bg-[hsl(var(--v4v-family)/0.1)]',
  },
] as const;

interface FixedFiltersSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  resultCount?: number;
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
}

export function FixedFiltersSidebar({
  filters,
  onFiltersChange,
  resultCount,
  isCollapsed,
  onCollapsedChange,
}: FixedFiltersSidebarProps) {
  // Persist collapsed state to localStorage
  const toggleCollapsed = () => {
    const newValue = !isCollapsed;
    onCollapsedChange(newValue);
    localStorage.setItem('v4v-filters-collapsed', String(newValue));
  };

  // Count location as 1 if either zip OR geolocation is active (they're mutually exclusive)
  const hasLocationFixed = filters.zip || (filters.lat !== undefined && filters.lng !== undefined);
  const activeFilterCount =
    filters.categories.length +
    filters.states.length +
    (filters.scope !== 'all' ? 1 : 0) +
    (hasLocationFixed ? 1 : 0) +
    (filters.tags?.length ?? 0);

  return (
    <TooltipProvider>
      {/* Spacer div - always collapsed width since expanded overlays */}
      <div className="hidden w-12 flex-shrink-0 lg:block" />

      {/* Fixed sidebar */}
      <AnimatePresence mode="wait">
        {isCollapsed ? (
          <motion.div
            key="collapsed"
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 48, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="sidebar-gradient fixed left-0 top-16 z-30 hidden h-[calc(100vh-64px)] flex-shrink-0 flex-col items-center border-r py-3 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-background/90 lg:flex"
          >
            {/* Top row: Filters icon + Expand icon */}
            <div className="flex flex-col items-center gap-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleCollapsed}
                    className="h-8 w-8 rounded-lg bg-[hsl(var(--v4v-gold)/0.1)] text-[hsl(var(--v4v-gold))] hover:bg-[hsl(var(--v4v-gold)/0.2)]"
                  >
                    <Filter className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p className="text-xs">Filters</p>
                </TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleCollapsed}
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                  >
                    <PanelLeft className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p className="text-xs">Expand filters</p>
                </TooltipContent>
              </Tooltip>
            </div>

            {/* Clear all filters button */}
            {activeFilterCount > 0 && (
              <>
                <div className="my-2 h-px w-6 bg-border" />
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onFiltersChange({ categories: [], states: [], scope: 'all', minTrust: 0, zip: undefined, radius: undefined, lat: undefined, lng: undefined })}
                      className="h-8 w-8 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p className="text-xs">Clear all filters ({activeFilterCount})</p>
                  </TooltipContent>
                </Tooltip>
              </>
            )}

            {/* Location indicator (zip code or geolocation) */}
            {(filters.zip || (filters.lat !== undefined && filters.lng !== undefined)) && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-2"
              >
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onFiltersChange({ ...filters, zip: undefined, radius: undefined, lat: undefined, lng: undefined })}
                      className="h-8 w-8 rounded-lg bg-[hsl(var(--v4v-gold)/0.1)] text-[hsl(var(--v4v-gold))] shadow-sm border-2 border-current"
                    >
                      <MapPin className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p className="text-xs">
                      {filters.zip
                        ? `Near ${filters.zip} (${filters.radius || 100} mi) - Click to clear`
                        : `Using GPS location (${filters.radius || 100} mi) - Click to clear`
                      }
                    </p>
                  </TooltipContent>
                </Tooltip>
              </motion.div>
            )}

            <div className="my-2 h-px w-6 bg-border" />

            {/* Category filter icons - single select */}
            {FILTER_ICONS.filter(item => item.key !== 'filter').map((item, index) => {
              const isActive = filters.categories[0] === item.key;

              const handleClick = () => {
                // Single-select: toggle off if clicking same category, otherwise switch
                if (isActive) {
                  onFiltersChange({ ...filters, categories: [], tags: [] });
                } else {
                  onFiltersChange({ ...filters, categories: [item.key], tags: [] });
                }
              };

              return (
                <motion.div
                  key={item.key}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="mb-1"
                >
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleClick}
                        className={cn(
                          'h-8 w-8 rounded-lg transition-all hover:scale-105',
                          isActive
                            ? cn(item.bg, item.color, 'shadow-sm border-2 border-current')
                            : 'bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground'
                        )}
                      >
                        <item.icon className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      <p className="text-xs">{isActive ? 'Clear' : 'Filter by'} {item.label}</p>
                    </TooltipContent>
                  </Tooltip>
                </motion.div>
              );
            })}
          </motion.div>
        ) : (
          <motion.aside
            key="expanded"
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="sidebar-gradient fixed left-0 top-16 z-30 hidden h-[calc(100vh-64px)] flex-shrink-0 flex-col overflow-hidden border-r shadow-sm backdrop-blur supports-[backdrop-filter]:bg-background/90 lg:flex"
          >
            {/* Header with Collapse Button */}
            <div className="sidebar-header-accent flex flex-none items-center justify-between px-4 py-3">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
                <span className="text-sm font-semibold">Filters</span>
              </div>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleCollapsed}
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                  >
                    <PanelLeftClose className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p className="text-xs">Collapse filters</p>
                </TooltipContent>
              </Tooltip>
            </div>

            {/* Filter Content - min-h-0 is critical for flex scrolling */}
            <ScrollArea className="min-h-0 flex-1 px-4 py-4">
              <FiltersSidebar
                filters={filters}
                onFiltersChange={onFiltersChange}
                resultCount={resultCount}
                hideHeader
              />
            </ScrollArea>
          </motion.aside>
        )}
      </AnimatePresence>
    </TooltipProvider>
  );
}
