import Link from 'next/link';
import { SearchBar } from '@/components/search-bar';
import { Briefcase, GraduationCap, Home as HomeIcon, Scale, Shield, RefreshCw, Search, CheckCircle2, Layers, MapPin, Calendar } from 'lucide-react';

const categories = [
  {
    name: 'Employment',
    slug: 'employment',
    description: 'Job placement, career services, and veteran-friendly employers',
    icon: Briefcase,
    color: 'bg-[hsl(210,70%,45%)]',
    hoverColor: 'hover:bg-[hsl(210,70%,40%)]',
  },
  {
    name: 'Training',
    slug: 'training',
    description: 'Vocational rehabilitation, certifications, and skill-building programs',
    icon: GraduationCap,
    color: 'bg-[hsl(160,50%,40%)]',
    hoverColor: 'hover:bg-[hsl(160,50%,35%)]',
  },
  {
    name: 'Housing',
    slug: 'housing',
    description: 'HUD-VASH, SSVF, transitional housing, and shelter resources',
    icon: HomeIcon,
    color: 'bg-[hsl(25,70%,50%)]',
    hoverColor: 'hover:bg-[hsl(25,70%,45%)]',
  },
  {
    name: 'Legal',
    slug: 'legal',
    description: 'Legal aid, VA appeals assistance, and advocacy services',
    icon: Scale,
    color: 'bg-[hsl(280,40%,45%)]',
    hoverColor: 'hover:bg-[hsl(280,40%,40%)]',
  },
];

