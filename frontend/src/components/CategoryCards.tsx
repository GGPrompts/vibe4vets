'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Briefcase, GraduationCap, Home as HomeIcon, Scale, UtensilsCrossed, FileCheck, Brain, HeartHandshake, HeartPulse, School, Wallet, Users, Check, ChevronDown, Tag } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import api from '@/lib/api';

const categories = [
  {
    name: 'Employment',
    slug: 'employment',
    description: 'Job placement, career services, and Veteran-friendly employers',
    icon: Briefcase,
    colorClass: 'bg-v4v-employment',
    mutedBgClass: 'bg-v4v-employment-muted',
    textClass: 'text-v4v-employment',
    borderClass: 'border-[hsl(var(--v4v-employment))]',
  },
  {
    name: 'Training',
    slug: 'training',
    description: 'Vocational rehabilitation, certifications, and skill-building programs',
    icon: GraduationCap,
    colorClass: 'bg-v4v-training',
    mutedBgClass: 'bg-v4v-training-muted',
    textClass: 'text-v4v-training',
    borderClass: 'border-[hsl(var(--v4v-training))]',
  },
  {
    name: 'Housing',
    slug: 'housing',
    description: 'HUD-VASH, SSVF, transitional housing, and shelter resources',
    icon: HomeIcon,
    colorClass: 'bg-v4v-housing',
    mutedBgClass: 'bg-v4v-housing-muted',
    textClass: 'text-v4v-housing',
    borderClass: 'border-[hsl(var(--v4v-housing))]',
  },
  {
    name: 'Legal',
    slug: 'legal',
    description: 'Legal aid, VA appeals assistance, and advocacy services',
    icon: Scale,
    colorClass: 'bg-v4v-legal',
    mutedBgClass: 'bg-v4v-legal-muted',
    textClass: 'text-v4v-legal',
    borderClass: 'border-[hsl(var(--v4v-legal))]',
  },
  {
    name: 'Food',
    slug: 'food',
    description: 'Food pantries, meal programs, and emergency food assistance',
    icon: UtensilsCrossed,
    colorClass: 'bg-v4v-food',
    mutedBgClass: 'bg-v4v-food-muted',
    textClass: 'text-v4v-food',
    borderClass: 'border-[hsl(var(--v4v-food))]',
  },
  {
    name: 'Benefits',
    slug: 'benefits',
    description: 'VA claims assistance, benefits counseling, and VSO services',
    icon: FileCheck,
    colorClass: 'bg-v4v-benefits',
    mutedBgClass: 'bg-v4v-benefits-muted',
    textClass: 'text-v4v-benefits',
    borderClass: 'border-[hsl(var(--v4v-benefits))]',
  },
  {
    name: 'Mental Health',
    slug: 'mentalHealth',
    description: 'Counseling, PTSD support, crisis services, and mental wellness programs',
    icon: Brain,
    colorClass: 'bg-v4v-mentalHealth',
    mutedBgClass: 'bg-v4v-mentalHealth-muted',
    textClass: 'text-v4v-mentalHealth',
    borderClass: 'border-[hsl(var(--v4v-mentalHealth))]',
  },
  {
    name: 'Support Services',
    slug: 'supportServices',
    description: 'General Veteran support, peer mentoring, and case management',
    icon: HeartHandshake,
    colorClass: 'bg-v4v-supportServices',
    mutedBgClass: 'bg-v4v-supportServices-muted',
    textClass: 'text-v4v-supportServices',
    borderClass: 'border-[hsl(var(--v4v-supportServices))]',
  },
  {
    name: 'Healthcare',
    slug: 'healthcare',
    description: 'Medical care, VA health services, and wellness programs',
    icon: HeartPulse,
    colorClass: 'bg-v4v-healthcare',
    mutedBgClass: 'bg-v4v-healthcare-muted',
    textClass: 'text-v4v-healthcare',
    borderClass: 'border-[hsl(var(--v4v-healthcare))]',
  },
  {
    name: 'Education',
    slug: 'education',
    description: 'College programs, scholarships, and academic support',
    icon: School,
    colorClass: 'bg-v4v-education',
    mutedBgClass: 'bg-v4v-education-muted',
    textClass: 'text-v4v-education',
    borderClass: 'border-[hsl(var(--v4v-education))]',
  },
  {
    name: 'Financial',
    slug: 'financial',
    description: 'Financial counseling, emergency assistance, and debt relief',
    icon: Wallet,
    colorClass: 'bg-v4v-financial',
    mutedBgClass: 'bg-v4v-financial-muted',
    textClass: 'text-v4v-financial',
    borderClass: 'border-[hsl(var(--v4v-financial))]',
  },
  {
    name: 'Family',
    slug: 'family',
    description: 'Resources for spouses, dependents, survivors, and childcare support',
    icon: Users,
    colorClass: 'bg-v4v-family',
    mutedBgClass: 'bg-v4v-family-muted',
    textClass: 'text-v4v-family',
    borderClass: 'border-[hsl(var(--v4v-family))]',
  },
];

