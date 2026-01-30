'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  Shield,
  RefreshCw,
  CheckCircle2,
  Database,
  Cpu,
  Eye,
  Lock,
  ChevronDown,
  Search,
  ArrowRight,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BackToTop } from '@/components/BackToTop';
import { AIStatsWidget } from '@/components/AIStatsWidget';

// Lightbox component for viewing screenshots
function ImageLightbox({
  src,
  alt,
  isOpen,
  onClose
}: {
  src: string;
  alt: string;
  isOpen: boolean;
  onClose: () => void;
}) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
      onClick={onClose}
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
        aria-label="Close"
      >
        <X className="h-6 w-6 text-white" />
      </button>
      <div className="relative max-w-[90vw] max-h-[90vh]" onClick={(e) => e.stopPropagation()}>
        <Image
          src={src}
          alt={alt}
          width={1920}
          height={1080}
          className="object-contain max-h-[90vh] w-auto rounded-lg"
        />
        <p className="text-white/80 text-center mt-4 text-sm">{alt}</p>
      </div>
    </div>
  );
}

interface ExpandableSectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

function ExpandableSection({ title, icon, children, defaultOpen = false }: ExpandableSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="rounded-2xl border-2 border-border bg-white dark:bg-zinc-900 shadow-md hover:shadow-lg transition-shadow duration-300">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between p-6 text-left"
      >
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-[hsl(var(--v4v-gold)/0.15)] to-[hsl(var(--v4v-gold)/0.05)]">
            {icon}
          </div>
          <h3 className="font-display text-xl font-medium text-foreground">{title}</h3>
        </div>
        <ChevronDown
          className={`h-5 w-5 text-muted-foreground transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>
      {isOpen && (
        <div className="border-t border-border/50 px-6 pb-6 pt-4">
          {children}
        </div>
      )}
    </div>
  );
}

const sourceTiers = [
  {
    tier: 1,
    score: '100%',
    examples: 'VA.gov, Department of Labor, HUD',
    description: 'Official government sources with verified accuracy',
    color: 'bg-green-500',
  },
  {
    tier: 2,
    score: '80%',
    examples: 'DAV, VFW, American Legion',
    description: 'Major Veteran service organizations',
    color: 'bg-blue-500',
  },
  {
    tier: 3,
    score: '60%',
    examples: 'State Veteran agencies',
    description: 'State-level official resources',
    color: 'bg-yellow-500',
  },
  {
    tier: 4,
    score: '40%',
    examples: 'Community directories',
    description: 'Local and community-based resources',
    color: 'bg-orange-500',
  },
];

const dataSources = [
  {
    name: 'VA Developer API',
    type: 'Official API',
    description: 'Facilities, services, and programs directly from the VA',
  },
  {
    name: 'CareerOneStop API',
    type: 'Official API',
    description: 'Job resources from the Department of Labor',
  },
  {
    name: 'USAJobs API',
    type: 'Official API',
    description: 'Federal employment opportunities',
  },
  {
    name: 'VA.gov Pages',
    type: 'Structured Data',
    description: 'Employment and benefit program information',
  },
  {
    name: 'HUD-VASH',
    type: 'Structured Data',
    description: 'Housing assistance program listings',
  },
  {
    name: 'VSO Websites',
    type: 'Community',
    description: 'Veteran Service Organization resources',
  },
];

const screenshots = [
  {
    src: '/about/ParallelAgents.png',
    alt: '10 AI agents running in parallel, each building a different data connector',
    title: 'Parallel Agent Grid',
    description: '10 AI agents building data connectors simultaneously—Vet Centers, GPD Shelters, SkillBridge, and more.',
  },
  {
    src: '/about/OpusAndHaikus.png',
    alt: '27 AI agents with a mix of Opus and Haiku models working on different tasks',
    title: 'Opus + Haiku Swarm',
    description: '27 agents running together—Opus for complex tasks, Haiku for research and data extraction.',
  },
  {
    src: '/about/HaikuResearchSwarm.png',
    alt: 'Research task queue showing parallel Haiku agents exploring different data sources',
    title: 'Research Swarm',
    description: 'Haiku agents researching Veteran resources across dozens of data sources in parallel.',
  },
];

export default function AboutPage() {
  const [lightboxImage, setLightboxImage] = useState<typeof screenshots[0] | null>(null);

  return (
    <main className="min-h-screen pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-[hsl(var(--v4v-bg-base))] via-[hsl(var(--v4v-bg-elevated))] to-[hsl(var(--v4v-bg-base))]">
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute left-1/4 top-1/3 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.08)] blur-3xl" />
          <div className="absolute right-1/3 bottom-0 h-48 w-48 rounded-full bg-[hsl(var(--v4v-employment)/0.06)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-4xl px-6 py-16 lg:py-20">
          <div className="text-center">
            <h1 className="animate-fade-in-up font-display text-4xl font-semibold text-foreground sm:text-5xl" style={{ opacity: 0 }}>
              About{' '}
              <span className="text-[hsl(var(--v4v-gold-dark))]">VRD.ai</span>
            </h1>
            <p className="animate-fade-in-up delay-100 mt-4 text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]" style={{ opacity: 0 }}>
              Veteran Resource Directory
            </p>
            <p className="animate-fade-in-up delay-200 mt-6 max-w-2xl mx-auto text-lg text-muted-foreground sm:text-xl" style={{ opacity: 0 }}>
              We believe Veterans deserve a transparent, easy-to-use directory of resources.
              Here&apos;s how we build and maintain it.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Statement */}
      <section className="relative bg-v4v-navy text-white py-16">
        <div className="absolute inset-0">
          <div className="hero-gradient absolute inset-0" />
          <div className="hero-pattern absolute inset-0" />
        </div>
        <div className="relative mx-auto max-w-4xl px-6 text-center">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="h-px w-10 bg-gradient-to-r from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
            <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold))]">Our Mission</span>
            <div className="h-px w-10 bg-gradient-to-l from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
          </div>
          <p className="text-xl leading-relaxed text-white/90 sm:text-2xl">
            VRD.ai aggregates Veteran resources from VA.gov, the Department of Labor,
            nonprofits, and community organizations into one searchable directory.
            We&apos;re transparent about using web scraping and AI to help Veterans find
            resources that go <span className="text-[hsl(var(--v4v-gold))]">beyond VA.gov</span>.
          </p>
        </div>
      </section>

      {/* AI Transparency Section */}
      <section className="py-16 bg-background">
        <div className="mx-auto max-w-4xl px-6">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="h-px w-10 bg-gradient-to-r from-transparent to-border" />
              <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]">
                AI Transparency
              </span>
              <div className="h-px w-10 bg-gradient-to-l from-transparent to-border" />
            </div>
            <h2 className="font-display text-2xl font-medium text-foreground sm:text-3xl mb-3">
              How Our AI Works
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              We believe in radical transparency. Here&apos;s real-time data on how our AI-powered
              system discovers and verifies Veteran resources.
            </p>
          </div>
          <AIStatsWidget />

          {/* AI Development Screenshots */}
          <div className="mt-12">
            <h3 className="font-display text-xl font-medium text-foreground text-center mb-6">
              Built by AI Agents Working in Parallel
            </h3>
            <p className="text-muted-foreground text-center mb-8 max-w-2xl mx-auto">
              VRD.ai was built using Claude AI agents (Opus and Haiku models) working simultaneously
              on different parts of the codebase. Here&apos;s what that looks like:
            </p>
            <div className="grid gap-6 md:grid-cols-3">
              {screenshots.map((screenshot) => (
                <button
                  key={screenshot.src}
                  onClick={() => setLightboxImage(screenshot)}
                  className="rounded-xl border-2 border-border bg-white dark:bg-zinc-900 overflow-hidden shadow-md hover:shadow-xl hover:border-[hsl(var(--v4v-gold))] transition-all duration-300 text-left group"
                >
                  <div className="aspect-video relative">
                    <Image
                      src={screenshot.src}
                      alt={screenshot.alt}
                      fill
                      className="object-cover object-top group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                      <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/70 text-white text-xs px-3 py-1.5 rounded-full">
                        Click to enlarge
                      </span>
                    </div>
                  </div>
                  <div className="p-4">
                    <h4 className="font-medium text-foreground text-sm mb-1">{screenshot.title}</h4>
                    <p className="text-xs text-muted-foreground">
                      {screenshot.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Expandable Sections */}
      <section className="py-16 bg-[hsl(var(--v4v-bg-muted))]">
        <div className="mx-auto max-w-4xl px-6 space-y-4">
          {/* How Resources Are Gathered */}
          <ExpandableSection
            title="How Resources Are Gathered"
            icon={<Database className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
            defaultOpen={true}
          >
            <p className="text-muted-foreground mb-6">
              We use a &quot;connector&quot; system to pull data from multiple sources. Each connector
              is specialized for a specific data source, ensuring we extract accurate information.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              {dataSources.map((source) => (
                <div
                  key={source.name}
                  className="rounded-xl border border-border bg-muted/50 p-4"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-foreground">{source.name}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold-dark))]">
                      {source.type}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{source.description}</p>
                </div>
              ))}
            </div>
          </ExpandableSection>

          {/* Trust Scoring */}
          <ExpandableSection
            title="Trust Scoring"
            icon={<Shield className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
          >
            <p className="text-muted-foreground mb-6">
              Every resource has a trust score calculated from two factors:
              <strong className="text-foreground"> reliability</strong> (based on the source tier) and{' '}
              <strong className="text-foreground">freshness</strong> (how recently the resource was verified).
            </p>
            <div className="rounded-xl border border-border bg-muted/50 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="font-mono text-sm text-muted-foreground bg-muted/50 px-3 py-1.5 rounded-lg">
                  Trust Score = Reliability × Freshness
                </div>
              </div>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong className="text-foreground">Reliability</strong> is determined by the source tier (see below)</span>
                </li>
                <li className="flex items-start gap-2">
                  <RefreshCw className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span><strong className="text-foreground">Freshness</strong> decays over time since last verification</span>
                </li>
              </ul>
            </div>
          </ExpandableSection>

          {/* Source Tiers */}
          <ExpandableSection
            title="Source Tiers"
            icon={<Eye className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
          >
            <p className="text-muted-foreground mb-6">
              We classify data sources into four tiers based on their reliability.
              Higher-tier sources are prioritized in search results.
            </p>
            <div className="space-y-3">
              {sourceTiers.map((tier) => (
                <div
                  key={tier.tier}
                  className="flex items-center gap-4 rounded-xl border border-border bg-muted/50 p-4"
                >
                  <div className="flex items-center gap-3 min-w-[80px]">
                    <div className={`h-3 w-3 rounded-full ${tier.color}`} />
                    <span className="font-medium text-foreground">Tier {tier.tier}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-muted-foreground">{tier.description}</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">{tier.examples}</p>
                  </div>
                  <div className="text-sm font-medium text-[hsl(var(--v4v-gold-dark))]">
                    {tier.score}
                  </div>
                </div>
              ))}
            </div>
          </ExpandableSection>

          {/* Data Freshness */}
          <ExpandableSection
            title="Data Freshness"
            icon={<RefreshCw className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
          >
            <p className="text-muted-foreground mb-6">
              Stale data is a major problem with resource directories. We actively combat this
              with automated refresh schedules.
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Automated Refresh</h4>
                <p className="text-sm text-muted-foreground">
                  Our connectors run on scheduled jobs to pull the latest data from sources automatically.
                </p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Freshness Decay</h4>
                <p className="text-sm text-muted-foreground">
                  Resources that haven&apos;t been verified recently have their trust scores gradually reduced.
                </p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Change Detection</h4>
                <p className="text-sm text-muted-foreground">
                  When source data changes, we detect it and update our records with full audit trail.
                </p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Source Health</h4>
                <p className="text-sm text-muted-foreground">
                  We monitor all data sources for availability and flag any that become unreachable.
                </p>
              </div>
            </div>
          </ExpandableSection>

          {/* Human Review */}
          <ExpandableSection
            title="Human Review Process"
            icon={<CheckCircle2 className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
          >
            <p className="text-muted-foreground mb-6">
              Not everything can be automated. Certain changes require human verification
              to ensure accuracy.
            </p>
            <div className="rounded-xl border border-border bg-muted/50 p-6">
              <h4 className="font-medium text-foreground mb-3">Changes that trigger review:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--v4v-gold))]" />
                  Phone number changes
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--v4v-gold))]" />
                  Address or location updates
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--v4v-gold))]" />
                  Eligibility criteria changes
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--v4v-gold))]" />
                  New resources from lower-tier sources
                </li>
              </ul>
              <p className="text-sm text-muted-foreground mt-4">
                All flagged changes go into a review queue where they&apos;re verified before
                being published.
              </p>
            </div>
          </ExpandableSection>

          {/* AI Usage */}
          <ExpandableSection
            title="AI & Automation"
            icon={<Cpu className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
          >
            <p className="text-muted-foreground mb-6">
              We use AI to enhance our resource discovery and search capabilities.
              Here&apos;s how:
            </p>
            <div className="space-y-4">
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Resource Extraction</h4>
                <p className="text-sm text-muted-foreground">
                  AI helps parse unstructured web content to extract resource details like
                  contact information, eligibility criteria, and service descriptions.
                </p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Search Enhancement</h4>
                <p className="text-sm text-muted-foreground">
                  Semantic search understands the intent behind your queries, not just keywords.
                  Ask natural questions like &quot;housing help for homeless Veterans in Texas.&quot;
                </p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-4">
                <h4 className="font-medium text-foreground mb-2">Match Explanations</h4>
                <p className="text-sm text-muted-foreground">
                  Search results explain why each resource matched your query, so you understand
                  the relevance at a glance.
                </p>
              </div>
            </div>
          </ExpandableSection>

          {/* Privacy & No PII */}
          <ExpandableSection
            title="Privacy & No PII Policy"
            icon={<Lock className="h-6 w-6 text-[hsl(var(--v4v-gold-dark))]" />}
          >
            <p className="text-muted-foreground mb-6">
              Your privacy matters. We&apos;ve designed VRD.ai with a strict no-PII policy.
            </p>
            <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-6">
              <h4 className="font-medium text-foreground mb-4 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                What we DON&apos;T collect:
              </h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  No user accounts required
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  No Veteran personal information stored
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  No service records or military history
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  No tracking of individual searches
                </li>
              </ul>
              <p className="text-sm text-muted-foreground mt-4">
                Search works without accounts. We only collect anonymous, aggregated analytics
                to improve the service.
              </p>
            </div>
          </ExpandableSection>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-b from-card to-[hsl(var(--v4v-bg-muted))] py-16">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h2 className="font-display text-2xl font-medium text-foreground sm:text-3xl">
            Ready to find resources?
          </h2>
          <p className="mt-3 text-muted-foreground">
            Start searching our directory of Veteran resources today.
          </p>
          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Button asChild size="lg" className="btn-gold gap-2 rounded-xl px-8">
              <Link href="/search">
                <Search className="h-5 w-5" />
                Search Resources
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="gap-2 rounded-xl px-8">
              <Link href="/">
                <ArrowRight className="h-5 w-5" />
                Back to Home
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative overflow-hidden bg-v4v-navy py-14 text-white">
        <div className="absolute inset-0">
          <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.05)] blur-3xl" />
          <div className="absolute -left-32 -bottom-32 h-64 w-64 rounded-full bg-[hsl(var(--v4v-gold)/0.03)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          <div className="flex flex-col items-center text-center">
            {/* Logo */}
            <Link href="/" className="group">
              <Image
                src="/vrd-logo.png"
                alt="VRD.ai - Veteran Resource Directory"
                width={400}
                height={150}
                className="h-24 sm:h-28 w-auto transition-all duration-300 group-hover:scale-105"
              />
            </Link>
            <p className="mt-2 text-sm text-[hsl(var(--v4v-gold))] font-medium">
              Veteran Resource Directory
            </p>

            <p className="mt-4 max-w-lg text-base leading-relaxed text-white/70">
              Built with transparency. We aggregate Veteran resources from VA.gov,
              DOL, nonprofits, and community organizations—all in one searchable
              directory powered by AI.
            </p>

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

            <div className="mt-8 flex items-center gap-4 text-white/20">
              <div className="h-px w-16 bg-gradient-to-r from-transparent to-white/20" />
              <span className="text-lg text-[hsl(var(--v4v-gold)/0.5)]">*</span>
              <div className="h-px w-16 bg-gradient-to-l from-transparent to-white/20" />
            </div>

            <p className="mt-4 text-sm text-white/50">
              Helping Veterans find resources, one search at a time
            </p>
          </div>
        </div>
      </footer>

      <BackToTop />

      {/* Screenshot Lightbox */}
      {lightboxImage && (
        <ImageLightbox
          src={lightboxImage.src}
          alt={lightboxImage.alt}
          isOpen={!!lightboxImage}
          onClose={() => setLightboxImage(null)}
        />
      )}
    </main>
  );
}
