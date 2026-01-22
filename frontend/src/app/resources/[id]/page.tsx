'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import {
  Phone,
  Globe,
  MapPin,
  Clock,
  FileText,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Briefcase,
  BookOpen,
  Home,
  Scale,
  UtensilsCrossed,
  Award,
} from 'lucide-react';
import api, { type Resource } from '@/lib/api';
import { useAnalytics } from '@/lib/useAnalytics';
import { cn } from '@/lib/utils';
import { ReportFeedbackModal } from '@/components/ReportFeedbackModal';
import { BookmarkButton } from '@/components/bookmark-button';

const categoryColors: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.12)] text-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training)/0.12)] text-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.12)] text-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.12)] text-[hsl(var(--v4v-legal))]',
  food: 'bg-[hsl(var(--v4v-food)/0.12)] text-[hsl(var(--v4v-food))]',
  benefits: 'bg-[hsl(var(--v4v-benefits)/0.12)] text-[hsl(var(--v4v-benefits))]',
};

const categoryGradients: Record<string, string> = {
  employment: 'from-[hsl(var(--v4v-employment))] to-[hsl(215,70%,40%)]',
  training: 'from-[hsl(var(--v4v-training))] to-[hsl(165,55%,32%)]',
  housing: 'from-[hsl(var(--v4v-housing))] to-[hsl(24,75%,42%)]',
  legal: 'from-[hsl(var(--v4v-legal))] to-[hsl(265,50%,45%)]',
  food: 'from-[hsl(var(--v4v-food))] to-[hsl(145,55%,32%)]',
  benefits: 'from-[hsl(var(--v4v-benefits))] to-[hsl(340,55%,40%)]',
};

const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: BookOpen,
  housing: Home,
  legal: Scale,
  food: UtensilsCrossed,
  benefits: Award,
};

