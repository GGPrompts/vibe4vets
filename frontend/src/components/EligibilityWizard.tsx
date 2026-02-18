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
  UtensilsCrossed,
  Leaf,
  FileCheck,
} from 'lucide-react';
import { useAnalytics } from '@/lib/useAnalytics';
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

const DIETARY_OPTIONS = [
  { value: 'halal', label: 'Halal' },
  { value: 'kosher', label: 'Kosher' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'gluten_free', label: 'Gluten-free' },
] as const;

const RESOURCE_CATEGORIES = [
  { value: 'housing', label: 'Housing assistance' },
  { value: 'employment', label: 'Employment services' },
  { value: 'training', label: 'Training programs' },
  { value: 'legal', label: 'Legal services' },
  { value: 'food', label: 'Food assistance' },
  { value: 'benefits', label: 'Benefits consultation' },
  { value: 'mentalHealth', label: 'Mental health services' },
  { value: 'supportServices', label: 'Support services' },
  { value: 'healthcare', label: 'Healthcare services' },
  { value: 'education', label: 'Education programs' },
  { value: 'financial', label: 'Financial assistance' },
] as const;

const BENEFIT_TYPES = [
  { value: 'disability', label: 'Disability compensation' },
  { value: 'pension', label: 'VA pension' },
  { value: 'education', label: 'Education benefits (GI Bill)' },
  { value: 'healthcare', label: 'Healthcare enrollment' },
  { value: 'survivor', label: 'Survivor/dependent benefits' },
] as const;

const CONSULTATION_PREFERENCES = [
  { value: 'walk_in', label: 'Walk-in appointments' },
  { value: 'virtual', label: 'Virtual consultation' },
  { value: 'any', label: 'Any format' },
] as const;

export interface EligibilityState {
  states: string[];
  ageBracket: string | null;
  householdSize: string | null;
  incomeBracket: string | null;
  housingStatus: string | null;
  category: string | null;
  dietaryNeeds: string[];
  benefitTypes: string[];
  consultationPreference: string | null;
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
  const { trackWizardStart, trackWizardStep, trackWizardComplete } = useAnalytics();

  // Initialize state from URL params
  const getInitialState = (): EligibilityState => {
    const statesParam = searchParams.get('states');
    const dietaryParam = searchParams.get('dietary');
    const benefitTypesParam = searchParams.get('benefit_types');
    return {
      states: statesParam ? statesParam.split(',') : [],
      ageBracket: searchParams.get('age_bracket'),
      householdSize: searchParams.get('household_size'),
      incomeBracket: searchParams.get('income_bracket'),
      housingStatus: searchParams.get('housing_status'),
      category: searchParams.get('category'),
      dietaryNeeds: dietaryParam ? dietaryParam.split(',') : [],
      benefitTypes: benefitTypesParam ? benefitTypesParam.split(',') : [],
      consultationPreference: searchParams.get('consultation_preference'),
    };
  };

  const [filters, setFilters] = useState<EligibilityState>(getInitialState);
  const [isExpanded, setIsExpanded] = useState(!compact);

  // Section expansion state
  const [sectionsOpen, setSectionsOpen] = useState({
    location: true,
    category: false,
    age: false,
    household: false,
    income: false,
    housing: false,
    dietary: false,
    benefits: false,
    consultation: false,
  });
  const [hasTrackedStart, setHasTrackedStart] = useState(false);

