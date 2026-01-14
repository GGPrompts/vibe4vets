'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Resource, MatchExplanation } from '@/lib/api';

interface ResourceCardProps {
  resource: Resource;
  explanations?: MatchExplanation[];
  variant?: 'link' | 'selectable';
  selected?: boolean;
  onClick?: () => void;
}

export const categoryColors: Record<string, string> = {
  employment: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  training: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  housing: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  legal: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300',
};

function TrustIndicator({ score }: { score: number }) {
  const percentage = Math.round(score * 100);
  let color = 'bg-red-500';
  if (percentage >= 80) color = 'bg-green-500';
  else if (percentage >= 60) color = 'bg-yellow-500';
  else if (percentage >= 40) color = 'bg-orange-500';

  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-16 rounded-full bg-muted">
        <div
          className={`h-2 rounded-full ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-muted-foreground">
        {percentage}% trusted
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

  return (
    <>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="line-clamp-2 text-lg">{resource.title}</CardTitle>
          <TrustIndicator score={trustScore} />
        </div>
        <p className="text-sm text-muted-foreground">{resource.organization.name}</p>
      </CardHeader>
      <CardContent>
        <p className="mb-3 line-clamp-2 text-sm text-muted-foreground">
          {resource.summary || resource.description}
        </p>

        <div className="mb-3 flex flex-wrap gap-1">
          {resource.categories.map((cat) => (
            <Badge key={cat} variant="secondary" className={categoryColors[cat] || ''}>
              {cat}
            </Badge>
          ))}
          {resource.location && (
            <Badge variant="outline">
              {resource.location.city}, {resource.location.state}
            </Badge>
          )}
          {resource.scope === 'national' && (
            <Badge variant="outline">Nationwide</Badge>
          )}
        </div>

        {explanations && explanations.length > 0 && (
          <div className="mt-2 space-y-1 rounded-md bg-muted/50 p-2">
            <p className="text-xs font-medium text-muted-foreground">Why this matched:</p>
            {explanations.slice(0, 3).map((exp, i) => (
              <p key={i} className="text-xs text-muted-foreground">
                {exp.reason}
              </p>
            ))}
          </div>
        )}

        {resource.cost && (
          <p className="mt-2 text-sm font-medium text-green-600 dark:text-green-400">
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
}: ResourceCardProps) {
  if (variant === 'selectable') {
    return (
      <Card
        className={`h-full cursor-pointer transition-all hover:shadow-lg ${
          selected ? 'ring-2 ring-[hsl(var(--v4v-gold))]' : ''
        }`}
        onClick={onClick}
      >
        <CardInner resource={resource} explanations={explanations} />
      </Card>
    );
  }

  return (
    <Link href={`/resources/${resource.id}`}>
      <Card className="h-full transition-shadow hover:shadow-lg">
        <CardInner resource={resource} explanations={explanations} />
      </Card>
    </Link>
  );
}
