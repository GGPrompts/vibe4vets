import Link from 'next/link';
import { Scale, FileText, Users, Shield, Gavel, ArrowLeft } from 'lucide-react';
import { HubCard, type HubResource } from '@/components/HubCard';

const legalResources: HubResource[] = [
  {
    name: 'VA Appeals Process',
    description: 'Official information on appealing VA decisions, including the Board of Veterans\' Appeals and decision review options.',
    url: 'https://www.va.gov/decision-reviews/',
    icon: FileText,
  },
  {
    name: 'Accredited VA Attorneys',
    description: 'Find VA-accredited attorneys, claims agents, and representatives who can help with benefits claims and appeals.',
    url: 'https://www.va.gov/vso/',
    icon: Scale,
  },
  {
    name: 'Legal Services Corporation',
    description: 'Find free civil legal aid providers in your area, many with programs specifically serving veterans.',
    url: 'https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help',
    icon: Gavel,
  },
  {
    name: 'National Veterans Legal Services Program',
    description: 'Nonprofit providing free legal assistance to veterans on VA claims, discharge upgrades, and military records corrections.',
    url: 'https://www.nvlsp.org/',
    icon: Shield,
  },
  {
    name: 'American Bar Association Veterans Legal',
    description: 'ABA initiative connecting veterans with pro bono legal services for military-related issues and civil legal needs.',
    url: 'https://www.americanbar.org/groups/legal_services/milvets/',
    icon: Users,
  },
  {
    name: 'Stateside Legal',
    description: 'Free legal information and resources for military members, veterans, and their families on common legal issues.',
    url: 'https://statesidelegal.org/',
    icon: FileText,
  },
];

export default function LegalHubPage() {
  return (
    <main className="min-h-screen bg-[hsl(var(--v4v-cream))]">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[hsl(280,40%,45%)] text-white">
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
              <Scale className="h-10 w-10" />
            </div>
            <div>
              <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl">
                Legal Resources
              </h1>
              <p className="mt-2 text-lg text-white/80">
                Legal aid, VA appeals assistance, and advocacy services
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
              Trusted Legal Resources
            </h2>
            <p className="mt-2 text-[hsl(var(--muted-foreground))]">
              Official programs and organizations providing legal assistance to veterans
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {legalResources.map((resource) => (
              <HubCard
                key={resource.name}
                resource={resource}
                category="legal"
              />
            ))}
          </div>

          {/* Disclaimer */}
          <div className="mt-12 rounded-xl border border-[hsl(var(--border))] bg-white p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Important Notice
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              The resources listed here are for informational purposes. We do not provide legal
              advice. For specific legal matters, please consult with a qualified attorney or
              VA-accredited representative.
            </p>
          </div>

          {/* Search CTA */}
          <div className="mt-6 rounded-xl border border-[hsl(var(--border))] bg-white p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Find Local Legal Aid
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Search our database for legal resources in your area, including veteran legal clinics,
              pro bono attorneys, and legal aid organizations.
            </p>
            <Link
              href="/search?category=legal"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-[hsl(var(--v4v-navy))] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[hsl(var(--v4v-navy-light))]"
            >
              Search Legal Resources
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
