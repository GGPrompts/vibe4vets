'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Briefcase, BookOpen, Home, Scale, MapPin, Globe, CheckCircle2, Tag, Phone, Clock, UtensilsCrossed, Award } from 'lucide-react';
import type { Resource, MatchExplanation } from '@/lib/api';
import { BookmarkButton } from '@/components/bookmark-button';

interface ResourceCardProps {
  resource: Resource;
  explanations?: MatchExplanation[];
  variant?: 'link' | 'selectable' | 'modal';
  selected?: boolean;
  onClick?: () => void;
  /** Search params to preserve for "back to search" navigation */
  searchParams?: string;
  /** Enable layoutId for shared element transitions */
  enableLayoutId?: boolean;
  /** Distance in miles from search location (for nearby search) */
  distance?: number;
}

// Design system colors for accent bars
const accentBarColors: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal))]',
  food: 'bg-[hsl(var(--v4v-food))]',
  benefits: 'bg-[hsl(var(--v4v-benefits))]',
};

// Card background gradients - subtle category tints
const cardBackgrounds: Record<string, string> = {
  employment: 'bg-gradient-to-br from-[hsl(var(--v4v-employment)/0.03)] via-white to-[hsl(var(--v4v-employment)/0.06)]',
  training: 'bg-gradient-to-br from-[hsl(var(--v4v-training)/0.03)] via-white to-[hsl(var(--v4v-training)/0.06)]',
  housing: 'bg-gradient-to-br from-[hsl(var(--v4v-housing)/0.03)] via-white to-[hsl(var(--v4v-housing)/0.06)]',
  legal: 'bg-gradient-to-br from-[hsl(var(--v4v-legal)/0.03)] via-white to-[hsl(var(--v4v-legal)/0.06)]',
  food: 'bg-gradient-to-br from-[hsl(var(--v4v-food)/0.03)] via-white to-[hsl(var(--v4v-food)/0.06)]',
  benefits: 'bg-gradient-to-br from-[hsl(var(--v4v-benefits)/0.03)] via-white to-[hsl(var(--v4v-benefits)/0.06)]',
};

// Card border colors on hover
const cardHoverBorders: Record<string, string> = {
  employment: 'hover:border-[hsl(var(--v4v-employment)/0.3)]',
  training: 'hover:border-[hsl(var(--v4v-training)/0.3)]',
  housing: 'hover:border-[hsl(var(--v4v-housing)/0.3)]',
  legal: 'hover:border-[hsl(var(--v4v-legal)/0.3)]',
  food: 'hover:border-[hsl(var(--v4v-food)/0.3)]',
  benefits: 'hover:border-[hsl(var(--v4v-benefits)/0.3)]',
};

// Badge styling using design system
const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.12)] text-[hsl(var(--v4v-employment))] border-[hsl(var(--v4v-employment)/0.25)]',
  training: 'bg-[hsl(var(--v4v-training)/0.12)] text-[hsl(var(--v4v-training))] border-[hsl(var(--v4v-training)/0.25)]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.12)] text-[hsl(var(--v4v-housing))] border-[hsl(var(--v4v-housing)/0.25)]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.12)] text-[hsl(var(--v4v-legal))] border-[hsl(var(--v4v-legal)/0.25)]',
  food: 'bg-[hsl(var(--v4v-food)/0.12)] text-[hsl(var(--v4v-food))] border-[hsl(var(--v4v-food)/0.25)]',
  benefits: 'bg-[hsl(var(--v4v-benefits)/0.12)] text-[hsl(var(--v4v-benefits))] border-[hsl(var(--v4v-benefits)/0.25)]',
};

// Category icons
const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: BookOpen,
  housing: Home,
  legal: Scale,
  food: UtensilsCrossed,
  benefits: Award,
};

// Export for use in other components
export const categoryColors = categoryBadgeStyles;

