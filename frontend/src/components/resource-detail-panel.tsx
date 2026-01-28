'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { Resource, MatchExplanation } from '@/lib/api';
import {
  ExternalLink,
  Phone,
  MapPin,
  Clock,
  Globe,
  Shield,
  CheckCircle,
  AlertCircle,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

const categoryColors: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.12)] text-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training)/0.12)] text-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.12)] text-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.12)] text-[hsl(var(--v4v-legal))]',
  food: 'bg-[hsl(var(--v4v-food)/0.12)] text-[hsl(var(--v4v-food))]',
  benefits: 'bg-[hsl(var(--v4v-benefits)/0.12)] text-[hsl(var(--v4v-benefits))]',
  mentalHealth: 'bg-[hsl(var(--v4v-mentalHealth)/0.12)] text-[hsl(var(--v4v-mentalHealth))]',
  supportServices: 'bg-[hsl(var(--v4v-supportServices)/0.12)] text-[hsl(var(--v4v-supportServices))]',
  healthcare: 'bg-[hsl(var(--v4v-healthcare)/0.12)] text-[hsl(var(--v4v-healthcare))]',
  education: 'bg-[hsl(var(--v4v-education)/0.12)] text-[hsl(var(--v4v-education))]',
  financial: 'bg-[hsl(var(--v4v-financial)/0.12)] text-[hsl(var(--v4v-financial))]',
};

interface TrustIndicatorProps {
  score: number;
  size?: 'sm' | 'md';
}

function TrustIndicator({ score, size = 'md' }: TrustIndicatorProps) {
  const percentage = Math.round(score * 100);
  let color = 'bg-red-500';
  let textColor = 'text-red-600';
  let label = 'Low Trust';

  if (percentage >= 80) {
    color = 'bg-green-500';
    textColor = 'text-green-600';
    label = 'Highly Trusted';
  } else if (percentage >= 60) {
    color = 'bg-yellow-500';
    textColor = 'text-yellow-600';
    label = 'Moderately Trusted';
  } else if (percentage >= 40) {
    color = 'bg-orange-500';
    textColor = 'text-orange-600';
    label = 'Some Trust';
  }

  const barHeight = size === 'sm' ? 'h-1.5' : 'h-2';
  const barWidth = size === 'sm' ? 'w-16' : 'w-24';

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <div className={`${barHeight} ${barWidth} rounded-full bg-muted`}>
          <div
            className={`${barHeight} rounded-full ${color}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className={`text-sm font-medium ${textColor}`}>{percentage}%</span>
      </div>
      {size === 'md' && (
        <span className="text-xs text-muted-foreground">{label}</span>
      )}
    </div>
  );
}

interface ResourceDetailPanelProps {
  resource: Resource | null;
  explanations?: MatchExplanation[];
  onClose?: () => void;
}

export function ResourceDetailPanel({
  resource,
  explanations,
  onClose: _onClose,
}: ResourceDetailPanelProps) {
  if (!resource) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center">
        <div className="mb-4 rounded-full bg-muted p-4">
          <Sparkles className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="mb-2 text-lg font-semibold">Select a Resource</h3>
        <p className="text-sm text-muted-foreground">
          Click on a resource card to see its full details here.
        </p>
      </div>
    );
  }

  const trustScore = resource.trust.freshness_score * resource.trust.reliability_score;

  return (
    <ScrollArea className="h-full">
      <div className="space-y-6 p-6">
        {/* Header */}
        <div>
          <h2 className="mb-2 text-xl font-bold leading-tight">{resource.title}</h2>
          <p className="text-sm text-muted-foreground">{resource.organization.name}</p>
        </div>

        {/* Categories & Location */}
        <div className="flex flex-wrap gap-2">
          {resource.categories.map((cat) => (
            <Badge key={cat} className={categoryColors[cat] || ''}>
              {cat}
            </Badge>
          ))}
          {resource.location && (
            <Badge variant="outline">
              <MapPin className="mr-1 h-3 w-3" />
              {resource.location.city}, {resource.location.state}
            </Badge>
          )}
          {resource.scope === 'national' && (
            <Badge variant="outline">
              <Globe className="mr-1 h-3 w-3" />
              Nationwide
            </Badge>
          )}
        </div>

        <Separator />

        {/* Trust Signals */}
        <div className="rounded-lg border bg-muted/30 p-4">
          <div className="mb-3 flex items-center gap-2">
            <Shield className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
            <h4 className="font-medium">Trust Signals</h4>
          </div>
          <div className="space-y-3">
            <TrustIndicator score={trustScore} />
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-muted-foreground">Source Tier: </span>
                <span className="font-medium">
                  {resource.trust.source_tier ? `Tier ${resource.trust.source_tier}` : 'Unknown'}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Source: </span>
                <span className="font-medium">{resource.trust.source_name || 'Manual'}</span>
              </div>
              {resource.trust.last_verified && (
                <div className="col-span-2">
                  <span className="text-muted-foreground">Last Verified: </span>
                  <span className="font-medium">
                    {new Date(resource.trust.last_verified).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Why This Matched */}
        {explanations && explanations.length > 0 && (
          <div className="rounded-lg border border-[hsl(var(--v4v-gold))]/30 bg-[hsl(var(--v4v-gold))]/5 p-4">
            <div className="mb-2 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
              <h4 className="font-medium">Why This Matched</h4>
            </div>
            <ul className="space-y-1">
              {explanations.map((exp, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <ChevronRight className="mt-0.5 h-3 w-3 flex-shrink-0 text-muted-foreground" />
                  <span>{exp.reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <Separator />

        {/* Description */}
        <div>
          <h4 className="mb-2 font-medium">About</h4>
          <p className="text-sm leading-relaxed text-muted-foreground">
            {resource.summary || resource.description}
          </p>
        </div>

        {/* Eligibility */}
        {resource.eligibility && (
          <div>
            <h4 className="mb-2 font-medium">Eligibility</h4>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {resource.eligibility}
            </p>
          </div>
        )}

        {/* How to Apply */}
        {resource.how_to_apply && (
          <div>
            <h4 className="mb-2 font-medium">How to Apply</h4>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {resource.how_to_apply}
            </p>
          </div>
        )}

        {/* Additional Info */}
        <div className="space-y-2">
          {resource.hours && (
            <div className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span>{resource.hours}</span>
            </div>
          )}
          {resource.cost && (
            <div className="flex items-center gap-2 text-sm font-medium text-green-600 dark:text-green-400">
              <AlertCircle className="h-4 w-4" />
              <span>{resource.cost}</span>
            </div>
          )}
        </div>

        <Separator />

        {/* Action Buttons */}
        <div className="space-y-3">
          {resource.website && (
            <Button className="w-full" asChild>
              <a href={resource.website} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Visit Website
              </a>
            </Button>
          )}
          {resource.phone && (
            <Button variant="outline" className="w-full" asChild>
              <a href={`tel:${resource.phone}`}>
                <Phone className="mr-2 h-4 w-4" />
                {resource.phone}
              </a>
            </Button>
          )}
          <Button variant="ghost" className="w-full" asChild>
            <Link href={`/resources/${resource.id}`}>
              View Full Details
              <ChevronRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </ScrollArea>
  );
}
