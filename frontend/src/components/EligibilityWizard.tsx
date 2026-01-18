'use client';

import { useCallback, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import {
  ChevronDown,
  ChevronUp,
  Filter,
  X,
  MapPin,
  Users,
  DollarSign,
  Home,
  Calendar,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// DMV states for initial focus
const DMV_STATES = [
  { value: 'DC', label: 'Washington, DC' },
  { value: 'MD', label: 'Maryland' },
  { value: 'VA', label: 'Virginia' },
] as const;

const AGE_BRACKETS = [
  { value: 'under_55', label: 'Under 55' },
  { value: '55_61', label: '55-61' },
  { value: '62_plus', label: '62+' },
  { value: '65_plus', label: '65+' },
] as const;

const HOUSEHOLD_SIZES = [
  { value: '1', label: '1 person' },
  { value: '2', label: '2 people' },
  { value: '3', label: '3 people' },
  { value: '4', label: '4 people' },
  { value: '5', label: '5+ people' },
] as const;

const INCOME_BRACKETS = [
  { value: 'low', label: 'Low income', description: 'Below 50% Area Median Income' },
  { value: 'moderate', label: 'Moderate income', description: '50-80% Area Median Income' },
  { value: 'any', label: 'Any income level', description: 'No income restrictions' },
] as const;

const HOUSING_STATUSES = [
  { value: 'homeless', label: 'Currently experiencing homelessness' },
  { value: 'at_risk', label: 'At risk of housing instability' },
  { value: 'stably_housed', label: 'Stably housed' },
] as const;

export interface EligibilityState {
  states: string[];
  ageBracket: string | null;
  householdSize: string | null;
  incomeBracket: string | null;
  housingStatus: string | null;
}

interface EligibilityWizardProps {
  onFiltersChange?: (filters: EligibilityState) => void;
  className?: string;
  compact?: boolean;
}

export function EligibilityWizard({
  onFiltersChange,
  className,
  compact = false,
}: EligibilityWizardProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Initialize state from URL params
  const getInitialState = (): EligibilityState => {
    const statesParam = searchParams.get('states');
    return {
      states: statesParam ? statesParam.split(',') : [],
      ageBracket: searchParams.get('age_bracket'),
      householdSize: searchParams.get('household_size'),
      incomeBracket: searchParams.get('income_bracket'),
      housingStatus: searchParams.get('housing_status'),
    };
  };

  const [filters, setFilters] = useState<EligibilityState>(getInitialState);
  const [isExpanded, setIsExpanded] = useState(!compact);

  // Section expansion state
  const [sectionsOpen, setSectionsOpen] = useState({
    location: true,
    age: false,
    household: false,
    income: false,
    housing: false,
  });

  const toggleSection = (section: keyof typeof sectionsOpen) => {
    setSectionsOpen((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  // Update URL with new filters
  const updateUrl = useCallback(
    (newFilters: EligibilityState) => {
      const params = new URLSearchParams(searchParams.toString());

      // Update each filter in URL
      if (newFilters.states.length > 0) {
        params.set('states', newFilters.states.join(','));
      } else {
        params.delete('states');
      }

      if (newFilters.ageBracket) {
        params.set('age_bracket', newFilters.ageBracket);
      } else {
        params.delete('age_bracket');
      }

      if (newFilters.householdSize) {
        params.set('household_size', newFilters.householdSize);
      } else {
        params.delete('household_size');
      }

      if (newFilters.incomeBracket) {
        params.set('income_bracket', newFilters.incomeBracket);
      } else {
        params.delete('income_bracket');
      }

      if (newFilters.housingStatus) {
        params.set('housing_status', newFilters.housingStatus);
      } else {
        params.delete('housing_status');
      }

      router.push(`?${params.toString()}`, { scroll: false });
    },
    [router, searchParams]
  );

  const handleFiltersChange = (newFilters: EligibilityState) => {
    setFilters(newFilters);
    updateUrl(newFilters);
    onFiltersChange?.(newFilters);
  };

  const handleStateToggle = (state: string) => {
    const newStates = filters.states.includes(state)
      ? filters.states.filter((s) => s !== state)
      : [...filters.states, state];
    handleFiltersChange({ ...filters, states: newStates });
  };

  const handleAgeBracketChange = (value: string) => {
    handleFiltersChange({ ...filters, ageBracket: value });
  };

  const handleHouseholdSizeChange = (value: string) => {
    handleFiltersChange({ ...filters, householdSize: value });
  };

  const handleIncomeBracketChange = (value: string) => {
    handleFiltersChange({ ...filters, incomeBracket: value });
  };

  const handleHousingStatusChange = (value: string) => {
    handleFiltersChange({ ...filters, housingStatus: value });
  };

  const clearAllFilters = () => {
    const emptyFilters: EligibilityState = {
      states: [],
      ageBracket: null,
      householdSize: null,
      incomeBracket: null,
      housingStatus: null,
    };
    handleFiltersChange(emptyFilters);
  };

  const activeFilterCount =
    filters.states.length +
    (filters.ageBracket ? 1 : 0) +
    (filters.householdSize ? 1 : 0) +
    (filters.incomeBracket ? 1 : 0) +
    (filters.housingStatus ? 1 : 0);

  return (
    <div className={cn('rounded-lg border bg-card p-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-left"
        >
          <Filter className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
          <h3 className="font-semibold">Eligibility Wizard</h3>
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="text-xs">
              {activeFilterCount} active
            </Badge>
          )}
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </button>
        {activeFilterCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="h-8 text-sm text-muted-foreground hover:text-foreground"
          >
            <X className="mr-1 h-3 w-3" />
            Clear all
          </Button>
        )}
      </div>

      {/* Privacy notice */}
      {isExpanded && (
        <p className="mt-2 text-xs text-muted-foreground">
          Your answers are stored in the URL only - never on our servers. Share
          the link to save your search.
        </p>
      )}

      {isExpanded && (
        <div className="mt-4 space-y-4">
          <Separator />

          {/* Location Section */}
          <div>
            <button
              onClick={() => toggleSection('location')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
            >
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Location</span>
                {filters.states.length > 0 && (
                  <Badge variant="outline" className="text-xs">
                    {filters.states.length}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.location && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.location && (
              <div className="mt-2 space-y-2 pl-6">
                {DMV_STATES.map((state) => (
                  <div key={state.value} className="flex min-h-[44px] items-center space-x-3">
                    <Checkbox
                      id={`state-${state.value}`}
                      checked={filters.states.includes(state.value)}
                      onCheckedChange={() => handleStateToggle(state.value)}
                    />
                    <Label
                      htmlFor={`state-${state.value}`}
                      className="flex-1 cursor-pointer text-sm"
                    >
                      {state.label}
                    </Label>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Separator />

          {/* Age Section */}
          <div>
            <button
              onClick={() => toggleSection('age')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
            >
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Age</span>
                {filters.ageBracket && (
                  <Badge variant="outline" className="text-xs">
                    {AGE_BRACKETS.find((b) => b.value === filters.ageBracket)?.label}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.age && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.age && (
              <div className="mt-2 pl-6">
                <RadioGroup
                  value={filters.ageBracket || ''}
                  onValueChange={handleAgeBracketChange}
                >
                  {AGE_BRACKETS.map((bracket) => (
                    <div key={bracket.value} className="flex min-h-[44px] items-center space-x-3">
                      <RadioGroupItem value={bracket.value} id={`age-${bracket.value}`} />
                      <Label
                        htmlFor={`age-${bracket.value}`}
                        className="flex-1 cursor-pointer text-sm"
                      >
                        {bracket.label}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}
          </div>

          <Separator />

          {/* Household Size Section */}
          <div>
            <button
              onClick={() => toggleSection('household')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
            >
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Household Size</span>
                {filters.householdSize && (
                  <Badge variant="outline" className="text-xs">
                    {HOUSEHOLD_SIZES.find((s) => s.value === filters.householdSize)?.label}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.household && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.household && (
              <div className="mt-2 pl-6">
                <RadioGroup
                  value={filters.householdSize || ''}
                  onValueChange={handleHouseholdSizeChange}
                >
                  {HOUSEHOLD_SIZES.map((size) => (
                    <div key={size.value} className="flex min-h-[44px] items-center space-x-3">
                      <RadioGroupItem value={size.value} id={`household-${size.value}`} />
                      <Label
                        htmlFor={`household-${size.value}`}
                        className="flex-1 cursor-pointer text-sm"
                      >
                        {size.label}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}
          </div>

          <Separator />

          {/* Income Section */}
          <div>
            <button
              onClick={() => toggleSection('income')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
            >
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Income Level</span>
                {filters.incomeBracket && (
                  <Badge variant="outline" className="text-xs">
                    {INCOME_BRACKETS.find((b) => b.value === filters.incomeBracket)?.label}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.income && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.income && (
              <div className="mt-2 pl-6">
                <RadioGroup
                  value={filters.incomeBracket || ''}
                  onValueChange={handleIncomeBracketChange}
                >
                  {INCOME_BRACKETS.map((bracket) => (
                    <div key={bracket.value} className="flex min-h-[44px] items-center space-x-3">
                      <RadioGroupItem value={bracket.value} id={`income-${bracket.value}`} />
                      <Label
                        htmlFor={`income-${bracket.value}`}
                        className="flex-1 cursor-pointer"
                      >
                        <span className="text-sm">{bracket.label}</span>
                        <span className="block text-xs text-muted-foreground">
                          {bracket.description}
                        </span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}
          </div>

          <Separator />

          {/* Housing Status Section */}
          <div>
            <button
              onClick={() => toggleSection('housing')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
            >
              <div className="flex items-center gap-2">
                <Home className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Housing Status</span>
                {filters.housingStatus && (
                  <Badge variant="outline" className="text-xs">
                    {HOUSING_STATUSES.find((s) => s.value === filters.housingStatus)?.label}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.housing && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.housing && (
              <div className="mt-2 pl-6">
                <RadioGroup
                  value={filters.housingStatus || ''}
                  onValueChange={handleHousingStatusChange}
                >
                  {HOUSING_STATUSES.map((status) => (
                    <div key={status.value} className="flex min-h-[44px] items-center space-x-3">
                      <RadioGroupItem value={status.value} id={`housing-${status.value}`} />
                      <Label
                        htmlFor={`housing-${status.value}`}
                        className="flex-1 cursor-pointer text-sm"
                      >
                        {status.label}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default EligibilityWizard;
