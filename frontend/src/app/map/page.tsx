import Link from 'next/link';
import { MapPin } from 'lucide-react';
import { USMap } from '@/components/us-map';

export const metadata = {
  title: 'Find Resources by State | Vibe4Vets',
  description:
    'Explore Veteran resources across the United States. Click on a state to discover employment, training, housing, and legal resources available in your area.',
};

export default function MapPage() {
  return (
    <main className="min-h-screen bg-[hsl(var(--v4v-cream))] pt-14">
      {/* Main Content */}
      <section className="py-12 lg:py-16">
        <div className="mx-auto max-w-6xl px-6">
          {/* Page header */}
          <div className="mb-10">
            <div className="editorial-divider mb-4" />
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-[hsl(var(--v4v-navy))] p-2.5 text-white">
                <MapPin className="h-5 w-5" />
              </div>
              <h1 className="font-display text-3xl text-[hsl(var(--v4v-navy))] sm:text-4xl">
                Find Resources by State
              </h1>
            </div>
            <p className="mt-4 max-w-2xl text-lg text-[hsl(var(--muted-foreground))]">
              Click on any state to discover Veteran resources available in that
              area. We aggregate employment, training, housing, and legal
              resources from trusted sources nationwide.
            </p>
          </div>

          {/* Map Card */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-white p-6 shadow-sm lg:p-8">
            <USMap className="w-full" />
          </div>

          {/* Territories */}
          <div className="mt-6 rounded-xl border border-[hsl(var(--border))] bg-white p-6 shadow-sm">
            <h2 className="font-display text-xl text-[hsl(var(--v4v-navy))]">
              U.S. Territories
            </h2>
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              Territories aren&apos;t shown on the map. Use these links to browse resources.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {[
                { code: 'PR', label: 'Puerto Rico' },
                { code: 'GU', label: 'Guam' },
                { code: 'VI', label: 'U.S. Virgin Islands' },
                { code: 'AS', label: 'American Samoa' },
                { code: 'MP', label: 'Northern Mariana Islands' },
              ].map((t) => (
                <Link
                  key={t.code}
                  href={`/search?state=${t.code}`}
                  className="rounded-full border border-[hsl(var(--border))] bg-[hsl(var(--v4v-cream))] px-3 py-1.5 text-sm text-[hsl(var(--v4v-navy))] transition-colors hover:bg-white"
                >
                  {t.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Info cards */}
          <div className="mt-10 grid gap-6 sm:grid-cols-3">
            <div className="rounded-lg border border-[hsl(var(--border))] bg-white p-5">
              <div className="mb-3 inline-flex rounded-lg bg-[hsl(var(--v4v-employment))] p-2 text-white">
                <MapPin className="h-4 w-4" />
              </div>
              <h3 className="font-semibold text-[hsl(var(--v4v-navy))]">
                Location-Based Search
              </h3>
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                Find resources tailored to your specific state and locality.
              </p>
            </div>
            <div className="rounded-lg border border-[hsl(var(--border))] bg-white p-5">
              <div className="mb-3 inline-flex rounded-lg bg-[hsl(var(--v4v-training))] p-2 text-white">
                <MapPin className="h-4 w-4" />
              </div>
              <h3 className="font-semibold text-[hsl(var(--v4v-navy))]">
                50 States Coverage
              </h3>
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                Resources available across all 50 states plus territories.
              </p>
            </div>
            <div className="rounded-lg border border-[hsl(var(--border))] bg-white p-5">
              <div className="mb-3 inline-flex rounded-lg bg-[hsl(var(--v4v-housing))] p-2 text-white">
                <MapPin className="h-4 w-4" />
              </div>
              <h3 className="font-semibold text-[hsl(var(--v4v-navy))]">
                Regular Updates
              </h3>
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                Data refreshed daily from official and trusted sources.
              </p>
            </div>
          </div>
        </div>
      </section>

    </main>
  );
}
