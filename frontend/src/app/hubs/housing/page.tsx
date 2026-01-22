import Link from 'next/link';
import { Home as HomeIcon, Building, Users, Shield, Heart, ArrowLeft } from 'lucide-react';
import { HubCard, type HubResource } from '@/components/HubCard';

const housingResources: HubResource[] = [
  {
    name: 'HUD-VASH Program',
    description: 'HUD-VA Supportive Housing combines rental assistance vouchers with VA case management and clinical services for Veterans experiencing homelessness.',
    url: 'https://www.va.gov/homeless/hud-vash.asp',
    icon: HomeIcon,
  },
  {
    name: 'SSVF Provider Directory',
    description: 'Supportive Services for Veteran Families helps prevent housing instability and provides rapid re-housing for Veterans and their families.',
    url: 'https://www.va.gov/homeless/ssvf/',
    icon: Users,
  },
  {
    name: 'National Coalition for Homeless Veterans',
    description: 'Advocacy organization connecting Veterans experiencing homelessness with local service providers and emergency resources nationwide.',
    url: 'https://nchv.org/',
    icon: Shield,
  },
  {
    name: 'VA Housing Programs for Veterans',
    description: 'Comprehensive VA programs addressing housing needs including outreach, transitional housing, and permanent housing.',
    url: 'https://www.va.gov/homeless/',
    icon: Building,
  },
  {
    name: 'Veterans Inc.',
    description: 'New England\'s largest provider of support services for Veterans, offering housing, employment, and comprehensive assistance.',
    url: 'https://www.veteransinc.org/',
    icon: Heart,
  },
  {
    name: 'VA Home Loan Guarantee',
    description: 'VA-backed home loans with no down payment requirement, competitive rates, and no private mortgage insurance for eligible Veterans.',
    url: 'https://www.va.gov/housing-assistance/home-loans/',
    icon: HomeIcon,
  },
];

export default function HousingHubPage() {
  return (
    <main className="min-h-screen bg-[hsl(var(--v4v-cream))] pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[hsl(25,70%,50%)] text-white">
        <div className="absolute right-0 top-0 h-full w-1/3 opacity-10">
          <div className="h-full w-full bg-gradient-to-l from-white to-transparent" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6 py-16 lg:py-20">
          <Link
            href="/"
            className="mb-6 inline-flex items-center gap-2 text-sm text-white/70 transition-colors hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>

          <div className="flex items-center gap-4">
            <div className="rounded-xl bg-white/20 p-4">
              <HomeIcon className="h-10 w-10" />
            </div>
            <div>
              <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl">
                Housing Resources
              </h1>
              <p className="mt-2 text-lg text-white/80">
                HUD-VASH, SSVF, transitional housing, and shelter resources
              </p>
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white/30 to-transparent" />
      </section>

      {/* Resources Grid */}
      <section className="py-12 lg:py-16">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-8">
            <div className="editorial-divider mb-4" />
            <h2 className="font-display text-2xl text-[hsl(var(--v4v-navy))]">
              Trusted Housing Resources
            </h2>
            <p className="mt-2 text-[hsl(var(--muted-foreground))]">
              Official programs and organizations helping Veterans find stable housing
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {housingResources.map((resource) => (
              <HubCard
                key={resource.name}
                resource={resource}
                category="housing"
              />
            ))}
          </div>

          {/* Emergency Notice */}
          <div className="mt-12 rounded-xl border-2 border-[hsl(25,70%,50%)] bg-[hsl(25,70%,97%)] p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Need Immediate Help?
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              If you&apos;re a Veteran experiencing homelessness or a housing crisis, call the National Call
              Center for Homeless Veterans at <strong className="text-[hsl(var(--v4v-navy))]">1-877-4AID-VET (1-877-424-3838)</strong>.
              Available 24/7.
            </p>
          </div>

          {/* Search CTA */}
          <div className="mt-6 rounded-xl border border-[hsl(var(--border))] bg-white p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Find Local Resources
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Search our database for housing resources in your area, including local shelters,
              transitional housing, and Veteran-specific programs.
            </p>
            <Link
              href="/search?category=housing"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-[hsl(var(--v4v-navy))] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[hsl(var(--v4v-navy-light))]"
            >
              Search Housing Resources
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