function IntakeCard({ resource }: { resource: Resource }) {
  const location = resource.location;
  const intake = location?.intake;
  const eligibility = location?.eligibility;
  const verification = location?.verification;

  // If no intake info available, don't render
  if (!intake && !eligibility?.docs_required?.length) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <FileText className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
          How to Apply
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Intake Contact Methods */}
        <div className="space-y-3">
          {intake?.phone && (
            <a
              href={`tel:${intake.phone}`}
              className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/40">
                <Phone className="h-5 w-5 text-green-700 dark:text-green-400" />
              </div>
              <div>
                <p className="font-medium">Call to Apply</p>
                <p className="text-sm text-muted-foreground">{intake.phone}</p>
              </div>
            </a>
          )}

          {intake?.url && (
            <a
              href={intake.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/40">
                <Globe className="h-5 w-5 text-blue-700 dark:text-blue-400" />
              </div>
              <div>
                <p className="font-medium">Apply Online</p>
                <p className="text-sm text-muted-foreground">Visit website</p>
              </div>
            </a>
          )}

          {location?.address && (
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                `${location.address}, ${location.city}, ${location.state}`
              )}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/40">
                <MapPin className="h-5 w-5 text-purple-700 dark:text-purple-400" />
              </div>
              <div>
                <p className="font-medium">Get Directions</p>
                <p className="text-sm text-muted-foreground">
                  {location.city}, {location.state}
                </p>
              </div>
            </a>
          )}
        </div>

        {/* Intake Hours */}
        {intake?.hours && (
          <>
            <Separator />
            <div className="flex items-start gap-3">
              <Clock className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Intake Hours</p>
                <p className="text-sm text-muted-foreground">{intake.hours}</p>
              </div>
            </div>
          </>
        )}

        {/* Intake Notes */}
        {intake?.notes && (
          <div className="rounded-lg bg-amber-50 p-3 dark:bg-amber-900/20">
            <div className="flex items-start gap-2">
              <AlertCircle className="mt-0.5 h-4 w-4 text-amber-600 dark:text-amber-400" />
              <p className="text-sm text-amber-800 dark:text-amber-200">
                {intake.notes}
              </p>
            </div>
          </div>
        )}

        {/* Documents Required */}
        {eligibility?.docs_required && eligibility.docs_required.length > 0 && (
          <>
            <Separator />
            <div>
              <p className="mb-2 text-sm font-medium">What to Bring</p>
              <ul className="space-y-2">
                {eligibility.docs_required.map((doc, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                    {doc}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}

        {/* Verification Badge */}
        {verification?.last_verified_at && (
          <>
            <Separator />
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Last verified</span>
              <Badge variant="outline" className="text-xs">
                {new Date(verification.last_verified_at).toLocaleDateString()}
                {verification.verified_by && ` · ${verification.verified_by.replace('_', ' ')}`}
              </Badge>
            </div>
          </>
        )}

        {/* Waitlist Status */}
        {eligibility?.waitlist_status && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Waitlist</span>
            <Badge
              variant={eligibility.waitlist_status === 'open' ? 'default' : 'secondary'}
              className={
                eligibility.waitlist_status === 'open'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                  : eligibility.waitlist_status === 'closed'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                  : ''
              }
            >
              {eligibility.waitlist_status.charAt(0).toUpperCase() +
                eligibility.waitlist_status.slice(1)}
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function ResourceDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const { trackResourceView } = useAnalytics();
  const id = params.id as string;

  // Build back link with preserved search params
  const fromParams = searchParams.get('from');
  const backLink = fromParams ? `/search?${fromParams}` : '/search';

  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResource() {
      try {
        const data = await api.resources.get(id);
        setResource(data);
        // Track resource view analytics
        trackResourceView(data.id, data.categories[0], data.states[0]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resource');
      } finally {
        setLoading(false);
      }
    }

    fetchResource();
  }, [id, trackResourceView]);

  if (loading) {
    return (
      <main className="min-h-screen p-8 pt-24">
        <div className="mx-auto max-w-4xl animate-pulse">
          {/* Back link skeleton */}
          <Skeleton className="mb-6 h-4 w-24" />

          {/* Header skeleton */}
          <div className="mb-6">
            <div className="mb-2 flex gap-2">
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>
            <Skeleton className="mb-2 h-9 w-3/4" />
            <Skeleton className="h-5 w-48" />
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Main content cards */}
            <div className="space-y-6 md:col-span-2">
              <Card className="overflow-hidden">
                <CardHeader>
                  <Skeleton className="h-6 w-40" />
                </CardHeader>
                <CardContent className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                </CardContent>
              </Card>
              <Card className="overflow-hidden">
                <CardHeader>
                  <Skeleton className="h-6 w-32" />
                </CardHeader>
                <CardContent className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </CardContent>
              </Card>
            </div>

            {/* Sidebar card */}
            <Card className="h-fit overflow-hidden">
              <CardHeader>
                <Skeleton className="h-6 w-28" />
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="mb-2 flex justify-between">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-10" />
                  </div>
                  <Skeleton className="h-3 w-full rounded-full" />
                </div>
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-24" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    );
  }

  if (error || !resource) {
    return (
      <main className="min-h-screen p-8 pt-24">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="mb-4 text-2xl font-bold">Resource Not Found</h1>
          <p className="mb-4 text-muted-foreground">{error}</p>
          <Button asChild>
            <Link href={backLink}>Back to Search</Link>
          </Button>
        </div>
      </main>
    );
  }

  const primaryCategory = resource.categories[0] || 'employment';
  const CategoryIcon = categoryIcons[primaryCategory] || Briefcase;
  const gradient = categoryGradients[primaryCategory] || categoryGradients.employment;

  return (
    <main className="min-h-screen">
      {/* Gradient Header */}
      <div className={cn('bg-gradient-to-br px-8 pb-8 pt-24 text-white', gradient)}>
        <div className="mx-auto max-w-4xl">
          {/* Navigation */}
          <div className="mb-6">
            <Link
              href={backLink}
              className="inline-flex items-center gap-1 text-sm text-white/80 transition-colors hover:text-white"
            >
              ← Back to Search
            </Link>
          </div>

          {/* Category icon and badges */}
          <div className="mb-4 flex items-center gap-3">
            <div className="rounded-xl bg-white/20 p-3">
              <CategoryIcon className="h-6 w-6" />
            </div>
            <div className="flex flex-wrap gap-2">
              {resource.categories.map((cat) => (
                <Badge
                  key={cat}
                  className={cn('border-0 font-medium capitalize', categoryColors[cat] || '')}
                >
                  {cat}
                </Badge>
              ))}
            </div>
          </div>

          {/* Title and Bookmark */}
          <div className="flex items-start justify-between gap-4">
            <h1 className="font-display mb-2 text-3xl font-bold leading-tight sm:text-4xl">
              {resource.title}
            </h1>
            <BookmarkButton
              resourceId={resource.id}
              size="lg"
              className="shrink-0 border-white/30 bg-white/20 text-white hover:bg-white/30 hover:text-white"
            />
          </div>

          {/* Organization */}
          <p className="text-lg text-white/90">{resource.organization.name}</p>

          {/* Primary CTAs */}
          <div className="mt-6 flex flex-wrap gap-3">
            {resource.website && (
              <Button
                asChild
                className="gap-2 bg-white text-gray-900 hover:bg-white/90"
              >
                <a href={resource.website} target="_blank" rel="noopener noreferrer">
                  <Globe className="h-4 w-4" />
                  Visit Website
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
            )}
            {resource.phone && (
              <Button
                variant="outline"
                asChild
                className="gap-2 border-white/30 bg-white/10 text-white hover:bg-white/20"
              >
                <a href={`tel:${resource.phone}`}>
                  <Phone className="h-4 w-4" />
                  {resource.phone}
                </a>
              </Button>
            )}
            {resource.location && (
              <Button
                variant="outline"
                asChild
                className="gap-2 border-white/30 bg-white/10 text-white hover:bg-white/20"
              >
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                    `${resource.location.address || ''} ${resource.location.city}, ${resource.location.state}`
                  )}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <MapPin className="h-4 w-4" />
                  Get Directions
                </a>
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-8 py-8">
        <div className="mx-auto max-w-4xl">
          <div className="grid gap-6 md:grid-cols-3">
            {/* Main Content */}
            <div className="space-y-6 md:col-span-2">
              {/* Description */}
              <Card>
                <CardHeader>
                  <CardTitle>About This Resource</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap">{resource.description}</p>
                </CardContent>
              </Card>

              {/* Eligibility */}
              {resource.eligibility && (
                <Card>
                  <CardHeader>
                    <CardTitle>Eligibility</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{resource.eligibility}</p>
                  </CardContent>
                </Card>
              )}

              {/* How to Apply */}
              {resource.how_to_apply && (
                <Card>
                  <CardHeader>
                    <CardTitle>How to Apply</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap">{resource.how_to_apply}</p>
                  </CardContent>
                </Card>
              )}
            </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Intake Card - How to Apply */}
            <IntakeCard resource={resource} />

            {/* Contact Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {resource.website && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Website
                    </p>
                    <a
                      href={resource.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      Visit Website
                    </a>
                  </div>
                )}

                {resource.phone && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Phone
                    </p>
                    <a
                      href={`tel:${resource.phone}`}
                      className="text-primary hover:underline"
                    >
                      {resource.phone}
                    </a>
                  </div>
                )}

                {resource.hours && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Hours
                    </p>
                    <p>{resource.hours}</p>
                  </div>
                )}

                {resource.location && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Location
                    </p>
                    <p>
                      {resource.location.address && (
                        <>{resource.location.address}<br /></>
                      )}
                      {resource.location.city}, {resource.location.state}
                    </p>
                  </div>
                )}

                {resource.cost && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Cost
                    </p>
                    <p className="font-medium text-green-600 dark:text-green-400">
                      {resource.cost}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Coverage */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Coverage</CardTitle>
              </CardHeader>
              <CardContent>
                {resource.scope === 'national' ? (
                  <Badge variant="outline">Nationwide</Badge>
                ) : (
                  <div className="flex flex-wrap gap-1">
                    {resource.states.map((state) => (
                      <Badge key={state} variant="outline">
                        {state}
                      </Badge>
                    ))}
                  </div>
                )}

                {resource.languages.length > 0 && (
                  <div className="mt-4">
                    <p className="mb-2 text-sm font-medium text-muted-foreground">
                      Languages
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {resource.languages.map((lang) => (
                        <Badge key={lang} variant="secondary">
                          {lang.toUpperCase()}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Report Issue */}
            <div className="flex justify-center pt-2">
              <ReportFeedbackModal
                resourceId={resource.id}
                resourceTitle={resource.title}
              />
            </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
