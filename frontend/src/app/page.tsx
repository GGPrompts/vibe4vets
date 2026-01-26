'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { USMap } from '@/components/us-map';
import { CategoryCards } from '@/components/CategoryCards';
import { SortChips } from '@/components/SortChips';
import { Button } from '@/components/ui/button';
import { Search, Loader2 } from 'lucide-react';
import { useFilterContext } from '@/context/filter-context';
import type { SortOption } from '@/components/sort-dropdown-header';
import { BackToTop } from '@/components/BackToTop';

export default function Home() {
  const { filters, toggleCategory, toggleState, setEnabled, resourceCount, isLoadingCount, totalCount, isLoadingTotal } = useFilterContext();
  const [selectedSort, setSelectedSort] = useState<SortOption>('shuffle');
  const [zipCode, setZipCode] = useState('');
  const router = useRouter();

  // Enable resource count fetching when on the home page
  useEffect(() => {
    setEnabled(true);
    return () => setEnabled(false);
  }, [setEnabled]);

  // Build search URL with all selected filters
  const buildSearchUrl = () => {
    const params = new URLSearchParams();

    // Add zip code if provided (enables distance sorting)
    const hasZip = zipCode.length === 5;
    if (hasZip) {
      params.set('zip', zipCode);
    }

    // Add states (can be combined with zip for broader results)
    filters.states.forEach((state) => {
      params.append('state', state);
    });

    // Add categories (multiple values)
    filters.categories.forEach((category) => {
      params.append('category', category);
    });

    // Add sort option (distance is default when zip is set, handled by search page)
    if (selectedSort && selectedSort !== 'newest' && !hasZip) {
      params.set('sort', selectedSort);
    }

    const queryString = params.toString();
    return queryString ? `/search?${queryString}` : '/search';
  };

  const handleZipChange = (zip: string) => {
    setZipCode(zip);
    // Auto-select distance sort when user enters a zip
    if (zip.length > 0 && selectedSort !== 'distance') {
      setSelectedSort('distance');
    }
  };

  const handleSearch = () => {
    router.push(buildSearchUrl());
  };

  return (
    <main className="min-h-screen pt-16">
      {/* Hero Section - Logo + Map */}
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
              resources for Veterans. Select filters below to get started.
            </p>
          </div>

          {/* Interactive US Map */}
          <div className="mx-auto max-w-4xl">
            <div className="hero-search-container rounded-2xl p-4 sm:p-6 shadow-2xl">
              <USMap
                className="[&_svg]:max-h-[280px] sm:[&_svg]:max-h-[320px]"
                selectedStates={filters.states}
                onToggleState={toggleState}
              />
            </div>
            <p className={`mt-4 text-center text-base font-medium text-[hsl(var(--v4v-gold))] ${filters.states.length === 0 ? 'invisible' : ''}`}>
              {filters.states.length > 0 ? `Selected: ${filters.states.join(', ')}` : 'Select states'}
            </p>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="relative bg-background py-12 lg:py-16">
        {/* Subtle background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -left-20 top-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-training)/0.04)] blur-3xl" />
          <div className="absolute -right-20 bottom-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-housing)/0.04)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          {/* Section header */}
          <div className="mb-8 text-center">
            <h2 className="font-display text-2xl font-semibold text-foreground sm:text-3xl">
              What do you need help with?
            </h2>
          </div>

          {/* Category cards grid */}
          <CategoryCards
            selectedCategories={filters.categories}
            onToggleCategory={toggleCategory}
          />

          {/* Sort preferences */}
          <div className="mt-10">
            <SortChips
              selectedSort={selectedSort}
              onSortChange={setSelectedSort}
              zipCode={zipCode}
              onZipChange={handleZipChange}
            />
          </div>

          {/* Search button */}
          <div className="mt-10 flex flex-col items-center gap-4">
            <Button
              onClick={handleSearch}
              size="lg"
              className="btn-gold gap-3 rounded-xl px-12 py-6 text-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 min-w-[320px]"
            >
              <Search className="h-6 w-6" />
              {isLoadingCount ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Loading...</span>
                </>
              ) : resourceCount !== null ? (
                <span className="tabular-nums">Search {resourceCount.toLocaleString()} Resources</span>
              ) : (
                <span>Search Resources</span>
              )}
            </Button>
            <p className={`text-sm text-muted-foreground ${!(filters.states.length > 0 || filters.categories.length > 0 || zipCode.length === 5) ? 'invisible' : ''}`}>
              {filters.states.length > 0 || filters.categories.length > 0 || zipCode.length === 5 ? (
                <>
                  {zipCode.length === 5 && `Near ${zipCode}`}
                  {zipCode.length === 5 && (filters.states.length > 0 || filters.categories.length > 0) && ' · '}
                  {filters.states.length > 0 && `${filters.states.length} state${filters.states.length > 1 ? 's' : ''}`}
                  {filters.states.length > 0 && filters.categories.length > 0 && ' · '}
                  {filters.categories.length > 0 && `${filters.categories.length} categor${filters.categories.length > 1 ? 'ies' : 'y'}`}
                  {(filters.states.length > 0 || filters.categories.length > 0) && ' selected'}
                </>
              ) : (
                'No filters selected'
              )}
            </p>
          </div>
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
              <span className="text-lg text-[hsl(var(--v4v-gold)/0.5)]">★</span>
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