  const toggleSection = (section: keyof typeof sectionsOpen) => {
    const sectionMap: Record<string, number> = {
      location: 1,
      category: 2,
      age: 3,
      household: 4,
      income: 5,
      housing: 6,
      dietary: 7,
      benefits: 8,
      consultation: 9,
    };
    // Track wizard step when opening a section
    if (!sectionsOpen[section]) {
      trackWizardStep(sectionMap[section] || 0);
    }
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

      if (newFilters.category) {
        params.set('category', newFilters.category);
      } else {
        params.delete('category');
      }

      if (newFilters.dietaryNeeds.length > 0) {
        params.set('dietary', newFilters.dietaryNeeds.join(','));
      } else {
        params.delete('dietary');
      }

      if (newFilters.benefitTypes.length > 0) {
        params.set('benefit_types', newFilters.benefitTypes.join(','));
      } else {
        params.delete('benefit_types');
      }

      if (newFilters.consultationPreference) {
        params.set('consultation_preference', newFilters.consultationPreference);
      } else {
        params.delete('consultation_preference');
      }

      router.push(`?${params.toString()}`, { scroll: false });
    },
    [router, searchParams]
  );

  const handleFiltersChange = (newFilters: EligibilityState) => {
    // Track wizard start on first interaction
    if (!hasTrackedStart) {
      trackWizardStart();
      setHasTrackedStart(true);
    }

    setFilters(newFilters);
    updateUrl(newFilters);
    onFiltersChange?.(newFilters);

    // Track wizard complete when all main fields are filled
    const isComplete =
      newFilters.states.length > 0 &&
      newFilters.ageBracket &&
      newFilters.housingStatus;
    if (isComplete) {
      trackWizardComplete();
    }
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

  const handleCategoryChange = (value: string) => {
    handleFiltersChange({ ...filters, category: value });
  };

  const handleDietaryToggle = (dietary: string) => {
    const newDietary = filters.dietaryNeeds.includes(dietary)
      ? filters.dietaryNeeds.filter((d) => d !== dietary)
      : [...filters.dietaryNeeds, dietary];
    handleFiltersChange({ ...filters, dietaryNeeds: newDietary });
  };

  const handleBenefitTypeToggle = (benefitType: string) => {
    const newBenefitTypes = filters.benefitTypes.includes(benefitType)
      ? filters.benefitTypes.filter((bt) => bt !== benefitType)
      : [...filters.benefitTypes, benefitType];
    handleFiltersChange({ ...filters, benefitTypes: newBenefitTypes });
  };

  const handleConsultationPreferenceChange = (value: string) => {
    handleFiltersChange({ ...filters, consultationPreference: value });
  };

  const clearAllFilters = () => {
    const emptyFilters: EligibilityState = {
      states: [],
      ageBracket: null,
      householdSize: null,
      incomeBracket: null,
      housingStatus: null,
      category: null,
      dietaryNeeds: [],
      benefitTypes: [],
      consultationPreference: null,
    };
    handleFiltersChange(emptyFilters);
  };

  const activeFilterCount =
    filters.states.length +
    (filters.ageBracket ? 1 : 0) +
    (filters.householdSize ? 1 : 0) +
    (filters.incomeBracket ? 1 : 0) +
    (filters.housingStatus ? 1 : 0) +
    (filters.category ? 1 : 0) +
    filters.dietaryNeeds.length +
    filters.benefitTypes.length +
    (filters.consultationPreference ? 1 : 0);

  return (
    <div className={cn('rounded-lg border bg-card p-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-left"
          aria-expanded={isExpanded}
          aria-controls="eligibility-wizard-content"
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
        <div id="eligibility-wizard-content" className="mt-4 space-y-4">
          <Separator />

          {/* Location Section */}
          <div>
            <button
              onClick={() => toggleSection('location')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
              aria-expanded={sectionsOpen.location}
              aria-controls="wizard-section-location"
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
              <div id="wizard-section-location" className="mt-2 space-y-2 pl-6">
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

          {/* Resource Category Section */}
          <div>
            <button
              onClick={() => toggleSection('category')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
              aria-expanded={sectionsOpen.category}
              aria-controls="wizard-section-category"
            >
              <div className="flex items-center gap-2">
                <UtensilsCrossed className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Resource Type</span>
                {filters.category && (
                  <Badge variant="outline" className="text-xs">
                    {RESOURCE_CATEGORIES.find((c) => c.value === filters.category)?.label}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.category && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.category && (
              <div id="wizard-section-category" className="mt-2 pl-6">
                <RadioGroup
                  value={filters.category || ''}
                  onValueChange={handleCategoryChange}
                >
                  {RESOURCE_CATEGORIES.map((cat) => (
                    <div key={cat.value} className="flex min-h-[44px] items-center space-x-3">
                      <RadioGroupItem value={cat.value} id={`category-${cat.value}`} />
                      <Label
                        htmlFor={`category-${cat.value}`}
                        className="flex-1 cursor-pointer text-sm"
                      >
                        {cat.label}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}
          </div>

          <Separator />

          {/* Age Section */}
          <div>
            <button
              onClick={() => toggleSection('age')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
              aria-expanded={sectionsOpen.age}
              aria-controls="wizard-section-age"
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
              <div id="wizard-section-age" className="mt-2 pl-6">
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
              aria-expanded={sectionsOpen.household}
              aria-controls="wizard-section-household"
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
              <div id="wizard-section-household" className="mt-2 pl-6">
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
              aria-expanded={sectionsOpen.income}
              aria-controls="wizard-section-income"
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
              <div id="wizard-section-income" className="mt-2 pl-6">
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
              aria-expanded={sectionsOpen.housing}
              aria-controls="wizard-section-housing"
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
              <div id="wizard-section-housing" className="mt-2 pl-6">
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

          <Separator />

          {/* Dietary Needs Section (for food resources) */}
          <div>
            <button
              onClick={() => toggleSection('dietary')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
              aria-expanded={sectionsOpen.dietary}
              aria-controls="wizard-section-dietary"
            >
              <div className="flex items-center gap-2">
                <Leaf className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Dietary Needs</span>
                {filters.dietaryNeeds.length > 0 && (
                  <Badge variant="outline" className="text-xs">
                    {filters.dietaryNeeds.length}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.dietary && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.dietary && (
              <div id="wizard-section-dietary" className="mt-2 space-y-2 pl-6">
                <p className="text-xs text-muted-foreground mb-2">
                  Filter for food pantries that offer specific dietary options
                </p>
                {DIETARY_OPTIONS.map((option) => (
                  <div key={option.value} className="flex min-h-[44px] items-center space-x-3">
                    <Checkbox
                      id={`dietary-${option.value}`}
                      checked={filters.dietaryNeeds.includes(option.value)}
                      onCheckedChange={() => handleDietaryToggle(option.value)}
                    />
                    <Label
                      htmlFor={`dietary-${option.value}`}
                      className="flex-1 cursor-pointer text-sm"
                    >
                      {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Separator />

          {/* Benefits Type Section */}
          <div>
            <button
              onClick={() => toggleSection('benefits')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
              aria-expanded={sectionsOpen.benefits}
              aria-controls="wizard-section-benefits"
            >
              <div className="flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Benefits Help Needed</span>
                {filters.benefitTypes.length > 0 && (
                  <Badge variant="outline" className="text-xs">
                    {filters.benefitTypes.length}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.benefits && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.benefits && (
              <div id="wizard-section-benefits" className="mt-2 space-y-2 pl-6">
                {BENEFIT_TYPES.map((benefitType) => (
                  <div key={benefitType.value} className="flex min-h-[44px] items-center space-x-3">
                    <Checkbox
                      id={`benefit-${benefitType.value}`}
                      checked={filters.benefitTypes.includes(benefitType.value)}
                      onCheckedChange={() => handleBenefitTypeToggle(benefitType.value)}
                    />
                    <Label
                      htmlFor={`benefit-${benefitType.value}`}
                      className="flex-1 cursor-pointer text-sm"
                    >
                      {benefitType.label}
                    </Label>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Separator />

          {/* Consultation Preference Section */}
          <div>
            <button
              onClick={() => toggleSection('consultation')}
              className="flex w-full min-h-[44px] items-center justify-between py-2"
              aria-expanded={sectionsOpen.consultation}
              aria-controls="wizard-section-consultation"
            >
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Consultation Format</span>
                {filters.consultationPreference && (
                  <Badge variant="outline" className="text-xs">
                    {CONSULTATION_PREFERENCES.find((p) => p.value === filters.consultationPreference)?.label}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform',
                  sectionsOpen.consultation && 'rotate-180'
                )}
              />
            </button>
            {sectionsOpen.consultation && (
              <div id="wizard-section-consultation" className="mt-2 pl-6">
                <RadioGroup
                  value={filters.consultationPreference || ''}
                  onValueChange={handleConsultationPreferenceChange}
                >
                  {CONSULTATION_PREFERENCES.map((pref) => (
                    <div key={pref.value} className="flex min-h-[44px] items-center space-x-3">
                      <RadioGroupItem value={pref.value} id={`consultation-${pref.value}`} />
                      <Label
                        htmlFor={`consultation-${pref.value}`}
                        className="flex-1 cursor-pointer text-sm"
                      >
                        {pref.label}
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
