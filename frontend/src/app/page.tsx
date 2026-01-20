'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { USMap } from '@/components/us-map';
import { CategoryCards } from '@/components/CategoryCards';
import { SortChips } from '@/components/SortChips';
import { Button } from '@/components/ui/button';
import { Shield, RefreshCw, CheckCircle2, Search, Loader2 } from 'lucide-react';
import { useFilterContext } from '@/context/filter-context';
import type { SortOption } from '@/components/sort-dropdown-header';
import { BackToTop } from '@/components/BackToTop';

const trustIndicators = [
  {
    icon: Shield,
    title: 'Verified Sources',
    description: 'Aggregating resources from VA.gov, DOL, and community sources',
  },
  {
    icon: RefreshCw,
    title: 'Regularly Updated',
    description: 'Resources refreshed automatically to stay current',
  },
  {
    icon: CheckCircle2,
    title: 'Human Reviewed',
    description: 'Critical changes verified by our team',
  },
];

const steps = [
  {
    number: '01',
    title: 'Pick Your State',
    description: 'Click states on the map to focus on resources in your area',
    href: '#select-state',
  },
  {
    number: '02',
    title: 'Choose Categories',
    description: 'Select what you need: employment, training, housing, or legal help',
    href: '#choose-categories',
  },
  {
    number: '03',
    title: 'Find Resources',
    description: 'Hit search to see matching resources with contact details',
    href: '#search',
  },
];

