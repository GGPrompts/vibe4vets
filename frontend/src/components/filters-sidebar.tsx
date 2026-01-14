'use client';

import { useState } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Filter, X, Briefcase, GraduationCap, Home, Scale, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export const CATEGORIES = [
  { value: 'employment', label: 'Employment', icon: Briefcase },
  { value: 'training', label: 'Training', icon: GraduationCap },
  { value: 'housing', label: 'Housing', icon: Home },
  { value: 'legal', label: 'Legal', icon: Scale },
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

export const SCOPES = [
  { value: 'all', label: 'All Resources' },
  { value: 'national', label: 'Nationwide Only' },
  { value: 'state', label: 'State-Specific' },
] as const;

export interface FilterState {
  categories: string[];
  states: string[];
  scope: string;
  minTrust: number;
}

interface FiltersSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  resultCount?: number;
  hideHeader?: boolean;
}

const categoryColors: Record<string, string> = {
  employment: 'text-blue-600 dark:text-blue-400',
  training: 'text-purple-600 dark:text-purple-400',
  housing: 'text-green-600 dark:text-green-400',
  legal: 'text-amber-600 dark:text-amber-400',
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
        onClick={onToggle}
        className="flex w-full items-center justify-between py-1 text-left"
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
          isOpen ? 'mt-3 grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        )}
      >
        <div className="overflow-hidden">{children}</div>
      </div>
    </div>
  );
}

export function FiltersSidebar({
  filters,
  onFiltersChange,
  resultCount,
  hideHeader = false,
}: FiltersSidebarProps) {
  // Collapsible section state - categories and scope open by default
  const [categoriesOpen, setCategoriesOpen] = useState(true);
  const [scopeOpen, setScopeOpen] = useState(true);
  const [statesOpen, setStatesOpen] = useState(false);
  const [trustOpen, setTrustOpen] = useState(false);

  const activeFilterCount =
    filters.categories.length +
    filters.states.length +
    (filters.scope !== 'all' ? 1 : 0) +
    (filters.minTrust > 0 ? 1 : 0);

  const handleCategoryToggle = (category: string) => {
    const newCategories = filters.categories.includes(category)
      ? filters.categories.filter((c) => c !== category)
      : [...filters.categories, category];
    onFiltersChange({ ...filters, categories: newCategories });
  };

  const handleStateToggle = (state: string) => {
    const newStates = filters.states.includes(state)
      ? filters.states.filter((s) => s !== state)
      : [...filters.states, state];
    onFiltersChange({ ...filters, states: newStates });
  };

  const handleScopeChange = (scope: string) => {
    onFiltersChange({ ...filters, scope });
  };

  const handleTrustChange = (value: number[]) => {
    onFiltersChange({ ...filters, minTrust: value[0] });
  };

  const clearAllFilters = () => {
    onFiltersChange({
      categories: [],
      states: [],
      scope: 'all',
      minTrust: 0,
    });
  };

  return (
    <div className="space-y-6">
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

      {activeFilterCount > 0 && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearAllFilters}
          className="h-auto w-full justify-start px-0 py-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <X className="mr-1 h-3 w-3" />
          Clear all filters ({activeFilterCount})
        </Button>
      )}

      <Separator />

      {/* Categories */}
      <CollapsibleSection
        title="Categories"
        badge={
          filters.categories.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {filters.categories.length}
            </Badge>
          )
        }
        isOpen={categoriesOpen}
        onToggle={() => setCategoriesOpen(!categoriesOpen)}
      >
        <div className="space-y-2">
          {CATEGORIES.map((category) => {
            const Icon = category.icon;
            const isChecked = filters.categories.includes(category.value);
            return (
              <div key={category.value} className="flex items-center space-x-2">
                <Checkbox
                  id={`category-${category.value}`}
                  checked={isChecked}
                  onCheckedChange={() => handleCategoryToggle(category.value)}
                />
                <Label
                  htmlFor={`category-${category.value}`}
                  className={`flex cursor-pointer items-center gap-2 text-sm ${
                    isChecked ? categoryColors[category.value] : ''
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {category.label}
                </Label>
              </div>
            );
          })}
        </div>
      </CollapsibleSection>

      <Separator />

      {/* Scope */}
      <CollapsibleSection
        title="Coverage"
        badge={
          filters.scope !== 'all' && (
            <Badge variant="outline" className="text-xs">
              1
            </Badge>
          )
        }
        isOpen={scopeOpen}
        onToggle={() => setScopeOpen(!scopeOpen)}
      >
        <RadioGroup value={filters.scope} onValueChange={handleScopeChange}>
          {SCOPES.map((scope) => (
            <div key={scope.value} className="flex items-center space-x-2">
              <RadioGroupItem value={scope.value} id={`scope-${scope.value}`} />
              <Label
                htmlFor={`scope-${scope.value}`}
                className="cursor-pointer text-sm"
              >
                {scope.label}
              </Label>
            </div>
          ))}
        </RadioGroup>
      </CollapsibleSection>

      <Separator />

      {/* States */}
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
        onToggle={() => setStatesOpen(!statesOpen)}
      >
        <ScrollArea className="h-48 rounded-md border p-2">
          <div className="space-y-2">
            {STATES.map((state) => {
              const isChecked = filters.states.includes(state.value);
              return (
                <div key={state.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`state-${state.value}`}
                    checked={isChecked}
                    onCheckedChange={() => handleStateToggle(state.value)}
                  />
                  <Label
                    htmlFor={`state-${state.value}`}
                    className="cursor-pointer text-sm"
                  >
                    {state.label}
                  </Label>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </CollapsibleSection>

      <Separator />

      {/* Trust Level */}
      <CollapsibleSection
        title="Minimum Trust"
        badge={
          filters.minTrust > 0 && (
            <Badge variant="outline" className="text-xs">
              {filters.minTrust}%
            </Badge>
          )
        }
        isOpen={trustOpen}
        onToggle={() => setTrustOpen(!trustOpen)}
      >
        <div className="space-y-3">
          <Slider
            value={[filters.minTrust]}
            onValueChange={handleTrustChange}
            max={100}
            step={10}
            className="py-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Any</span>
            <span>Highly Trusted</span>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
}
