'use client';

import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Check, ChevronDown, X, Tag } from 'lucide-react';
import { cn } from '@/lib/utils';
import api, { type CategoryTags, type TagGroup } from '@/lib/api';

interface TagFilterSidebarProps {
  /** Currently selected tags */
  selectedTags: string[];
  /** Callback when tags change */
  onTagsChange: (tags: string[]) => void;
  /** Currently selected categories (to highlight relevant tag groups) */
  selectedCategories?: string[];
  /** Whether to show in compact mode */
  compact?: boolean;
  /** Hide header */
  hideHeader?: boolean;
}

/**
 * Tree-style collapsible tag filter sidebar.
 * Categories are expandable sections containing tag groups with checkboxes.
 */
export function TagFilterSidebar({
  selectedTags,
  onTagsChange,
  selectedCategories = [],
  compact = false,
  hideHeader = false,
}: TagFilterSidebarProps) {
  // Fetch taxonomy data
  const { data: taxonomy, isLoading, error } = useQuery({
    queryKey: ['taxonomy', 'tags'],
    queryFn: () => api.taxonomy.getTags(),
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  });

  // Track which categories are expanded
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set()
  );

  // Auto-expand categories that have selected tags or are in selectedCategories
  useEffect(() => {
    if (!taxonomy) return;

    const newExpanded = new Set<string>();

    // Expand categories with selected tags
    for (const category of taxonomy.categories) {
      const categoryTagIds = category.groups.flatMap((g) =>
        g.tags.map((t) => t.id)
      );
      const hasSelectedTag = categoryTagIds.some((tagId) =>
        selectedTags.includes(tagId)
      );
      if (hasSelectedTag || selectedCategories.includes(category.category_id)) {
        newExpanded.add(category.category_id);
      }
    }

    if (newExpanded.size > 0) {
      setExpandedCategories((prev) => new Set([...prev, ...newExpanded]));
    }
  }, [taxonomy, selectedTags, selectedCategories]);

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(categoryId)) {
        next.delete(categoryId);
      } else {
        next.add(categoryId);
      }
      return next;
    });
  };

  const toggleTag = (tagId: string) => {
    const newTags = selectedTags.includes(tagId)
      ? selectedTags.filter((t) => t !== tagId)
      : [...selectedTags, tagId];
    onTagsChange(newTags);
  };

  const clearAllTags = () => {
    onTagsChange([]);
  };

  // Get selected tag names for display
  const selectedTagNames = useMemo(() => {
    if (!taxonomy) return new Map<string, string>();
    const nameMap = new Map<string, string>();
    for (const category of taxonomy.categories) {
      for (const group of category.groups) {
        for (const tag of group.tags) {
          if (selectedTags.includes(tag.id)) {
            nameMap.set(tag.id, tag.name);
          }
        }
      }
    }
    return nameMap;
  }, [taxonomy, selectedTags]);

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    );
  }

  if (error || !taxonomy) {
    return (
      <div className="text-sm text-muted-foreground">
        Unable to load tag filters.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      {!hideHeader && (
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Tag className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
            Eligibility Tags
          </h3>
          {selectedTags.length > 0 && (
            <Badge variant="secondary" className="text-xs">
              {selectedTags.length} selected
            </Badge>
          )}
        </div>
      )}

      {/* Selected tags as removable chips */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selectedTags.map((tagId) => (
            <Badge
              key={tagId}
              variant="secondary"
              className="gap-1 pl-2 pr-1 py-1 bg-[hsl(var(--v4v-gold)/0.1)] text-[hsl(var(--v4v-gold-dark))] hover:bg-[hsl(var(--v4v-gold)/0.2)] cursor-pointer"
              onClick={() => toggleTag(tagId)}
            >
              {selectedTagNames.get(tagId) || tagId}
              <X className="h-3 w-3 ml-0.5" />
            </Badge>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllTags}
            className="h-6 px-2 text-xs text-muted-foreground hover:text-foreground"
          >
            Clear all
          </Button>
        </div>
      )}

      {/* Category sections */}
      <ScrollArea className={compact ? 'h-64' : 'h-auto max-h-96'}>
        <div className="space-y-1 pr-2">
          {taxonomy.categories.map((category) => (
            <CategorySection
              key={category.category_id}
              category={category}
              isExpanded={expandedCategories.has(category.category_id)}
              onToggle={() => toggleCategory(category.category_id)}
              selectedTags={selectedTags}
              onTagToggle={toggleTag}
              isHighlighted={selectedCategories.includes(category.category_id)}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

interface CategorySectionProps {
  category: CategoryTags;
  isExpanded: boolean;
  onToggle: () => void;
  selectedTags: string[];
  onTagToggle: (tagId: string) => void;
  isHighlighted: boolean;
}

function CategorySection({
  category,
  isExpanded,
  onToggle,
  selectedTags,
  onTagToggle,
  isHighlighted,
}: CategorySectionProps) {
  // Count selected tags in this category
  const selectedCount = category.groups
    .flatMap((g) => g.tags)
    .filter((t) => selectedTags.includes(t.id)).length;

  return (
    <div
      className={cn(
        'rounded-lg border transition-colors',
        isHighlighted
          ? 'border-[hsl(var(--v4v-gold)/0.3)] bg-[hsl(var(--v4v-gold)/0.02)]'
          : 'border-transparent'
      )}
    >
      {/* Category header */}
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-muted/50 rounded-lg transition-colors"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <ChevronDown
            className={cn(
              'h-4 w-4 text-muted-foreground transition-transform duration-200',
              isExpanded && 'rotate-180'
            )}
          />
          <span className="text-sm font-medium">{category.category_name}</span>
          {selectedCount > 0 && (
            <Badge
              variant="secondary"
              className="h-5 px-1.5 text-xs bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold-dark))]"
            >
              {selectedCount}
            </Badge>
          )}
        </div>
      </button>

      {/* Expandable content */}
      <div
        className={cn(
          'grid transition-all duration-200 ease-in-out',
          isExpanded
            ? 'grid-rows-[1fr] opacity-100'
            : 'grid-rows-[0fr] opacity-0'
        )}
      >
        <div className="overflow-hidden">
          <div className="px-3 pb-3 pt-1 space-y-3">
            {category.groups.map((group) => (
              <TagGroupSection
                key={group.group}
                group={group}
                selectedTags={selectedTags}
                onTagToggle={onTagToggle}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

interface TagGroupSectionProps {
  group: TagGroup;
  selectedTags: string[];
  onTagToggle: (tagId: string) => void;
}

function TagGroupSection({
  group,
  selectedTags,
  onTagToggle,
}: TagGroupSectionProps) {
  // Convert group name to display name
  const groupDisplayName = group.group
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());

  return (
    <div>
      <div className="text-xs font-medium text-muted-foreground mb-1.5 uppercase tracking-wide">
        {groupDisplayName}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {group.tags.map((tag) => {
          const isSelected = selectedTags.includes(tag.id);
          return (
            <div
              key={tag.id}
              role="button"
              tabIndex={0}
              onClick={() => onTagToggle(tag.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onTagToggle(tag.id);
                }
              }}
              className={cn(
                'inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs transition-all cursor-pointer select-none',
                isSelected
                  ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.1)] text-[hsl(var(--v4v-gold-dark))] font-medium'
                  : 'border-border bg-background hover:bg-muted/50 text-foreground'
              )}
            >
              <span
                className={cn(
                  'flex h-3 w-3 items-center justify-center rounded-sm border',
                  isSelected
                    ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold))]'
                    : 'border-input bg-background'
                )}
              >
                {isSelected && <Check className="h-2 w-2 text-white" />}
              </span>
              {tag.name}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TagFilterSidebar;