const trustIndicators = [
  {
    icon: Shield,
    title: 'Verified Sources',
    description: 'Data from VA.gov, DOL, and trusted nonprofits',
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
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[hsl(var(--v4v-navy))] text-white">
        {/* Layered background gradients */}
        <div className="hero-gradient-layer absolute inset-0" />

        {/* Subtle star pattern overlay */}
        <div className="hero-stars absolute inset-0 opacity-60" />

        {/* Shield silhouette decoration (right side) */}
        <div className="hero-shield absolute -right-20 top-1/2 h-[500px] w-[400px] -translate-y-1/2 opacity-30 lg:opacity-50" />

        {/* Gold accent gradient (enhanced) */}
        <div className="absolute right-0 top-0 h-full w-1/2 opacity-10">
          <div className="h-full w-full bg-gradient-to-l from-[hsl(var(--v4v-gold))] via-[hsl(var(--v4v-gold)/0.5)] to-transparent" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6 py-24 lg:py-32">
          <div className="max-w-3xl">
            {/* Eyebrow text with decorative line */}
            <div className="animate-fade-in-up mb-6 flex items-center gap-4">
              <div className="h-px w-8 bg-[hsl(var(--v4v-gold))]" />
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-[hsl(var(--v4v-gold))]">
                Veteran Resource Directory
              </p>
            </div>

            {/* Main headline - larger with gold underline accent */}
            <h1 className="animate-fade-in-up delay-100 font-display text-4xl font-normal leading-[1.1] sm:text-5xl lg:text-6xl xl:text-7xl" style={{ opacity: 0 }}>
              Resources for Veterans,{' '}
              <span className="gold-underline text-[hsl(var(--v4v-gold))]">Beyond VA.gov</span>
            </h1>

            {/* Subheadline - refined */}
            <p className="animate-fade-in-up delay-200 mt-8 max-w-2xl text-lg leading-relaxed text-white/75 sm:text-xl lg:text-2xl" style={{ opacity: 0 }}>
              We aggregate employment, training, housing, and legal resources from
              across the country—all in one searchable directory.
            </p>

            {/* Search Bar - enhanced container */}
            <div className="animate-fade-in-up delay-300 mt-12" style={{ opacity: 0 }}>
              <div className="hero-search-container rounded-xl bg-white/10 p-3 backdrop-blur-sm transition-all duration-300">
                <SearchBar />
              </div>
              {/* Helper text below search */}
              <p className="mt-3 text-center text-sm text-white/50">
                Try: &quot;job training Texas&quot; or &quot;housing assistance California&quot;
              </p>
            </div>

            {/* Quick stats - enhanced with icons and cards */}
            <div className="animate-fade-in-up delay-400 mt-10 flex flex-wrap gap-4" style={{ opacity: 0 }}>
              <div className="hero-stat stat-shimmer flex items-center gap-3 rounded-lg px-5 py-3">
                <Layers className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
                <div>
                  <span className="font-display text-2xl text-[hsl(var(--v4v-gold))]">4</span>
                  <span className="ml-2 text-sm text-white/70">Categories</span>
                </div>
              </div>
              <div className="hero-stat stat-shimmer flex items-center gap-3 rounded-lg px-5 py-3">
                <MapPin className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
                <div>
                  <span className="font-display text-2xl text-[hsl(var(--v4v-gold))]">50</span>
                  <span className="ml-2 text-sm text-white/70">States Covered</span>
                </div>
              </div>
              <div className="hero-stat stat-shimmer flex items-center gap-3 rounded-lg px-5 py-3">
                <Calendar className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
                <div>
                  <span className="font-display text-2xl text-[hsl(var(--v4v-gold))]">Daily</span>
                  <span className="ml-2 text-sm text-white/70">Updates</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced bottom divider */}
        <div className="hero-divider absolute bottom-0 left-0 right-0" />
      </section>

      {/* Categories Section */}
      <section className="relative bg-[hsl(var(--v4v-cream))] py-20 lg:py-28">
        <div className="mx-auto max-w-6xl px-6">
          {/* Section header */}
          <div className="mb-12 max-w-2xl">
            <div className="editorial-divider mb-4" />
            <h2 className="font-display text-3xl text-[hsl(var(--v4v-navy))] sm:text-4xl">
              Browse by Category
            </h2>
            <p className="mt-3 text-lg text-[hsl(var(--muted-foreground))]">
              Find resources tailored to your specific needs
            </p>
          </div>

          {/* Category cards grid */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {categories.map((category, index) => {
              const Icon = category.icon;
              return (
                <Link
                  key={category.slug}
                  href={`/search?category=${category.slug}`}
                  className="category-card group relative overflow-hidden rounded-xl bg-white p-6 shadow-sm"
                  style={{
                    animationDelay: `${(index + 1) * 100}ms`,
                  }}
                >
                  {/* Color accent bar */}
                  <div className={`absolute left-0 top-0 h-1 w-full ${category.color}`} />

                  {/* Icon */}
                  <div className={`mb-4 inline-flex rounded-lg ${category.color} p-3 text-white transition-transform duration-300 group-hover:scale-110`}>
                    <Icon className="h-6 w-6" />
                  </div>

                  {/* Content */}
                  <h3 className="font-display text-xl text-[hsl(var(--v4v-navy))]">
                    {category.name}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-[hsl(var(--muted-foreground))]">
                    {category.description}
                  </p>

                  {/* Arrow indicator */}
                  <div className="mt-4 flex items-center text-sm font-medium text-[hsl(var(--v4v-gold))] opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                    <span>Explore</span>
                    <svg className="ml-1 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Trust Indicators Section */}
      <section className="border-y border-[hsl(var(--border))] bg-white py-16">
        <div className="mx-auto max-w-6xl px-6">
          <div className="grid gap-8 sm:grid-cols-3">
            {trustIndicators.map((indicator) => {
              const Icon = indicator.icon;
              return (
                <div key={indicator.title} className="flex items-start gap-4">
                  <div className="flex-shrink-0 rounded-full bg-[hsl(var(--v4v-gold)/0.1)] p-3">
                    <Icon className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[hsl(var(--v4v-navy))]">
                      {indicator.title}
                    </h3>
                    <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
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
      <section className="bg-[hsl(var(--v4v-cream))] py-20 lg:py-28">
        <div className="mx-auto max-w-6xl px-6">
          {/* Section header */}
          <div className="mb-12 text-center">
            <div className="mx-auto editorial-divider mb-4" />
            <h2 className="font-display text-3xl text-[hsl(var(--v4v-navy))] sm:text-4xl">
              How It Works
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-lg text-[hsl(var(--muted-foreground))]">
              Finding veteran resources should be simple
            </p>
          </div>

          {/* Steps */}
          <div className="relative">
            {/* Connecting line (desktop) */}
            <div className="absolute left-0 right-0 top-12 hidden h-0.5 bg-gradient-to-r from-transparent via-[hsl(var(--border))] to-transparent lg:block" />

            <div className="grid gap-8 lg:grid-cols-3">
              {steps.map((step) => (
                <div key={step.number} className="relative text-center">
                  {/* Step number */}
                  <div className="relative mx-auto mb-6 inline-flex h-24 w-24 items-center justify-center rounded-full bg-white shadow-sm">
                    <span className="font-display text-3xl text-[hsl(var(--v4v-navy))]">
                      {step.number}
                    </span>
                    {/* Gold accent ring */}
                    <div className="absolute inset-0 rounded-full border-2 border-[hsl(var(--v4v-gold)/0.3)]" />
                  </div>

                  {/* Content */}
                  <h3 className="font-display text-xl text-[hsl(var(--v4v-navy))]">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-[hsl(var(--muted-foreground))]">
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="mt-12 text-center">
            <Link
              href="/search"
              className="inline-flex items-center gap-2 rounded-lg bg-[hsl(var(--v4v-navy))] px-8 py-4 font-semibold text-white transition-all duration-300 hover:bg-[hsl(var(--v4v-navy-light))] hover:shadow-lg"
            >
              <Search className="h-5 w-5" />
              Start Searching
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[hsl(var(--v4v-navy))] py-12 text-white">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex flex-col items-center text-center">
            {/* Logo */}
            <h2 className="font-display text-2xl text-white">Vibe4Vets</h2>

            {/* Transparency statement */}
            <p className="mt-4 max-w-lg text-sm leading-relaxed text-white/60">
              Built with transparency. We use AI and web scraping to aggregate
              veteran resources from official sources, nonprofits, and community
              organizations—going beyond what VA.gov offers alone.
            </p>

            {/* Links */}
            <div className="mt-6 flex gap-6 text-sm">
              <Link href="/search" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Search Resources
              </Link>
              <Link href="/discover" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Fresh Finds
              </Link>
              <Link href="/admin" className="text-white/60 transition-colors hover:text-[hsl(var(--v4v-gold))]">
                Admin
              </Link>
            </div>

            {/* Copyright */}
            <div className="mt-8 border-t border-white/10 pt-8 text-xs text-white/40">
              <p>Built to help veterans find resources beyond VA.gov</p>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
