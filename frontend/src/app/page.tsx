'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { USMap } from '@/components/us-map';
import { CategoryCards } from '@/components/CategoryCards';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, MapPin, ChevronDown, X } from 'lucide-react';
import { useFilterContext } from '@/context/filter-context';
import { BackToTop } from '@/components/BackToTop';
import { cn } from '@/lib/utils';

export default function Home() {
  const { filters, setStates, totalCount, isLoadingTotal } = useFilterContext();
  const [zipCode, setZipCode] = useState('');
  const [zipState, setZipState] = useState<string | null>(null); // State for the entered ZIP
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const step2Ref = useRef<HTMLElement>(null);

  // Track if location has been selected (ZIP or state)
  const hasLocation = zipCode.length === 5 || filters.states.length > 0;

  // Map ZIP prefix (first 3 digits) to state - covers ~99% of cases
  // Source: USPS ZIP code prefix assignments
  const getStateFromZip = (zip: string): string | null => {
    if (zip.length < 3) return null;
    const prefix = parseInt(zip.substring(0, 3), 10);

    // ZIP prefix ranges by state (approximate, covers most cases)
    const ranges: [number, number, string][] = [
      [5, 5, 'NY'], [100, 149, 'NY'],
      [150, 196, 'PA'],
      [197, 199, 'DE'],
      [200, 205, 'DC'],
      [206, 219, 'MD'],
      [220, 246, 'VA'],
      [247, 268, 'WV'],
      [270, 289, 'NC'],
      [290, 299, 'SC'],
      [300, 319, 'GA'], [398, 399, 'GA'],
      [320, 339, 'FL'], [341, 342, 'FL'],
      [350, 369, 'AL'],
      [370, 385, 'TN'],
      [386, 397, 'MS'],
      [400, 418, 'KY'],
      [420, 427, 'KY'],
      [430, 458, 'OH'],
      [460, 479, 'IN'],
      [480, 499, 'MI'],
      [500, 528, 'IA'],
      [530, 549, 'WI'],
      [550, 567, 'MN'],
      [570, 577, 'SD'],
      [580, 588, 'ND'],
      [590, 599, 'MT'],
      [600, 629, 'IL'],
      [630, 658, 'MO'],
      [660, 679, 'KS'],
      [680, 693, 'NE'],
      [700, 714, 'LA'],
      [716, 729, 'AR'],
      [730, 749, 'OK'],
      [750, 799, 'TX'],
      [800, 816, 'CO'],
      [820, 831, 'WY'],
      [832, 838, 'ID'],
      [840, 847, 'UT'],
      [850, 865, 'AZ'],
      [870, 884, 'NM'],
      [889, 898, 'NV'],
      [900, 961, 'CA'],
      [967, 968, 'HI'],
      [970, 979, 'OR'],
      [980, 994, 'WA'],
      [995, 999, 'AK'],
      [6, 9, 'PR'],
      [10, 27, 'MA'],
      [28, 29, 'RI'],
      [30, 38, 'NH'],
      [39, 49, 'ME'],
      [50, 59, 'VT'],
      [60, 69, 'CT'],
      [70, 89, 'NJ'],
    ];

    for (const [start, end, state] of ranges) {
      if (prefix >= start && prefix <= end) {
        return state;
      }
    }
    return null;
  };

  // Get state from ZIP prefix (instant, no API call needed)
  useEffect(() => {
    if (zipCode.length === 5) {
      setZipState(getStateFromZip(zipCode));
    } else {
      setZipState(null);
    }
  }, [zipCode]);

  // Handle single state selection (replaces previous selection)
  const handleStateSelect = useCallback((stateAbbr: string) => {
    // Single-select: if same state clicked, deselect; otherwise select only this state
    if (filters.states.includes(stateAbbr)) {
      setStates([]);
    } else {
      setStates([stateAbbr]);
      // Scroll to categories when state is selected
      setTimeout(() => {
        step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    }
  }, [filters.states, setStates]);

  // Build search URL with location pre-filtered
  const buildSearchUrl = (categorySlug?: string) => {
    const params = new URLSearchParams();

    // Add zip code if provided (enables distance sorting)
    if (zipCode.length === 5) {
      params.set('zip', zipCode);
      params.set('radius', '100'); // Default 100mi for rural coverage
    }

    // Add state (single selection)
    if (filters.states.length > 0) {
      params.set('state', filters.states[0]);
    }

    // Add category if clicking from category card
    if (categorySlug) {
      params.set('category', categorySlug);
    }

    // Add categories from filter context
    filters.categories.forEach((category) => {
      if (category !== categorySlug) {
        params.append('category', category);
      }
    });

    // Add search query if provided
    if (searchQuery.trim()) {
      params.set('q', searchQuery.trim());
    }

    const queryString = params.toString();
    return queryString ? `/search?${queryString}` : '/search';
  };

  const handleZipChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 5);
    setZipCode(value);

    // Scroll to categories when ZIP is complete
    if (value.length === 5) {
      setTimeout(() => {
        step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    }
  };

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault();
    router.push(buildSearchUrl());
  };

  const handleCategoryClick = (categorySlug: string) => {
    // Navigate directly to search with this category
    router.push(buildSearchUrl(categorySlug));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <main className="min-h-screen pt-16">
      {/* Step 1: Location Selection */}
      <section className="relative overflow-hidden bg-v4v-navy text-white">
        {/* Background gradient and pattern */}
        <div className="hero-gradient absolute inset-0" />
        <div className="hero-pattern absolute inset-0" />

        {/* Subtle glow effects */}
        <div className="absolute left-1/4 top-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-[hsl(var(--v4v-gold)/0.1)] blur-3xl" />
        <div className="absolute right-1/4 top-1/3 h-64 w-64 rounded-full bg-[hsl(var(--v4v-employment)/0.08)] blur-3xl" />

        <div className="relative mx-auto max-w-6xl px-6 py-10 lg:py-14">
          {/* Intro text */}
          <div className="flex flex-col items-center text-center mb-8">
            <h1 className="font-display text-2xl font-semibold text-white sm:text-3xl lg:text-4xl">
              Veteran Resource Directory
            </h1>
            <p className="mt-3 text-base text-white/80 sm:text-lg max-w-xl">
              We&apos;ve curated{' '}
              <span className="font-semibold text-[hsl(var(--v4v-gold))]">
                {isLoadingTotal ? '...' : (totalCount?.toLocaleString() ?? '1,500+')}
              </span>{' '}
              resources for Veterans. Start by telling us your location.
            </p>
          </div>

          {/* ZIP centered above full-width map */}
          <div className="mx-auto max-w-5xl">
            <div className="hero-search-container rounded-2xl p-4 sm:p-6 shadow-2xl">
              {/* Step indicator - inside white container */}
              <div className="flex items-center justify-center gap-2 mb-4">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))] text-sm font-bold text-[hsl(var(--v4v-navy))]">
                  1
                </span>
                <span className="text-sm font-medium text-[hsl(var(--v4v-navy))]">Where are you located?</span>
              </div>

              {/* ZIP Code Input - centered */}
              <div className="flex flex-col items-center gap-3 mb-6">
                <label htmlFor="zip-input" className="text-sm font-medium text-[hsl(var(--v4v-navy))]">
                  Enter your ZIP code
                </label>
                <div className="relative w-full max-w-[220px]">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(var(--v4v-navy))]" />
                  <Input
                    id="zip-input"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={zipCode}
                    onChange={handleZipChange}
                    placeholder="e.g. 22030"
                    className={cn(
                      'h-12 pl-10 pr-10 text-lg text-center bg-white border-2 border-white text-[hsl(var(--v4v-navy))] placeholder:text-gray-400 rounded-lg shadow-lg',
                      'focus:border-[hsl(var(--v4v-gold))] focus:ring-[hsl(var(--v4v-gold)/0.5)] focus:ring-2',
                      zipCode.length === 5 && 'bg-[hsl(var(--v4v-gold))] border-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))] font-semibold'
                    )}
                  />
                  {zipCode && (
                    <button
                      type="button"
                      onClick={() => setZipCode('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(var(--v4v-navy)/0.5)] hover:text-[hsl(var(--v4v-navy))] transition-colors"
                      aria-label="Clear ZIP code"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  )}
                </div>
                {zipCode.length === 5 && (
                  <p className="text-sm text-[hsl(var(--v4v-gold))] font-medium">
                    Searching within 100 miles
                  </p>
                )}
              </div>

              {/* Divider */}
              <div className="flex items-center gap-3 mb-6">
                <div className="h-px flex-1 bg-[hsl(var(--v4v-navy)/0.2)]" />
                <span className="text-xs text-[hsl(var(--v4v-navy)/0.6)] uppercase tracking-wide">or click a state</span>
                <div className="h-px flex-1 bg-[hsl(var(--v4v-navy)/0.2)]" />
              </div>

              {/* Full-width US Map */}
              <div className="hidden sm:block">
                <USMap
                  className="[&_svg]:max-h-[320px]"
                  selectedStates={zipState ? [zipState] : filters.states}
                  onToggleState={handleStateSelect}
                  singleSelect
                />
              </div>

              {/* Mobile: Dropdown for state selection */}
              <div className="sm:hidden">
                <USMap
                  className=""
                  selectedStates={zipState ? [zipState] : filters.states}
                  onToggleState={handleStateSelect}
                  singleSelect
                />
              </div>
            </div>

            {/* Selected location indicator */}
            {hasLocation && (
              <div className="mt-4 text-center">
                <p className="text-base font-medium text-[hsl(var(--v4v-gold))]">
                  {zipCode.length === 5 && `ZIP: ${zipCode}`}
                  {zipCode.length === 5 && filters.states.length > 0 && ' + '}
                  {filters.states.length > 0 && filters.states[0]}
                </p>
              </div>
            )}

            {/* Scroll indicator when location not yet selected */}
            {!hasLocation && (
              <div className="mt-6 flex flex-col items-center text-white/50 animate-bounce">
                <span className="text-xs mb-1">Select a location to continue</span>
                <ChevronDown className="h-5 w-5" />
              </div>
            )}
          </div>
        </div>

        {/* Scroll cue when location IS selected */}
        {hasLocation && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center text-white/70 animate-bounce">
            <ChevronDown className="h-6 w-6" />
          </div>
        )}
      </section>

      {/* Step 2: What are you looking for? */}
      <section
        ref={step2Ref}
        className="relative bg-background py-12 lg:py-16"
      >
        {/* Subtle background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -left-20 top-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-training)/0.04)] blur-3xl" />
          <div className="absolute -right-20 bottom-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-housing)/0.04)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          {/* Step indicator */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]">
              2
            </span>
            <span className="text-sm font-medium text-foreground">
              What do you need help with?
            </span>
          </div>

          {/* Section header */}
          <div className="mb-8 text-center">
            <h2 className="font-display text-2xl font-semibold text-foreground sm:text-3xl">
              Find Resources
            </h2>
            <p className="mt-2 text-muted-foreground">
              Search by keyword or browse by category
            </p>
          </div>

          {/* Search bar */}
          <form onSubmit={handleSearch} className="mb-10">
            <div className="mx-auto max-w-2xl">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Search for jobs, housing, benefits, legal help..."
                  className="h-14 pl-12 pr-32 text-lg rounded-xl border-2 focus:border-[hsl(var(--v4v-gold))]"
                />
                <Button
                  type="submit"
                  className="absolute right-2 top-1/2 -translate-y-1/2 btn-gold rounded-lg px-6"
                >
                  Search
                </Button>
              </div>
            </div>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 mb-10">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-muted-foreground">or browse categories</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          {/* Category cards grid - clicking navigates to search */}
          <CategoryCards
            selectedCategories={filters.categories}
            onToggleCategory={handleCategoryClick}
          />

          {/* Location reminder if not set */}
          {!hasLocation && (
            <div className="mt-8 text-center">
              <p className="text-sm text-muted-foreground">
                <button
                  type="button"
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                  className="text-[hsl(var(--v4v-gold-dark))] hover:underline font-medium"
                >
                  Select your location above
                </button>
                {' '}to see resources near you
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="relative overflow-hidden bg-v4v-navy py-10 text-white">
        {/* Decorative background */}
        <div className="absolute inset-0">
          <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.05)] blur-3xl" />
          <div className="absolute -left-32 -bottom-32 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.03)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          <div className="flex flex-col items-center text-center">
            <h2 className="font-display text-2xl font-semibold text-[hsl(var(--v4v-gold))]">Vibe4Vets</h2>

            {/* Transparency statement */}
            <p className="mt-4 max-w-lg text-base leading-relaxed text-white/70">
              Built with transparency. We aggregate Veteran resources from VA.gov,
              DOL, nonprofits, and community organizations—all in one searchable
              directory powered by AI.
            </p>

            {/* Links */}
            <div className="mt-6 flex flex-wrap justify-center gap-8 text-base">
              <Link href="/search" className="text-white/70 transition-colors hover:text-[hsl(var(--v4v-gold))] flex items-center gap-2">
                <Search className="h-4 w-4" />
                Search
              </Link>
              <Link href="/discover" className="text-white/70 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Fresh Finds
              </Link>
              <Link href="/about" className="text-white/70 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                About
              </Link>
              <Link href="/admin" className="text-white/70 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Admin
              </Link>
            </div>

            {/* Divider with star */}
            <div className="mt-8 flex items-center gap-4 text-white/20">
              <div className="h-px w-16 bg-gradient-to-r from-transparent to-white/20" />
              <span className="text-lg text-[hsl(var(--v4v-gold)/0.5)]">*</span>
              <div className="h-px w-16 bg-gradient-to-l from-transparent to-white/20" />
            </div>

            {/* Copyright */}
            <p className="mt-4 text-sm text-white/50">
              Helping Veterans find resources, one search at a time
            </p>
          </div>
        </div>
      </footer>

      {/* Back to top button */}
      <BackToTop />
    </main>
  );
}
