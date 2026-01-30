'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { USMap } from '@/components/us-map';
import { CategoryCards } from '@/components/CategoryCards';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, MapPin, ChevronDown } from 'lucide-react';
import { useFilterContext } from '@/context/filter-context';
import { BackToTop } from '@/components/BackToTop';
import { cn } from '@/lib/utils';

export default function Home() {
  const { filters, setStates, totalCount, isLoadingTotal } = useFilterContext();
  const [zipCode, setZipCode] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [locationSelected, setLocationSelected] = useState(false);
  const router = useRouter();
  const step2Ref = useRef<HTMLElement>(null);

  // Track if location has been selected (ZIP or state)
  const hasLocation = zipCode.length === 5 || filters.states.length > 0;

  // Smooth scroll to Step 2 when location is selected
  useEffect(() => {
    if (hasLocation && !locationSelected) {
      setLocationSelected(true);
      // Small delay to allow state update before scroll
      setTimeout(() => {
        step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    }
  }, [hasLocation, locationSelected]);

  // Handle single state selection (replaces previous selection)
  const handleStateSelect = useCallback((stateAbbr: string) => {
    // Single-select: if same state clicked, deselect; otherwise select only this state
    if (filters.states.includes(stateAbbr)) {
      setStates([]);
    } else {
      setStates([stateAbbr]);
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
          {/* Step indicator */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))] text-sm font-bold text-[hsl(var(--v4v-navy))]">
              1
            </span>
            <span className="text-sm font-medium text-white/90">Where are you located?</span>
          </div>

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
              {/* ZIP Code Input - centered */}
              <div className="flex flex-col items-center gap-3 mb-6">
                <label htmlFor="zip-input" className="text-sm font-medium text-white/90">
                  Enter your ZIP code
                </label>
                <div className="relative w-full max-w-[200px]">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-white/50" />
                  <Input
                    id="zip-input"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={zipCode}
                    onChange={handleZipChange}
                    placeholder="e.g. 22030"
                    style={{ color: 'white' }}
                    className={cn(
                      'h-12 pl-10 text-lg text-center bg-white/10 border-white/20 placeholder:text-white/40',
                      'focus:bg-white/20 focus:border-[hsl(var(--v4v-gold))] focus:ring-[hsl(var(--v4v-gold)/0.3)]',
                      zipCode.length === 5 && 'bg-[hsl(var(--v4v-gold)/0.2)] border-[hsl(var(--v4v-gold))] font-semibold'
                    )}
                  />
                </div>
                {zipCode.length === 5 && (
                  <p className="text-sm text-[hsl(var(--v4v-gold))] font-medium">
                    Searching within 100 miles
                  </p>
                )}
              </div>

              {/* Divider */}
              <div className="flex items-center gap-3 mb-6">
                <div className="h-px flex-1 bg-white/20" />
                <span className="text-xs text-white/50 uppercase tracking-wide">or click a state</span>
                <div className="h-px flex-1 bg-white/20" />
              </div>

              {/* Full-width US Map */}
              <div className="hidden sm:block">
                <USMap
                  className="[&_svg]:max-h-[320px]"
                  selectedStates={filters.states}
                  onToggleState={handleStateSelect}
                  singleSelect
                />
              </div>

              {/* Mobile: Dropdown for state selection */}
              <div className="sm:hidden">
                <USMap
                  className=""
                  selectedStates={filters.states}
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
        className={cn(
          'relative bg-background py-12 lg:py-16 transition-opacity duration-500',
          hasLocation ? 'opacity-100' : 'opacity-50'
        )}
      >
        {/* Subtle background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -left-20 top-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-training)/0.04)] blur-3xl" />
          <div className="absolute -right-20 bottom-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-housing)/0.04)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          {/* Step indicator */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className={cn(
              'flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold transition-colors',
              hasLocation
                ? 'bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]'
                : 'bg-muted text-muted-foreground'
            )}>
              2
            </span>
            <span className={cn(
              'text-sm font-medium transition-colors',
              hasLocation ? 'text-foreground' : 'text-muted-foreground'
            )}>
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
                  disabled={!hasLocation}
                />
                <Button
                  type="submit"
                  disabled={!hasLocation}
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
