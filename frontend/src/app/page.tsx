'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { USMap } from '@/components/us-map';
import { CategoryCards } from '@/components/CategoryCards';
import { SortChips } from '@/components/SortChips';
import { Shield, RefreshCw, CheckCircle2, Search } from 'lucide-react';
import { useFilterContext } from '@/context/filter-context';
import type { SortOption } from '@/components/sort-dropdown-header';

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
    title: 'Search',
    description: 'Enter keywords or browse by category to find relevant resources',
  },
  {
    number: '02',
    title: 'Filter',
    description: 'Narrow results by location, category, or specific needs',
  },
  {
    number: '03',
    title: 'Connect',
    description: 'Get contact info and details to access the resources you need',
  },
];

export default function Home() {
  const { filters, toggleCategory, toggleState, setEnabled } = useFilterContext();
  const [selectedSort, setSelectedSort] = useState<SortOption>('shuffle');

  // Enable resource count fetching when on the home page
  useEffect(() => {
    setEnabled(true);
    return () => setEnabled(false);
  }, [setEnabled]);

  return (
    <main className="min-h-screen pt-14">
      {/* Hero Section - Navy background */}
      <section className="relative overflow-hidden bg-v4v-navy text-white">
        {/* Background gradient and pattern */}
        <div className="hero-gradient absolute inset-0" />
        <div className="hero-pattern absolute inset-0" />

        {/* Gold accent gradient */}
        <div className="absolute right-0 top-0 h-full w-1/2 opacity-20">
          <div className="h-full w-full bg-gradient-to-l from-[hsl(var(--v4v-gold))] via-transparent to-transparent" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6 py-12 lg:py-16">
          <div className="text-center">
            {/* Main headline - single line */}
            <h1
              className="animate-fade-in-up font-display text-3xl font-semibold sm:text-4xl lg:text-5xl"
              style={{ opacity: 0 }}
            >
              Find Veteran Resources{' '}
              <span className="text-[hsl(var(--v4v-gold))]">by State</span>
            </h1>

            {/* Interactive US Map */}
            <div className="animate-fade-in-up delay-100 mx-auto mt-8 max-w-4xl" style={{ opacity: 0 }}>
              <div className="hero-search-container rounded-xl p-4">
                <USMap
                  className="[&_svg]:max-h-[320px]"
                  selectedStates={filters.states}
                  onToggleState={toggleState}
                />
              </div>
              <p className="mt-3 text-sm text-white/50">
                Click a state to explore resources in your area
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section - Soft background */}
      <section className="relative bg-background py-16 lg:py-24">
        <div className="mx-auto max-w-6xl px-6">
          {/* Section header */}
          <div className="mb-10">
            <div className="editorial-divider mb-4" />
            <h2 className="font-display text-2xl font-semibold text-foreground sm:text-3xl">
              Browse by Category
            </h2>
            <p className="mt-2 text-muted-foreground">
              Find resources tailored to your specific needs
            </p>
          </div>

          {/* Category cards grid */}
          <CategoryCards
            selectedCategories={filters.categories}
            onToggleCategory={toggleCategory}
          />

          {/* Sort chips */}
          <div className="mt-8">
            <SortChips
              selectedSort={selectedSort}
              onSortChange={setSelectedSort}
            />
          </div>
        </div>
      </section>

      {/* Trust Indicators Section */}
      <section className="relative border-y border-border bg-card py-12">
        <div className="mx-auto max-w-6xl px-6">
          <div className="grid gap-8 sm:grid-cols-3">
            {trustIndicators.map((indicator) => {
              const Icon = indicator.icon;
              return (
                <div key={indicator.title} className="flex items-start gap-3">
                  <div className="flex-shrink-0 rounded-lg bg-[hsl(var(--v4v-gold)/0.1)] p-2.5">
                    <Icon className="h-5 w-5 text-[hsl(var(--v4v-gold-dark))]" />
                  </div>
                  <div>
                    <h3 className="font-medium text-foreground">
                      {indicator.title}
                    </h3>
                    <p className="mt-0.5 text-sm text-muted-foreground">
                      {indicator.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative bg-background py-16 lg:py-24">
        <div className="mx-auto max-w-6xl px-6">
          {/* Section header */}
          <div className="mb-10 text-center">
            <div className="mx-auto editorial-divider mb-4" />
            <h2 className="font-display text-2xl font-semibold text-foreground sm:text-3xl">
              How It Works
            </h2>
            <p className="mx-auto mt-2 max-w-xl text-muted-foreground">
              Finding veteran resources should be simple
            </p>
          </div>

          {/* Steps */}
          <div className="relative">
            {/* Connecting line (desktop) */}
            <div className="absolute left-0 right-0 top-12 hidden h-px bg-gradient-to-r from-transparent via-border to-transparent lg:block" />

            <div className="grid gap-8 lg:grid-cols-3">
              {steps.map((step) => (
                <div key={step.number} className="relative text-center">
                  {/* Step number */}
                  <div className="relative mx-auto mb-5 inline-flex h-24 w-24 items-center justify-center">
                    <div className="step-circle absolute inset-0 rounded-full" />
                    <span className="relative font-display text-2xl font-semibold text-[hsl(var(--v4v-gold-dark))]">
                      {step.number}
                    </span>
                  </div>

                  {/* Content */}
                  <h3 className="font-display text-lg font-medium text-foreground">
                    {step.title}
                  </h3>
                  <p className="mt-1.5 text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="mt-10 text-center">
            <Link
              href="/search"
              className="btn-primary inline-flex items-center gap-2 rounded-lg px-6 py-3"
            >
              <Search className="h-4 w-4" />
              <span className="text-sm font-medium">Start Searching</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-v4v-navy py-10 text-white">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex flex-col items-center text-center">
            {/* Logo */}
            <h2 className="font-display text-xl font-semibold text-[hsl(var(--v4v-gold))]">Vibe4Vets</h2>

            {/* Transparency statement */}
            <p className="mt-3 max-w-lg text-sm leading-relaxed text-white/60">
              Built with transparency. We aggregate veteran resources from VA.gov,
              DOL, nonprofits, and community organizations—all in one searchable
              directory powered by AI.
            </p>

            {/* Links */}
            <div className="mt-5 flex flex-wrap justify-center gap-4 text-sm">
              <Link href="/search" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Search Resources
              </Link>
              <Link href="/map" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Browse by State
              </Link>
              <Link href="/discover" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Fresh Finds
              </Link>
              <Link href="/admin" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Admin
              </Link>
            </div>

            {/* Copyright */}
            <div className="mt-6 border-t border-white/10 pt-6 text-xs text-white/40">
              <p>All veteran resources in one place</p>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
