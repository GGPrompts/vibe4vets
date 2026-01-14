'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Shield, Briefcase, BookOpen, Home, Scale, MapPin, Globe, CheckCircle2 } from 'lucide-react';
import type { Resource, MatchExplanation } from '@/lib/api';

interface ResourceCardProps {
  resource: Resource;
  explanations?: MatchExplanation[];
  variant?: 'link' | 'selectable';
  selected?: boolean;
  onClick?: () => void;
  /** Search params to preserve for "back to search" navigation */
  searchParams?: string;
}

// Design system colors for accent bars
const accentBarColors: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal))]',
};

// Badge styling using design system
const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.1)] text-[hsl(var(--v4v-employment))] border-[hsl(var(--v4v-employment)/0.3)]',
  training: 'bg-[hsl(var(--v4v-training)/0.1)] text-[hsl(var(--v4v-training))] border-[hsl(var(--v4v-training)/0.3)]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.1)] text-[hsl(var(--v4v-housing))] border-[hsl(var(--v4v-housing)/0.3)]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.1)] text-[hsl(var(--v4v-legal))] border-[hsl(var(--v4v-legal)/0.3)]',
};

// Category icons
const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: BookOpen,
  housing: Home,
  legal: Scale,
};

// Export for use in other components
export const categoryColors = categoryBadgeStyles;

function TrustIndicator({ score }: { score: number }) {
  const percentage = Math.round(score * 100);
  let color = 'bg-red-500';
  let label = 'Low';
  if (percentage >= 80) {
    color = 'bg-green-500';
    label = 'High';
  } else if (percentage >= 60) {
    color = 'bg-yellow-500';
    label = 'Good';
  } else if (percentage >= 40) {
    color = 'bg-orange-500';
    label = 'Fair';
  }

  return (
    <div className="flex items-center gap-2">
      <Shield className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
      <div className="h-2.5 w-20 rounded-full bg-muted overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs font-medium text-muted-foreground">
        {label}
      </span>
    </div>
  );
}

function CardInner({
  resource,
  explanations,
}: {
  resource: Resource;
  explanations?: MatchExplanation[];
}) {
  const trustScore = resource.trust.freshness_score * resource.trust.reliability_score;
  const primaryCategory = resource.categories[0] || 'employment';
  const CategoryIcon = categoryIcons[primaryCategory] || Briefcase;

  return (
    <>
      {/* Category accent bar */}
      <div className={`absolute left-0 top-0 h-1 w-full ${accentBarColors[primaryCategory] || accentBarColors.employment}`} />

      <CardHeader className="pb-3 pt-5">
        {/* Trust indicator row */}
        <div className="mb-2 flex items-center justify-end">
          <TrustIndicator score={trustScore} />
        </div>

        {/* Title with icon */}
        <div className="flex items-start gap-3">
          <div className={`shrink-0 rounded-lg p-2 ${accentBarColors[primaryCategory] || accentBarColors.employment} text-white transition-transform duration-300 group-hover:scale-110`}>
            <CategoryIcon className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <CardTitle className="font-display line-clamp-2 text-lg text-[hsl(var(--v4v-navy))] transition-colors duration-300 group-hover:text-[hsl(var(--v4v-gold))] dark:text-foreground dark:group-hover:text-[hsl(var(--v4v-gold))]">
              {resource.title}
            </CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              {resource.organization.name}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <p className="mb-4 line-clamp-2 text-sm leading-relaxed text-muted-foreground">
          {resource.summary || resource.description}
        </p>

        {/* Badges */}
        <div className="mb-3 flex flex-wrap gap-2">
          {resource.categories.map((cat) => {
            const Icon = categoryIcons[cat] || Briefcase;
            return (
              <Badge
                key={cat}
                variant="outline"
                className={`${categoryBadgeStyles[cat] || ''} gap-1 border font-medium`}
              >
                <Icon className="h-3 w-3" />
                <span className="capitalize">{cat}</span>
              </Badge>
            );
          })}
          {resource.location && (
            <Badge
              variant="outline"
              className="gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.08)] text-[hsl(var(--v4v-gold))] font-medium"
            >
              <MapPin className="h-3 w-3" />
              {resource.location.city}, {resource.location.state}
            </Badge>
          )}
          {resource.scope === 'national' && (
            <Badge
              variant="outline"
              className="gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.08)] text-[hsl(var(--v4v-gold))] font-medium"
            >
              <Globe className="h-3 w-3" />
              Nationwide
            </Badge>
          )}
        </div>

        {/* Match explanation */}
        {explanations && explanations.length > 0 && (
          <div className="mt-3 rounded-lg border border-[hsl(var(--v4v-gold)/0.2)] bg-[hsl(var(--v4v-gold)/0.05)] p-3">
            <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-[hsl(var(--v4v-gold))]">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Why this matched
            </p>
            <ul className="space-y-1">
              {explanations.slice(0, 3).map((exp, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[hsl(var(--v4v-gold))]" />
                  {exp.reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Cost indicator */}
        {resource.cost && (
          <p className="mt-3 text-sm font-semibold text-green-600 dark:text-green-400">
            {resource.cost}
          </p>
        )}
      </CardContent>
    </>
  );
}

export function ResourceCard({
  resource,
  explanations,
  variant = 'link',
  selected = false,
  onClick,
  searchParams,
}: ResourceCardProps) {
  if (variant === 'selectable') {
    return (
      <Card
        className={`category-card group relative h-full cursor-pointer overflow-hidden bg-white dark:bg-card ${
          selected ? 'ring-2 ring-[hsl(var(--v4v-gold))]' : ''
        }`}
        onClick={onClick}
      >
        <CardInner resource={resource} explanations={explanations} />
      </Card>
    );
  }

  // Build href with optional search params for back navigation
  const href = searchParams
    ? `/resources/${resource.id}?from=${encodeURIComponent(searchParams)}`
    : `/resources/${resource.id}`;

  return (
    <Link href={href} className="block h-full">
      <Card className="category-card group relative h-full overflow-hidden bg-white dark:bg-card">
        <CardInner resource={resource} explanations={explanations} />
      </Card>
    </Link>
  );
}