interface CategoryCardsProps {
  selectedCategories: string[];
  onToggleCategory: (category: string) => void;
  /** Selected eligibility tags */
  selectedTags?: string[];
  /** Callback when tags change */
  onTagsChange?: (tags: string[]) => void;
  /** Enable tag expansion on card click */
  enableTagExpansion?: boolean;
}

export function CategoryCards({
  selectedCategories,
  onToggleCategory,
  selectedTags = [],
  onTagsChange,
  enableTagExpansion = false,
}: CategoryCardsProps) {
  // Track which category card is expanded
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

  const handleCardClick = (categorySlug: string) => {
    if (enableTagExpansion) {
      // Toggle expansion
      if (expandedCategory === categorySlug) {
        setExpandedCategory(null);
      } else {
        setExpandedCategory(categorySlug);
        // Also select the category when expanding
        if (!selectedCategories.includes(categorySlug)) {
          onToggleCategory(categorySlug);
        }
      }
    } else {
      onToggleCategory(categorySlug);
    }
  };

  const handleTagToggle = (tagId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onTagsChange) return;

    const newTags = selectedTags.includes(tagId)
      ? selectedTags.filter((t) => t !== tagId)
      : [...selectedTags, tagId];
    onTagsChange(newTags);
  };

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {categories.map((category) => {
        const Icon = category.icon;
        const isSelected = selectedCategories.includes(category.slug);
        const isExpanded = expandedCategory === category.slug;

        return (
          <div
            key={category.slug}
            className="relative transition-all duration-300"
          >
            <button
              type="button"
              onClick={() => handleCardClick(category.slug)}
              className={cn(
                'soft-card category-card group relative w-full overflow-hidden p-5 text-left transition-all duration-200',
                isSelected
                  ? 'ring-2 ring-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.05)]'
                  : '',
                isExpanded && 'rounded-b-none'
              )}
            >
              {/* Color accent bar */}
              <div
                className={cn(
                  'absolute left-0 top-0 w-full transition-all duration-300',
                  category.colorClass,
                  isSelected || isExpanded ? 'h-1.5' : 'h-1 group-hover:h-1.5'
                )}
              />

              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Icon */}
                  <div
                    className={cn(
                      'mb-3 inline-flex rounded-lg p-2.5 transition-transform duration-300 group-hover:scale-110',
                      category.mutedBgClass
                    )}
                  >
                    <Icon className={cn('h-5 w-5', category.textClass)} />
                  </div>

                  {/* Content */}
                  <h3 className="font-display text-lg font-medium text-foreground">
                    {category.name}
                  </h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                    {category.description}
                  </p>
                </div>

                {/* Right side indicators */}
                <div className="flex flex-col items-end gap-2">
                  {/* Selected indicator */}
                  {isSelected && (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))]">
                      <Check className="h-4 w-4 text-white" />
                    </div>
                  )}

                  {/* Expand indicator for tag expansion mode */}
                  {enableTagExpansion && (
                    <div
                      className={cn(
                        'flex items-center gap-1 text-xs text-muted-foreground',
                        isExpanded && category.textClass
                      )}
                    >
                      <Tag className="h-3 w-3" />
                      <ChevronDown
                        className={cn(
                          'h-3 w-3 transition-transform duration-200',
                          isExpanded && 'rotate-180'
                        )}
                      />
                    </div>
                  )}
                </div>
              </div>
            </button>

            {/* Expanded tag selection area */}
            {enableTagExpansion && isExpanded && (
              <ExpandedTagSection
                categorySlug={category.slug}
                categoryName={category.name}
                borderClass={category.borderClass}
                selectedTags={selectedTags}
                onTagToggle={(tagId, e) => handleTagToggle(tagId, e)}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

interface ExpandedTagSectionProps {
  categorySlug: string;
  categoryName: string;
  borderClass: string;
  selectedTags: string[];
  onTagToggle: (tagId: string, e: React.MouseEvent) => void;
}

function ExpandedTagSection({
  categorySlug,
  categoryName,
  borderClass,
  selectedTags,
  onTagToggle,
}: ExpandedTagSectionProps) {
  // Fetch tags for this category
  const { data: categoryTags, isLoading } = useQuery({
    queryKey: ['taxonomy', 'tags', categorySlug],
    queryFn: () => api.taxonomy.getCategoryTags(categorySlug),
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  });

  if (isLoading) {
    return (
      <div className={cn(
        'rounded-b-lg border-t-0 border-2 bg-card p-4',
        borderClass
      )}>
        <div className="flex flex-wrap gap-2">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-28" />
        </div>
      </div>
    );
  }

  if (!categoryTags) {
    return null;
  }

  return (
    <div
      className={cn(
        'rounded-b-lg border-t-0 border-2 bg-card/95 backdrop-blur p-4 animate-in slide-in-from-top-2 duration-200',
        borderClass
      )}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-xs font-medium text-muted-foreground mb-3 flex items-center gap-2">
        <Tag className="h-3 w-3" />
        Filter by {categoryName} tags:
      </div>

      <div className="space-y-4">
        {categoryTags.groups.map((group) => (
          <div key={group.group}>
            <div className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
              {group.group.replace(/_/g, ' ')}
            </div>
            <div className="flex flex-wrap gap-2">
              {group.tags.map((tag) => {
                const isTagSelected = selectedTags.includes(tag.id);
                return (
                  <div
                    key={tag.id}
                    role="button"
                    tabIndex={0}
                    onClick={(e) => onTagToggle(tag.id, e)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onTagToggle(tag.id, e as unknown as React.MouseEvent);
                      }
                    }}
                    className={cn(
                      'inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-sm transition-all cursor-pointer select-none',
                      isTagSelected
                        ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold-dark))] font-medium'
                        : 'border-border bg-background hover:bg-muted/50 text-foreground'
                    )}
                  >
                    <span
                      className={cn(
                        'flex h-3.5 w-3.5 items-center justify-center rounded-sm border',
                        isTagSelected
                          ? 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold))]'
                          : 'border-input bg-background'
                      )}
                    >
                      {isTagSelected && <Check className="h-2.5 w-2.5 text-white" />}
                    </span>
                    {tag.name}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Selected tags summary */}
      {selectedTags.length > 0 && (
        <div className="mt-4 pt-3 border-t">
          <div className="flex flex-wrap gap-1.5">
            {categoryTags.flat_tags
              .filter((tag) => selectedTags.includes(tag.id))
              .map((tag) => (
                <Badge
                  key={tag.id}
                  variant="secondary"
                  className="bg-[hsl(var(--v4v-gold)/0.2)] text-[hsl(var(--v4v-gold-dark))]"
                >
                  {tag.name}
                </Badge>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

export { categories };
