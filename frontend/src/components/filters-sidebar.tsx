'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Filter, X, Briefcase, GraduationCap, Home, Scale, ChevronDown, PanelLeft, PanelLeftClose } from 'lucide-react';
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
  employment: 'text-[hsl(var(--v4v-employment))]',
  training: 'text-[hsl(var(--v4v-training))]',
  housing: 'text-[hsl(var(--v4v-housing))]',
  legal: 'text-[hsl(var(--v4v-legal))]',
};

const categoryAccents: Record<string, string> = {
  employment: 'border-l-[hsl(var(--v4v-employment))] bg-[hsl(var(--v4v-employment)/0.04)]',
  training: 'border-l-[hsl(var(--v4v-training))] bg-[hsl(var(--v4v-training)/0.04)]',
  housing: 'border-l-[hsl(var(--v4v-housing))] bg-[hsl(var(--v4v-housing)/0.04)]',
  legal: 'border-l-[hsl(var(--v4v-legal))] bg-[hsl(var(--v4v-legal)/0.04)]',
};

const categoryIconBg: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.1)]',
  training: 'bg-[hsl(var(--v4v-training)/0.1)]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.1)]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.1)]',
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
        className="flex w-full min-h-[44px] items-center justify-between py-2 text-left"
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

  const activeFilterCount =
    filters.categories.length +
    filters.states.length +
    (filters.scope !== 'all' ? 1 : 0);

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

  const clearAllFilters = () => {
    onFiltersChange({
      categories: [],
      states: [],
      scope: 'all',
      minTrust: 0, // Keep for API compatibility
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

      <Button
        variant="ghost"
        size="sm"
        onClick={clearAllFilters}
        className={cn(
          'h-auto w-full justify-start px-0 py-1 text-sm text-muted-foreground hover:text-foreground',
          activeFilterCount === 0 && 'invisible'
        )}
      >
        <X className="mr-1 h-3 w-3" />
        Clear all filters ({activeFilterCount})
      </Button>

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
        <div className="space-y-1">
          {CATEGORIES.map((category) => {
            const Icon = category.icon;
            const isChecked = filters.categories.includes(category.value);
            return (
              <div
                key={category.value}
                className={cn(
                  'flex min-h-[44px] items-center space-x-3 rounded-lg border-l-2 px-2 transition-all duration-200',
                  isChecked
                    ? categoryAccents[category.value]
                    : 'border-l-transparent hover:bg-muted/50'
                )}
              >
                <Checkbox
                  id={`category-${category.value}`}
                  checked={isChecked}
                  onCheckedChange={() => handleCategoryToggle(category.value)}
                  className={isChecked ? categoryColors[category.value] : ''}
                />
                <Label
                  htmlFor={`category-${category.value}`}
                  className={cn(
                    'flex flex-1 min-h-[44px] cursor-pointer items-center gap-2 text-sm',
                    isChecked ? categoryColors[category.value] : ''
                  )}
                >
                  <span className={cn(
                    'flex h-6 w-6 items-center justify-center rounded-md transition-colors',
                    isChecked ? categoryIconBg[category.value] : 'bg-muted/50'
                  )}>
                    <Icon className="h-3.5 w-3.5" />
                  </span>
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
        <RadioGroup value={filters.scope} onValueChange={handleScopeChange} className="space-y-1">
          {SCOPES.map((scope) => {
            const isSelected = filters.scope === scope.value;
            return (
              <div
                key={scope.value}
                className={cn(
                  'flex min-h-[44px] items-center space-x-3 rounded-lg border-l-2 px-2 transition-all duration-200',
                  isSelected
                    ? 'border-l-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.05)]'
                    : 'border-l-transparent hover:bg-muted/50'
                )}
              >
                <RadioGroupItem value={scope.value} id={`scope-${scope.value}`} />
                <Label
                  htmlFor={`scope-${scope.value}`}
                  className={cn(
                    'flex flex-1 min-h-[44px] cursor-pointer items-center text-sm',
                    isSelected && 'text-[hsl(var(--v4v-gold-dark))]'
                  )}
                >
                  {scope.label}
                </Label>
              </div>
            );
          })}
        </RadioGroup>
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
        onToggle={() => setStatesOpen(!statesOpen)}
      >
        <ScrollArea className="h-48 rounded-lg border bg-card/50 p-2">
          <div className="space-y-0.5">
            {STATES.map((state) => {
              const isChecked = filters.states.includes(state.value);
              return (
                <div
                  key={state.value}
                  className={cn(
                    'flex min-h-[40px] items-center space-x-3 rounded-md border-l-2 px-2 transition-all duration-200',
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
                      'flex flex-1 min-h-[40px] cursor-pointer items-center text-sm',
                      isChecked && 'font-medium text-[hsl(var(--v4v-navy))]'
                    )}
                  >
                    {state.label}
                  </Label>
                </div>
              );
            })}
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
] as const;

interface FixedFiltersSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  resultCount?: number;
}

export function FixedFiltersSidebar({
  filters,
  onFiltersChange,
  resultCount,
}: FixedFiltersSidebarProps) {
  // Default to collapsed
  const [isCollapsed, setIsCollapsed] = useState(true);

  // Load collapsed state from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('v4v-filters-collapsed');
    // Default to collapsed if no saved preference
    if (saved !== null) setIsCollapsed(saved === 'true');
  }, []);

  // Persist collapsed state
  const toggleCollapsed = () => {
    const newValue = !isCollapsed;
    setIsCollapsed(newValue);
    localStorage.setItem('v4v-filters-collapsed', String(newValue));
  };

  const activeFilterCount =
    filters.categories.length +
    filters.states.length +
    (filters.scope !== 'all' ? 1 : 0) +
    (filters.minTrust > 0 ? 1 : 0);

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
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleCollapsed}
                  className="h-9 w-9 text-muted-foreground hover:text-foreground"
                >
                  <PanelLeft className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p className="text-xs">Expand filters</p>
              </TooltipContent>
            </Tooltip>

            <div className="my-2 h-px w-6 bg-border" />

            {FILTER_ICONS.map((item, index) => {
              // Check if this category is currently active
              const isActive = item.key !== 'filter' && filters.categories.includes(item.key);

              const handleClick = () => {
                if (item.key === 'filter') {
                  // Main filter icon just expands the sidebar
                  toggleCollapsed();
                } else {
                  // Category icons toggle the filter directly
                  const newCategories = isActive
                    ? filters.categories.filter((c) => c !== item.key)
                    : [...filters.categories, item.key];
                  onFiltersChange({ ...filters, categories: newCategories });
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
                      <p className="text-xs">
                        {item.key === 'filter' ? item.label : `${isActive ? 'Remove' : 'Add'} ${item.label}`}
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </motion.div>
              );
            })}

            {activeFilterCount > 0 && (
              <>
                <div className="my-2 h-px w-6 bg-border" />
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onFiltersChange({ categories: [], states: [], scope: 'all', minTrust: 0 })}
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
            <div className="sidebar-header-accent flex items-center justify-between px-4 py-3">
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

            {/* Filter Content */}
            <ScrollArea className="flex-1 px-4 py-4">
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
