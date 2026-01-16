import Link from 'next/link';
import { SearchBar } from '@/components/search-bar';
import { Briefcase, GraduationCap, Home as HomeIcon, Scale, Shield, RefreshCw, Search, CheckCircle2, Layers, MapPin, Calendar, ChevronRight } from 'lucide-react';

const categories = [
  {
    name: 'Employment',
    slug: 'employment',
    description: 'Job placement, career services, and veteran-friendly employers',
    icon: Briefcase,
    colorClass: 'bg-v4v-employment',
    mutedBgClass: 'bg-v4v-employment-muted',
    textClass: 'text-v4v-employment',
  },
  {
    name: 'Training',
    slug: 'training',
    description: 'Vocational rehabilitation, certifications, and skill-building programs',
    icon: GraduationCap,
    colorClass: 'bg-v4v-training',
    mutedBgClass: 'bg-v4v-training-muted',
    textClass: 'text-v4v-training',
  },
  {
    name: 'Housing',
    slug: 'housing',
    description: 'HUD-VASH, SSVF, transitional housing, and shelter resources',
    icon: HomeIcon,
    colorClass: 'bg-v4v-housing',
    mutedBgClass: 'bg-v4v-housing-muted',
    textClass: 'text-v4v-housing',
  },
  {
    name: 'Legal',
    slug: 'legal',
    description: 'Legal aid, VA appeals assistance, and advocacy services',
    icon: Scale,
    colorClass: 'bg-v4v-legal',
    mutedBgClass: 'bg-v4v-legal-muted',
    textClass: 'text-v4v-legal',
  },
];

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

        <div className="relative mx-auto max-w-6xl px-6 py-20 lg:py-28">
          <div className="max-w-3xl">
            {/* Eyebrow text */}
            <div className="animate-fade-in-up mb-5 flex items-center gap-3">
              <div className="h-px w-10 bg-[hsl(var(--v4v-gold))]" />
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[hsl(var(--v4v-gold))]">
                Veteran Resource Directory
              </p>
            </div>

            {/* Main headline */}
            <h1
              className="animate-fade-in-up delay-100 font-display text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl"
              style={{ opacity: 0 }}
            >
              Resources for Veterans,{' '}
              <span className="gold-underline text-[hsl(var(--v4v-gold))]">All in One Place</span>
            </h1>

            {/* Subheadline */}
            <p
              className="animate-fade-in-up delay-200 mt-6 max-w-2xl text-base leading-relaxed text-white/70 sm:text-lg"
              style={{ opacity: 0 }}
            >
              We aggregate employment, training, housing, and legal resources from
              across the country—all in one searchable directory.
            </p>

            {/* Search Bar */}
            <div className="animate-fade-in-up delay-300 mt-10" style={{ opacity: 0 }}>
              <div className="hero-search-container rounded-xl p-3">
                <SearchBar />
              </div>
              <p className="mt-3 text-center text-sm text-white/50">
                Try: &quot;job training Texas&quot; or &quot;housing assistance California&quot;
              </p>
            </div>

            {/* Quick stats */}
            <div className="animate-fade-in-up delay-400 mt-10 flex flex-wrap gap-3" style={{ opacity: 0 }}>
              <div className="hero-stat flex items-center gap-2 px-4 py-2.5">
                <Layers className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
                <span className="font-display text-xl text-[hsl(var(--v4v-gold))]">4</span>
                <span className="text-sm text-white/60">Categories</span>
              </div>
              <div className="hero-stat flex items-center gap-2 px-4 py-2.5">
                <MapPin className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
                <span className="font-display text-xl text-[hsl(var(--v4v-gold))]">50</span>
                <span className="text-sm text-white/60">States</span>
              </div>
              <div className="hero-stat flex items-center gap-2 px-4 py-2.5">
                <Calendar className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
                <span className="font-display text-xl text-[hsl(var(--v4v-gold))]">Daily</span>
                <span className="text-sm text-white/60">Updates</span>
              </div>
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
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <Link
                  key={category.slug}
                  href={`/search?category=${category.slug}`}
                  className="soft-card category-card group relative overflow-hidden p-5"
                >
                  {/* Color accent bar */}
                  <div className={`absolute left-0 top-0 h-1 w-full ${category.colorClass} transition-all duration-300 group-hover:h-1.5`} />

                  {/* Icon */}
                  <div className={`mb-3 inline-flex rounded-lg p-2.5 ${category.mutedBgClass} transition-transform duration-300 group-hover:scale-110`}>
                    <Icon className={`h-5 w-5 ${category.textClass}`} />
                  </div>

                  {/* Content */}
                  <h3 className="font-display text-lg font-medium text-foreground">
                    {category.name}
                  </h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                    {category.description}
                  </p>

                  {/* Arrow indicator */}
                  <div className="mt-3 flex items-center text-sm font-medium text-[hsl(var(--v4v-gold-dark))] opacity-0 transition-all duration-300 group-hover:opacity-100">
                    <span>Explore</span>
                    <ChevronRight className="ml-1 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
                  </div>
                </Link>
              );
            })}
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
