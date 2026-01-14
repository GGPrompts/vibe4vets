'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import api, { type Resource } from '@/lib/api';
import {
  ExternalLink,
  Phone,
  MapPin,
  Clock,
  Globe,
  Shield,
  CheckCircle,
  ChevronRight,
  Home,
  DollarSign,
  Building2,
  Calendar,
} from 'lucide-react';

const categoryColors: Record<string, string> = {
  employment: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  training: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  housing: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  legal: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300',
};

const categoryLabels: Record<string, string> = {
  employment: 'Employment',
  training: 'Training',
  housing: 'Housing',
  legal: 'Legal',
};

interface TrustIndicatorProps {
  score: number;
  showLabel?: boolean;
}

function TrustIndicator({ score, showLabel = true }: TrustIndicatorProps) {
  const percentage = Math.round(score * 100);
  let color = 'bg-red-500';
  let textColor = 'text-red-600 dark:text-red-400';
  let label = 'Low Trust';

  if (percentage >= 80) {
    color = 'bg-green-500';
    textColor = 'text-green-600 dark:text-green-400';
    label = 'Highly Trusted';
  } else if (percentage >= 60) {
    color = 'bg-yellow-500';
    textColor = 'text-yellow-600 dark:text-yellow-400';
    label = 'Moderately Trusted';
  } else if (percentage >= 40) {
    color = 'bg-orange-500';
    textColor = 'text-orange-600 dark:text-orange-400';
    label = 'Some Trust';
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Trust Score</span>
        <span className={`text-lg font-bold ${textColor}`}>{percentage}%</span>
      </div>
      <div className="h-3 w-full rounded-full bg-muted">
        <div
          className={`h-3 rounded-full transition-all ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="flex items-center gap-2">
          <CheckCircle className={`h-4 w-4 ${textColor}`} />
          <span className={`text-sm font-medium ${textColor}`}>{label}</span>
        </div>
      )}
    </div>
  );
}

function TrustSignalCard({ resource }: { resource: Resource }) {
  const trustScore = resource.trust.freshness_score * resource.trust.reliability_score;

  const tierLabels: Record<number, string> = {
    1: 'Official Government Source',
    2: 'Established VSO',
    3: 'State Agency',
    4: 'Community Directory',
  };

  const tierBadgeColors: Record<number, string> = {
    1: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300',
    2: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    3: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    4: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
  };

  // Calculate days since last verified
  const getVerifiedText = () => {
    if (!resource.trust.last_verified) return null;
    const verifiedDate = new Date(resource.trust.last_verified);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - verifiedDate.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Verified today';
    if (diffDays === 1) return 'Verified yesterday';
    if (diffDays < 7) return `Verified ${diffDays} days ago`;
    if (diffDays < 30) return `Verified ${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
    return `Verified ${verifiedDate.toLocaleDateString()}`;
  };

  return (
    <Card className="border-2">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Shield className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
          Trust Signals
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <TrustIndicator score={trustScore} />

        <Separator />

        {/* Last Verified - Prominent display */}
        {resource.trust.last_verified && (
          <div className="rounded-lg bg-muted/50 p-3">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">{getVerifiedText()}</span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {new Date(resource.trust.last_verified).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        )}

        {/* Source Info */}
        <div className="space-y-3">
          {resource.trust.source_tier && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Source Type</span>
              <Badge className={tierBadgeColors[resource.trust.source_tier] || ''}>
                Tier {resource.trust.source_tier}
              </Badge>
            </div>
          )}

          {resource.trust.source_tier && (
            <p className="text-xs text-muted-foreground">
              {tierLabels[resource.trust.source_tier] || 'Unknown source type'}
            </p>
          )}

          {resource.trust.source_name && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Source</span>
              <span className="text-sm font-medium">{resource.trust.source_name}</span>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Freshness Score</span>
            <span className="text-sm font-medium">
              {Math.round(resource.trust.freshness_score * 100)}%
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Reliability Score</span>
            <span className="text-sm font-medium">
              {Math.round(resource.trust.reliability_score * 100)}%
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ResourceDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResource() {
      try {
        const data = await api.resources.get(id);
        setResource(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resource');
      } finally {
        setLoading(false);
      }
    }

    fetchResource();
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen bg-muted/30">
        <div className="mx-auto max-w-5xl p-6 md:p-8">
          {/* Breadcrumb skeleton */}
          <Skeleton className="mb-6 h-5 w-48" />
          {/* Header skeleton */}
          <div className="mb-8 rounded-xl bg-card p-6 shadow-sm">
            <Skeleton className="mb-3 h-6 w-32" />
            <Skeleton className="mb-2 h-10 w-3/4" />
            <Skeleton className="h-5 w-1/2" />
          </div>
          {/* Content skeleton */}
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="space-y-6 lg:col-span-2">
              <Skeleton className="h-48 w-full rounded-xl" />
              <Skeleton className="h-32 w-full rounded-xl" />
            </div>
            <div className="space-y-6">
              <Skeleton className="h-64 w-full rounded-xl" />
              <Skeleton className="h-48 w-full rounded-xl" />
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error || !resource) {
    return (
      <main className="min-h-screen bg-muted/30">
        <div className="mx-auto max-w-5xl p-6 md:p-8">
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 rounded-full bg-muted p-4">
              <Building2 className="h-8 w-8 text-muted-foreground" />
            </div>
            <h1 className="mb-2 text-2xl font-bold">Resource Not Found</h1>
            <p className="mb-6 max-w-md text-muted-foreground">{error || 'The resource you\'re looking for doesn\'t exist or has been removed.'}</p>
            <Button asChild>
              <Link href="/search">
                <ChevronRight className="mr-2 h-4 w-4 rotate-180" />
                Back to Search
              </Link>
            </Button>
          </div>
        </div>
      </main>
    );
  }

  const primaryCategory = resource.categories[0];

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-5xl p-6 md:p-8">
        {/* Breadcrumb Navigation */}
        <nav className="mb-6 flex items-center gap-2 text-sm">
          <Link
            href="/"
            className="flex items-center gap-1 text-muted-foreground transition-colors hover:text-foreground"
          >
            <Home className="h-4 w-4" />
            <span>Home</span>
          </Link>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <Link
            href="/search"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            Search
          </Link>
          {primaryCategory && (
            <>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
              <Link
                href={`/search?category=${primaryCategory}`}
                className="text-muted-foreground transition-colors hover:text-foreground"
              >
                {categoryLabels[primaryCategory] || primaryCategory}
              </Link>
            </>
          )}
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium text-foreground">{resource.title}</span>
        </nav>

        {/* Header Card */}
        <div className="mb-8 rounded-xl bg-card p-6 shadow-sm">
          {/* Category Badges */}
          <div className="mb-3 flex flex-wrap gap-2">
            {resource.categories.map((cat) => (
              <Badge
                key={cat}
                className={`${categoryColors[cat] || ''} text-sm font-medium`}
              >
                {categoryLabels[cat] || cat}
              </Badge>
            ))}
            {resource.scope === 'national' && (
              <Badge variant="outline" className="gap-1">
                <Globe className="h-3 w-3" />
                Nationwide
              </Badge>
            )}
          </div>

          {/* Title */}
          <h1 className="mb-2 text-2xl font-bold leading-tight md:text-3xl">
            {resource.title}
          </h1>

          {/* Organization */}
          <div className="flex items-center gap-2 text-muted-foreground">
            <Building2 className="h-4 w-4" />
            <span className="text-lg">{resource.organization.name}</span>
          </div>

          {/* Quick Info Row */}
          <div className="mt-4 flex flex-wrap items-center gap-4 text-sm">
            {resource.location && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{resource.location.city}, {resource.location.state}</span>
              </div>
            )}
            {resource.cost && (
              <div className="flex items-center gap-1.5 font-medium text-green-600 dark:text-green-400">
                <DollarSign className="h-4 w-4" />
                <span>{resource.cost}</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Content */}
          <div className="space-y-6 lg:col-span-2">
            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle>About This Resource</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap leading-relaxed text-muted-foreground">
                  {resource.description}
                </p>
              </CardContent>
            </Card>

            {/* Eligibility */}
            {resource.eligibility && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    Eligibility Requirements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap leading-relaxed text-muted-foreground">
                    {resource.eligibility}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* How to Apply */}
            {resource.how_to_apply && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ChevronRight className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
                    How to Apply
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap leading-relaxed text-muted-foreground">
                    {resource.how_to_apply}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Related Resources Placeholder */}
            <Card className="border-dashed">
              <CardHeader>
                <CardTitle className="text-muted-foreground">Related Resources</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Related resources based on category and location will appear here in a future update.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Contact Info Card */}
            <Card className="border-2">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Phone className="h-5 w-5 text-primary" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Website Button */}
                {resource.website && (
                  <Button className="w-full" asChild>
                    <a href={resource.website} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Visit Website
                    </a>
                  </Button>
                )}

                {/* Phone Button */}
                {resource.phone && (
                  <Button variant="outline" className="w-full" asChild>
                    <a href={`tel:${resource.phone}`}>
                      <Phone className="mr-2 h-4 w-4" />
                      {resource.phone}
                    </a>
                  </Button>
                )}

                <Separator />

                {/* Hours */}
                {resource.hours && (
                  <div className="flex items-start gap-3">
                    <Clock className="mt-0.5 h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Hours</p>
                      <p className="text-sm text-muted-foreground">{resource.hours}</p>
                    </div>
                  </div>
                )}

                {/* Location */}
                {resource.location && (
                  <div className="flex items-start gap-3">
                    <MapPin className="mt-0.5 h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Location</p>
                      <p className="text-sm text-muted-foreground">
                        {resource.location.address && (
                          <>{resource.location.address}<br /></>
                        )}
                        {resource.location.city}, {resource.location.state}
                      </p>
                    </div>
                  </div>
                )}

                {/* Cost */}
                {resource.cost && (
                  <div className="flex items-start gap-3">
                    <DollarSign className="mt-0.5 h-4 w-4 text-green-600" />
                    <div>
                      <p className="text-sm font-medium">Cost</p>
                      <p className="text-sm font-medium text-green-600 dark:text-green-400">
                        {resource.cost}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Trust Signals */}
            <TrustSignalCard resource={resource} />

            {/* Coverage */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Globe className="h-5 w-5 text-muted-foreground" />
                  Coverage
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="mb-2 text-sm font-medium text-muted-foreground">Service Area</p>
                  {resource.scope === 'national' ? (
                    <Badge variant="outline" className="gap-1">
                      <Globe className="h-3 w-3" />
                      Nationwide
                    </Badge>
                  ) : (
                    <div className="flex flex-wrap gap-1">
                      {resource.states.map((state) => (
                        <Badge key={state} variant="outline">
                          {state}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {resource.languages.length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-medium text-muted-foreground">
                      Languages Available
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
          </div>
        </div>
      </div>
    </main>
  );
}