export default function Home() {
  const { filters, toggleCategory, toggleState, setEnabled, resourceCount, isLoadingCount } = useFilterContext();
  const [selectedSort, setSelectedSort] = useState<SortOption>('shuffle');
  const router = useRouter();

  // Enable resource count fetching when on the home page
  useEffect(() => {
    setEnabled(true);
    return () => setEnabled(false);
  }, [setEnabled]);

  // Build search URL with all selected filters
  const buildSearchUrl = () => {
    const params = new URLSearchParams();

    // Add states (multiple values)
    filters.states.forEach((state) => {
      params.append('state', state);
    });

    // Add categories (multiple values)
    filters.categories.forEach((category) => {
      params.append('category', category);
    });

    // Add sort option
    if (selectedSort && selectedSort !== 'newest') {
      params.set('sort', selectedSort);
    }

    const queryString = params.toString();
    return queryString ? `/search?${queryString}` : '/search';
  };

  const handleSearch = () => {
    router.push(buildSearchUrl());
  };

  return (
    <main className="min-h-screen pt-16">
      {/* Hero Section - Bold opening with logo */}
      <section className="relative overflow-hidden bg-gradient-to-b from-[hsl(var(--v4v-bg-base))] via-[hsl(var(--v4v-bg-elevated))] to-[hsl(var(--v4v-bg-base))]">
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Large subtle star watermark */}
          <div className="absolute -right-20 -top-20 h-80 w-80 opacity-[0.03]">
            <Image
              src="/brand/vibe4vets-icon.png"
              alt=""
              fill
              className="object-contain"
              aria-hidden="true"
            />
          </div>
          {/* Gradient orbs for depth */}
          <div className="absolute left-1/4 top-1/3 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.08)] blur-3xl" />
          <div className="absolute right-1/3 bottom-0 h-48 w-48 rounded-full bg-[hsl(var(--v4v-employment)/0.06)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6 py-12 lg:py-16">
          {/* Logo + Tagline */}
          <div className="flex flex-col items-center text-center">
            <div className="animate-fade-in-up" style={{ opacity: 0 }}>
              <Image
                src="/brand/vibe4vets-logo-full-cropped.png"
                alt="Vibe4Vets - Veteran Resource Directory"
                width={582}
                height={157}
                priority
                className="h-auto w-auto max-w-[320px] sm:max-w-[450px] lg:max-w-[550px] drop-shadow-sm"
              />
            </div>
            <p className="animate-fade-in-up delay-100 mt-6 max-w-lg text-lg text-muted-foreground sm:text-xl" style={{ opacity: 0 }}>
              Employment, training, housing & legal resources—all in one place
            </p>
          </div>

          {/* How It Works - Jump links to sections */}
          <div className="animate-fade-in-up delay-200 mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center sm:gap-6 lg:gap-10" style={{ opacity: 0 }}>
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center gap-3">
                <a
                  href={step.href}
                  className="flex items-center gap-3 rounded-xl bg-card/60 backdrop-blur-sm px-5 py-4 border border-border/50 shadow-sm hover:shadow-md hover:border-[hsl(var(--v4v-gold)/0.4)] hover:bg-card/80 transition-all duration-300 cursor-pointer group"
                >
                  <span className="flex h-11 w-11 items-center justify-center rounded-full bg-[hsl(var(--v4v-gold))] font-display text-base font-bold text-[hsl(var(--v4v-navy))] shadow-sm group-hover:scale-110 transition-transform duration-200">
                    {step.number}
                  </span>
                  <div className="text-left">
                    <span className="font-medium text-foreground text-base group-hover:text-[hsl(var(--v4v-navy))]">{step.title}</span>
                    <p className="text-sm text-muted-foreground max-w-[180px] leading-snug">{step.description}</p>
                  </div>
                </a>
                {index < steps.length - 1 && (
                  <div className="hidden h-px w-6 bg-gradient-to-r from-border to-transparent lg:block" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Map Section - Navy background with angled transition */}
      <section id="select-state" className="relative overflow-hidden bg-v4v-navy text-white scroll-mt-20">
        {/* Angled top edge for visual interest */}
        <div className="absolute -top-1 left-0 right-0 h-16 bg-[hsl(var(--v4v-bg-base))]" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 30%, 0 100%)' }} />

        {/* Background gradient and pattern */}
        <div className="hero-gradient absolute inset-0" />
        <div className="hero-pattern absolute inset-0" />

        {/* Subtle glow effects */}
        <div className="absolute left-1/4 top-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-[hsl(var(--v4v-gold)/0.1)] blur-3xl" />
        <div className="absolute right-1/4 top-1/3 h-64 w-64 rounded-full bg-[hsl(var(--v4v-employment)/0.08)] blur-3xl" />

        <div className="relative mx-auto max-w-6xl px-6 py-16 lg:py-20">
          <div className="text-center">
            {/* Main headline with icon accent */}
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="h-px w-10 bg-gradient-to-r from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
              <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold))]">Step 1</span>
              <div className="h-px w-10 bg-gradient-to-l from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
            </div>
            <h2 className="font-display text-3xl font-semibold sm:text-4xl lg:text-5xl">
              Select Your{' '}
              <span className="text-[hsl(var(--v4v-gold))]">State</span>
            </h2>
            <p className="mt-3 text-base text-white/70 max-w-md mx-auto sm:text-lg">
              Click one or more states on the map to find local resources
            </p>

            {/* Interactive US Map */}
            <div className="mx-auto mt-8 max-w-4xl">
              <div className="hero-search-container rounded-2xl p-4 sm:p-6 shadow-2xl">
                <USMap
                  className="[&_svg]:max-h-[320px]"
                  selectedStates={filters.states}
                  onToggleState={toggleState}
                />
              </div>
              {filters.states.length > 0 && (
                <p className="mt-4 text-base font-medium text-[hsl(var(--v4v-gold))]">
                  Selected: {filters.states.join(', ')}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Angled bottom edge */}
        <div className="absolute -bottom-1 left-0 right-0 h-16 bg-background" style={{ clipPath: 'polygon(0 70%, 100% 0, 100% 100%, 0 100%)' }} />
      </section>

      {/* Categories Section - Enhanced with step indicator */}
      <section id="choose-categories" className="relative bg-background py-16 lg:py-20 scroll-mt-16">
        {/* Subtle background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -left-20 top-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-training)/0.04)] blur-3xl" />
          <div className="absolute -right-20 bottom-1/4 h-64 w-64 rounded-full bg-[hsl(var(--v4v-housing)/0.04)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          {/* Section header with step indicator */}
          <div className="mb-10 text-center">
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="h-px w-10 bg-gradient-to-r from-transparent to-border" />
              <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]">Step 2</span>
              <div className="h-px w-10 bg-gradient-to-l from-transparent to-border" />
            </div>
            <h2 className="font-display text-3xl font-semibold text-foreground sm:text-4xl">
              Choose Your Categories
            </h2>
            <p className="mt-3 text-base text-muted-foreground max-w-md mx-auto sm:text-lg">
              Select one or more categories to narrow your search
            </p>
          </div>

          {/* Category cards grid */}
          <CategoryCards
            selectedCategories={filters.categories}
            onToggleCategory={toggleCategory}
          />

          {/* Sort preferences */}
          <div className="mt-10 text-center">
            <p className="text-base text-muted-foreground mb-3">How should we sort your results?</p>
            <SortChips
              selectedSort={selectedSort}
              onSortChange={setSelectedSort}
            />
          </div>

          {/* Search button - Made more prominent */}
          <div id="search" className="mt-12 flex flex-col items-center gap-4 scroll-mt-24">
            <Button
              onClick={handleSearch}
              size="lg"
              className="btn-gold gap-3 rounded-xl px-12 py-6 text-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <Search className="h-6 w-6" />
              {isLoadingCount ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Loading...</span>
                </>
              ) : resourceCount !== null ? (
                <span>Search {resourceCount.toLocaleString()} Resources</span>
              ) : (
                <span>Search Resources</span>
              )}
            </Button>
            {(filters.states.length > 0 || filters.categories.length > 0) && (
              <p className="text-sm text-muted-foreground">
                {filters.states.length > 0 && `${filters.states.length} state${filters.states.length > 1 ? 's' : ''}`}
                {filters.states.length > 0 && filters.categories.length > 0 && ' · '}
                {filters.categories.length > 0 && `${filters.categories.length} categor${filters.categories.length > 1 ? 'ies' : 'y'}`}
                {' selected'}
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Trust Indicators Section - More visual interest */}
      <section className="relative bg-gradient-to-b from-card to-[hsl(var(--v4v-bg-muted))] py-16">
        <div className="mx-auto max-w-6xl px-6">
          <div className="text-center mb-10">
            <h3 className="font-display text-2xl font-medium text-foreground sm:text-3xl">Why Vibe4Vets?</h3>
          </div>
          <div className="grid gap-6 sm:grid-cols-3">
            {trustIndicators.map((indicator, index) => {
              const Icon = indicator.icon;
              return (
                <div
                  key={indicator.title}
                  className="group relative rounded-2xl bg-card/80 backdrop-blur-sm border border-border/50 p-8 text-center shadow-sm hover:shadow-md hover:border-[hsl(var(--v4v-gold)/0.3)] transition-all duration-300"
                >
                  {/* Decorative number */}
                  <span className="absolute -top-3 -right-3 flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--v4v-gold)/0.15)] text-sm font-medium text-[hsl(var(--v4v-gold-dark))]">
                    {index + 1}
                  </span>
                  <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-[hsl(var(--v4v-gold)/0.15)] to-[hsl(var(--v4v-gold)/0.05)] group-hover:from-[hsl(var(--v4v-gold)/0.25)] group-hover:to-[hsl(var(--v4v-gold)/0.1)] transition-all duration-300">
                    <Icon className="h-7 w-7 text-[hsl(var(--v4v-gold-dark))]" />
                  </div>
                  <h4 className="text-lg font-medium text-foreground">
                    {indicator.title}
                  </h4>
                  <p className="mt-2 text-base text-muted-foreground leading-relaxed">
                    {indicator.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer - Enhanced with logo and visual polish */}
      <footer className="relative overflow-hidden bg-v4v-navy py-14 text-white">
        {/* Decorative background */}
        <div className="absolute inset-0">
          <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.05)] blur-3xl" />
          <div className="absolute -left-32 -bottom-32 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.03)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          <div className="flex flex-col items-center text-center">
            {/* Logo */}
            <Image
              src="/brand/vibe4vets-icon.png"
              alt=""
              width={56}
              height={56}
              className="h-14 w-14 opacity-80"
            />
            <h2 className="mt-3 font-display text-2xl font-semibold text-[hsl(var(--v4v-gold))]">Vibe4Vets</h2>

            {/* Transparency statement */}
            <p className="mt-4 max-w-lg text-base leading-relaxed text-white/70">
              Built with transparency. We aggregate veteran resources from VA.gov,
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
              Helping veterans find resources, one search at a time
            </p>
          </div>
        </div>
      </footer>

      {/* Back to top button */}
      <BackToTop />
    </main>
  );
}