function CardInner({
  resource,
  explanations,
  showBookmark = false,
  renderBookmark = false,
  /** When true, phone numbers render as plain text (to avoid nested <a> in <Link>) */
  disablePhoneLinks = false,
  /** Distance in miles from search location */
  distance,
}: {
  resource: Resource;
  explanations?: MatchExplanation[];
  showBookmark?: boolean;
  /** Actually render the bookmark button inside the card (for modal/selectable variants) */
  renderBookmark?: boolean;
  /** When true, phone numbers render as plain text (to avoid nested <a> in <Link>) */
  disablePhoneLinks?: boolean;
  /** Distance in miles from search location */
  distance?: number;
}) {
  const primaryCategory = resource.categories[0] || 'employment';
  const CategoryIcon = categoryIcons[primaryCategory] || Briefcase;

  return (
    <>
      {/* Category accent bar - thicker */}
      <div className={`absolute left-0 top-0 h-1.5 w-full ${accentBarColors[primaryCategory] || accentBarColors.employment}`} />

      {/* Decorative corner gradient */}
      <div
        className={`absolute -right-8 -top-8 h-24 w-24 rounded-full opacity-[0.07] blur-2xl ${accentBarColors[primaryCategory] || accentBarColors.employment}`}
      />

      {/* Bookmark button - rendered inside card so it animates with the card */}
      {renderBookmark && (
        <div className="absolute right-3 top-[1.125rem] z-10">
          <BookmarkButton resourceId={resource.id} size="sm" showTooltip={false} />
        </div>
      )}

      <CardHeader className="pb-3 pt-4">
        {/* Title with icon and bookmark */}
        <div className="flex items-start gap-3">
          <div className={`shrink-0 rounded-lg p-2 ${accentBarColors[primaryCategory] || accentBarColors.employment} text-white transition-transform duration-300 group-hover:scale-110`}>
            <CategoryIcon className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="font-display line-clamp-2 text-lg text-[hsl(var(--v4v-navy))] dark:text-foreground">
                {resource.title}
              </CardTitle>
              {/* Placeholder for bookmark button spacing */}
              {(showBookmark || renderBookmark) && <div className="h-6 w-6 shrink-0" />}
            </div>
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

        {/* Category badges */}
        <div className="mb-2 flex flex-wrap gap-2">
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
          {/* State badges when no location entity */}
          {!resource.location && resource.states && resource.states.length > 0 && (
            resource.states.slice(0, 3).map((state) => (
              <Badge
                key={state}
                variant="outline"
                className="gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.08)] text-[hsl(var(--v4v-gold))] font-medium"
              >
                <MapPin className="h-3 w-3" />
                {state}
              </Badge>
            ))
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
          {distance !== undefined && (
            <Badge
              variant="outline"
              className="gap-1 border-emerald-500/40 bg-emerald-50 text-emerald-700 font-semibold dark:bg-emerald-950 dark:text-emerald-300"
            >
              <MapPin className="h-3 w-3" />
              {distance < 1 ? '<1' : distance.toFixed(1)} mi
            </Badge>
          )}
        </div>

        {/* Tags badges */}
        {resource.tags && resource.tags.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-1.5">
            {resource.tags.slice(0, 4).map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="gap-1 border-muted-foreground/20 bg-muted/50 text-muted-foreground text-xs py-0 h-5 font-normal"
              >
                <Tag className="h-2.5 w-2.5" />
                <span className="capitalize">{tag.replace(/_/g, ' ')}</span>
              </Badge>
            ))}
            {resource.tags.length > 4 && (
              <Badge
                variant="outline"
                className="border-muted-foreground/20 bg-muted/50 text-muted-foreground text-xs py-0 h-5 font-normal"
              >
                +{resource.tags.length - 4}
              </Badge>
            )}
          </div>
        )}

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

        {/* Eligibility summary */}
        {resource.eligibility && (
          <p className="mt-3 text-sm text-green-600 dark:text-green-400 line-clamp-2">
            {resource.eligibility.split(/[.!?]/)[0].trim()}.
          </p>
        )}

        {/* Local provider contact info */}
        {resource.location && (resource.location.intake?.phone || resource.location.intake?.hours) && (
          <div className="mt-3 rounded-lg border border-muted bg-muted/30 p-3">
            <p className="mb-2 text-xs font-semibold text-muted-foreground">Local Provider</p>
            <div className="space-y-1">
              {resource.location.intake?.phone && (
                disablePhoneLinks ? (
                  <span className="flex items-center gap-2 text-sm text-primary">
                    <Phone className="h-3.5 w-3.5" />
                    {resource.location.intake.phone}
                  </span>
                ) : (
                  <a
                    href={`tel:${resource.location.intake.phone}`}
                    className="flex items-center gap-2 text-sm text-primary hover:underline"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Phone className="h-3.5 w-3.5" />
                    {resource.location.intake.phone}
                  </a>
                )
              )}
              {resource.location.intake?.hours && (
                <p className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {resource.location.intake.hours}
                </p>
              )}
            </div>
          </div>
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
  enableLayoutId = false,
  distance,
}: ResourceCardProps) {
  const primaryCategory = resource.categories[0] || 'employment';

  // For modal/selectable variants, render bookmark inside card so it animates with the card
  const renderBookmarkInside = variant === 'modal' || variant === 'selectable';
  // For link variant, disable phone links to avoid nested <a> tags
  const isLinkVariant = variant === 'link';

  const cardContent = (
    <Card
      className={`category-card group relative h-full overflow-hidden border transition-all duration-300 ${
        cardBackgrounds[primaryCategory] || cardBackgrounds.employment
      } ${cardHoverBorders[primaryCategory] || cardHoverBorders.employment} ${
        variant === 'selectable' && selected ? 'ring-2 ring-[hsl(var(--v4v-gold))]' : ''
      } ${variant === 'modal' || variant === 'selectable' ? 'cursor-pointer' : ''}`}
      onClick={variant === 'modal' || variant === 'selectable' ? onClick : undefined}
    >
      <CardInner
        resource={resource}
        explanations={explanations}
        showBookmark={isLinkVariant}
        renderBookmark={renderBookmarkInside}
        disablePhoneLinks={isLinkVariant}
        distance={distance}
      />
    </Card>
  );

  // Wrapper with bookmark button for link variant only
  // (modal/selectable have bookmark rendered inside the card)
  const withBookmark = (content: React.ReactNode) => (
    <div className="relative h-full">
      {content}
      <div className="absolute right-3 top-[1.125rem] z-10">
        <BookmarkButton resourceId={resource.id} size="sm" showTooltip={false} />
      </div>
    </div>
  );

  // Modal variant: clickable card with layoutId for shared element transition
  if (variant === 'modal') {
    if (enableLayoutId) {
      return (
        <motion.div layoutId={`resource-card-${resource.id}`} className="h-full">
          {cardContent}
        </motion.div>
      );
    }
    return cardContent;
  }

  // Selectable variant: clickable card without link
  if (variant === 'selectable') {
    return cardContent;
  }

  // Link variant (default): navigates to detail page
  // Bookmark is outside the Link so it's clickable independently
  const href = searchParams
    ? `/resources/${resource.id}?from=${encodeURIComponent(searchParams)}`
    : `/resources/${resource.id}`;

  return withBookmark(
    <Link href={href} className="block h-full">
      {cardContent}
    </Link>
  );
}
