import Link from 'next/link';
import { GraduationCap, BookOpen, Award, Building2, Wrench, ArrowLeft } from 'lucide-react';
import { HubCard, type HubResource } from '@/components/HubCard';

const trainingResources: HubResource[] = [
  {
    name: 'VR&E Program (Chapter 31)',
    description: 'Veteran Readiness and Employment helps veterans with service-connected disabilities prepare for, find, and maintain suitable careers.',
    url: 'https://www.va.gov/careers-employment/vocational-rehabilitation/',
    icon: GraduationCap,
  },
  {
    name: 'GI Bill Benefits',
    description: 'Education benefits including tuition, housing, and supplies for college, trade schools, and other approved programs.',
    url: 'https://www.va.gov/education/about-gi-bill-benefits/',
    icon: BookOpen,
  },
  {
    name: 'VA Apprenticeship Programs',
    description: 'On-the-job training and apprenticeship programs where you can learn while earning, with GI Bill support.',
    url: 'https://www.va.gov/education/about-gi-bill-benefits/how-to-use-benefits/on-the-job-training-apprenticeships/',
    icon: Wrench,
  },
  {
    name: 'Vet Center Career Services',
    description: 'Community-based counseling centers offering career development, resume help, and transition assistance.',
    url: 'https://www.vetcenter.va.gov/',
    icon: Building2,
  },
  {
    name: 'SkillBridge Program',
    description: 'DOD program allowing service members to gain civilian work experience through internships during their last 180 days of service.',
    url: 'https://skillbridge.osd.mil/',
    icon: Award,
  },
  {
    name: 'VA WEAMS School Search',
    description: 'Search VA-approved schools, employers, and training programs eligible for GI Bill benefits.',
    url: 'https://www.va.gov/education/gi-bill-comparison-tool/',
    icon: GraduationCap,
  },
];

export default function TrainingHubPage() {
  return (
    <main className="min-h-screen bg-[hsl(var(--v4v-cream))]">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[hsl(160,50%,40%)] text-white">
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
              <GraduationCap className="h-10 w-10" />
            </div>
            <div>
              <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl">
                Training Resources
              </h1>
              <p className="mt-2 text-lg text-white/80">
                Vocational rehabilitation, certifications, and skill-building programs
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
              Trusted Training Resources
            </h2>
            <p className="mt-2 text-[hsl(var(--muted-foreground))]">
              Official programs helping veterans build skills and advance their careers
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {trainingResources.map((resource) => (
              <HubCard
                key={resource.name}
                resource={resource}
                category="training"
              />
            ))}
          </div>

          {/* GI Bill Tip */}
          <div className="mt-12 rounded-xl border-2 border-[hsl(160,50%,40%)] bg-[hsl(160,50%,97%)] p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Maximize Your Benefits
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Before enrolling in any program, check if it&apos;s approved for GI Bill benefits using
              the VA Comparison Tool. This helps ensure you&apos;re getting the most value from your
              education benefits.
            </p>
          </div>

          {/* Search CTA */}
          <div className="mt-6 rounded-xl border border-[hsl(var(--border))] bg-white p-6">
            <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))]">
              Find Local Training
            </h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Search our database for training programs in your area, including trade schools,
              certification programs, and workforce development initiatives.
            </p>
            <Link
              href="/search?category=training"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-[hsl(var(--v4v-navy))] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[hsl(var(--v4v-navy-light))]"
            >
              Search Training Resources
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
