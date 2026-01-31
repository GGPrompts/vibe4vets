'use client';

import { useState, useRef, useCallback } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { USMap } from '@/components/us-map';
import { CategoryCards } from '@/components/CategoryCards';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, MapPin, ChevronDown, X, Locate, Loader2 } from 'lucide-react';
import { useFilterContext } from '@/context/filter-context';
import { BackToTop } from '@/components/BackToTop';
import { cn } from '@/lib/utils';

export default function Home() {
  const { filters, setStates, totalCount, isLoadingTotal } = useFilterContext();
  const [zipCode, setZipCode] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLocating, setIsLocating] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);
  const router = useRouter();
  const step2Ref = useRef<HTMLElement>(null);

  // Track if location has been selected (ZIP, state, or geolocation)
  const hasLocation = zipCode.length === 5 || filters.states.length > 0 || userCoords !== null;

  // Handle single state selection (replaces previous selection)
  const handleStateSelect = useCallback((stateAbbr: string) => {
    // Clear geolocation when selecting state
    setUserCoords(null);
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

  // Handle "Use my location" click
  const handleGeolocation = useCallback(() => {
    if (!navigator.geolocation) return;

    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsLocating(false);
        const { latitude, longitude } = position.coords;
        setUserCoords({ lat: latitude, lng: longitude });
        setZipCode(''); // Clear ZIP when using geolocation
        setStates([]); // Clear state selection
        // Scroll to categories
        setTimeout(() => {
          step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
      },
      () => {
        setIsLocating(false);
        // Silently fail - user can still use ZIP or state
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
    );
  }, [setStates]);

  // Build search URL with location pre-filtered
  const buildSearchUrl = (categorySlug?: string) => {
    const params = new URLSearchParams();

    // Add geolocation if available (highest priority)
    if (userCoords) {
      params.set('lat', String(userCoords.lat));
      params.set('lng', String(userCoords.lng));
      params.set('radius', '100');
    }
    // Add zip code if provided (enables distance sorting)
    else if (zipCode.length === 5) {
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

    // Clear geolocation when typing ZIP
    if (value.length > 0 && userCoords) {
      setUserCoords(null);
    }

    // Clear state selection when ZIP is entered (ZIP is more specific)
    if (value.length === 5 && filters.states.length > 0) {
      setStates([]);
    }

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
    <main className="min-h-screen pt-16 relative">
      {/* Gold strip behind header to match accent bar */}
      <div className="absolute top-0 left-0 right-0 h-16 bg-gradient-to-r from-[hsl(var(--v4v-gold))] via-[hsl(var(--v4v-gold-light))] to-[hsl(var(--v4v-gold))]" />

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

          {/* Map as hero element */}
          <div className="mx-auto max-w-5xl">
            {/* US Map in white container - hero element */}
            <div className="hero-search-container rounded-2xl p-4 sm:p-6 shadow-2xl">
              {/* Subtle instruction text */}
              <p className="text-center text-sm text-[hsl(var(--v4v-navy)/0.7)] mb-4">
                Click a state to begin
              </p>

              {/* Full-width US Map */}
              <div className="hidden sm:block">
                <USMap
                  className="[&_svg]:max-h-[360px]"
                  selectedStates={filters.states}
                  onToggleState={handleStateSelect}
                  singleSelect
                />
              </div>

              {/* Mobile: state selection */}
              <div className="sm:hidden">
                <USMap
                  className=""
                  selectedStates={filters.states}
                  onToggleState={handleStateSelect}
                  singleSelect
                />
              </div>

              {/* Selected state indicator inside container */}
              {filters.states.length > 0 && (
                <div className="mt-3 text-center">
                  <span className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--v4v-gold))] px-4 py-1.5 text-sm font-semibold text-[hsl(var(--v4v-navy))]">
                    {filters.states[0]}
                    <button
                      type="button"
                      onClick={() => setStates([])}
                      className="hover:text-[hsl(var(--v4v-navy)/0.7)] transition-colors"
                      aria-label="Clear state selection"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </span>
                </div>
              )}
            </div>

            {/* Location input below container - on blue background */}
            <div className="mt-6 flex flex-col items-center gap-4">
              {/* ZIP Code Input */}
              <div className="flex items-center gap-3">
                <span className="text-sm text-white/70">Or enter ZIP:</span>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/50" />
                  <Input
                    id="zip-input"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={zipCode}
                    onChange={handleZipChange}
                    placeholder="ZIP code"
                    className={cn(
                      'h-10 w-32 pl-9 pr-8 text-sm text-center bg-white/10 border border-white/20 text-white placeholder:text-white/40 rounded-lg',
                      'focus:border-[hsl(var(--v4v-gold))] focus:ring-[hsl(var(--v4v-gold)/0.3)] focus:ring-2 focus:bg-white/15',
                      zipCode.length === 5 && 'bg-[hsl(var(--v4v-gold))] border-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))] font-semibold placeholder:text-[hsl(var(--v4v-navy)/0.5)]'
                    )}
                  />
                  {zipCode && (
                    <button
                      type="button"
                      onClick={() => setZipCode('')}
                      className={cn(
                        'absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 transition-colors',
                        zipCode.length === 5 ? 'text-[hsl(var(--v4v-navy)/0.5)] hover:text-[hsl(var(--v4v-navy))]' : 'text-white/50 hover:text-white'
                      )}
                      aria-label="Clear ZIP code"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
                {zipCode.length === 5 && (
                  <span className="text-sm text-[hsl(var(--v4v-gold))] font-medium">
                    100mi radius
                  </span>
                )}
              </div>

              {/* Use my location button */}
              {!userCoords ? (
                <button
                  type="button"
                  onClick={handleGeolocation}
                  disabled={isLocating}
                  className="text-sm text-white/60 hover:text-white transition-colors flex items-center gap-1.5"
                >
                  {isLocating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Getting location...
                    </>
                  ) : (
                    <>
                      <Locate className="h-4 w-4" />
                      Use my current location
                    </>
                  )}
                </button>
              ) : (
                <div className="flex items-center gap-2 text-sm text-[hsl(var(--v4v-gold))] font-medium">
                  <Locate className="h-4 w-4" />
                  Using your location
                  <button
                    type="button"
                    onClick={() => setUserCoords(null)}
                    className="text-white/50 hover:text-white transition-colors"
                    aria-label="Clear location"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Scroll indicator when location not yet selected */}
            {!hasLocation && (
              <div className="mt-8 flex flex-col items-center text-white/50 animate-bounce">
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
        className="relative bg-background py-12 lg:py-16 scroll-mt-20"
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
              Search by keyword
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
            <span className="text-muted-foreground">or browse categories</span>
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
            {/* Logo */}
            <Link href="/" className="group">
              <Image
                src="/vrd-logo.png"
                alt="VetRD - Veteran Resource Directory"
                width={400}
                height={150}
                className="h-16 w-auto transition-all duration-300 group-hover:scale-105"
              />
            </Link>
            <p className="mt-2 text-sm text-[hsl(var(--v4v-gold))] font-medium">
              Veteran Resource Directory
            </p>

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
