import Link from 'next/link';
import { Briefcase, Building2, Users, Target, Award, ArrowLeft } from 'lucide-react';
import { HubCard, type HubResource } from '@/components/HubCard';

const employmentResources: HubResource[] = [
  {
    name: 'VA Careers & Employment',
    description: 'Official VA employment resources including career counseling, job training, and resume help for transitioning service members and veterans.',
    url: 'https://www.va.gov/careers-employment/',
    icon: Briefcase,
  },
  {
    name: 'DOL Veterans\' Employment & Training',
    description: 'Department of Labor programs providing employment resources, job training, and placement services specifically for veterans.',
    url: 'https://www.dol.gov/agencies/vets',
    icon: Building2,
  },
  {
    name: 'CareerOneStop',
    description: 'Sponsored by DOL, offering career exploration, training, and job search resources including veteran-specific pathways.',
    url: 'https://www.careeronestop.org/Veterans/default.aspx',
    icon: Target,
  },
  {
    name: 'Hire Heroes USA',
    description: 'Free career services for transitioning military, veterans, and military spouses including coaching and job placement.',
    url: 'https://www.hireheroesusa.org/',
    icon: Users,
  },
  {
    name: 'American Corporate Partners',
    description: 'Free mentoring program connecting veterans with corporate professionals for career guidance and networking.',
    url: 'https://www.acp-usa.org/',
    icon: Award,
  },
  {
    name: 'USAJobs',
    description: 'Official federal government job board with veterans\' preference hiring and dedicated veteran job listings.',
    url: 'https://www.usajobs.gov/Help/working-in-government/unique-hiring-paths/veterans/',
    icon: Building2,
  },
];

export default function EmploymentHubPage() {
  return (
    <main className="min-h-screen bg-[hsl(var(--v4v-cream))]">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[hsl(210,70%,45%)] text-white">
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
              <Briefcase className="h-10 w-10" />
            </div>
            <div>
              <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl">
                Employment Resources
              </h1>
              <p className="mt-2 text-lg text-white/80">
                Job placement, career services, and veteran-friendly employers
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
              Trusted Employment Resources
            </h2>
            <p className="mt-2 text-[hsl(var(--muted-foreground))]">
              Official government programs and established nonprofits helping veterans find careers
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {employmentResources.map((resource) => (
              <HubCard
                key={resource.name}
                resource={resource}
                category="employment"
              />
            ))}
          </div>

          {/* Additional Info */}
          <div className="mt-12 rounded-xl border border-[hsl(var(--border))] bg-white p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Need More Help?
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Search our full database for employment resources in your area, including local
              veteran service organizations and state-specific programs.
            </p>
            <Link
              href="/search?category=employment"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-[hsl(var(--v4v-navy))] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[hsl(var(--v4v-navy-light))]"
            >
              Search Employment Resources
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
