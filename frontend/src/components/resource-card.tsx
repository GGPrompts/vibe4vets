'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Briefcase, BookOpen, Home, Scale, MapPin, Globe, Phone, Clock, UtensilsCrossed, Award, ExternalLink, Brain, HeartHandshake, HeartPulse, School, Wallet, Users } from 'lucide-react';
import type { Resource, MatchExplanation } from '@/lib/api';
import { BookmarkButton } from '@/components/bookmark-button';

interface ResourceCardProps {
  resource: Resource;
  explanations?: MatchExplanation[];
  variant?: 'link' | 'selectable' | 'modal';
  selected?: boolean;
  onClick?: () => void;
  /** Enable layoutId for shared element transitions */
  enableLayoutId?: boolean;
  /** Distance in miles from search location (for nearby search) */
  distance?: number;
  /** Hide Local Provider section to save space */
  compact?: boolean;
}

// Design system colors for accent bars
const accentBarColors: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal))]',
  food: 'bg-[hsl(var(--v4v-food))]',
  benefits: 'bg-[hsl(var(--v4v-benefits))]',
  mentalHealth: 'bg-[hsl(var(--v4v-mentalHealth))]',
  supportServices: 'bg-[hsl(var(--v4v-supportServices))]',
  healthcare: 'bg-[hsl(var(--v4v-healthcare))]',
  education: 'bg-[hsl(var(--v4v-education))]',
  financial: 'bg-[hsl(var(--v4v-financial))]',
};

// Card background gradients - subtle category tints
const cardBackgrounds: Record<string, string> = {
  employment: 'bg-gradient-to-br from-[hsl(var(--v4v-employment)/0.03)] via-white to-[hsl(var(--v4v-employment)/0.06)]',
  training: 'bg-gradient-to-br from-[hsl(var(--v4v-training)/0.03)] via-white to-[hsl(var(--v4v-training)/0.06)]',
  housing: 'bg-gradient-to-br from-[hsl(var(--v4v-housing)/0.03)] via-white to-[hsl(var(--v4v-housing)/0.06)]',
  legal: 'bg-gradient-to-br from-[hsl(var(--v4v-legal)/0.03)] via-white to-[hsl(var(--v4v-legal)/0.06)]',
  food: 'bg-gradient-to-br from-[hsl(var(--v4v-food)/0.03)] via-white to-[hsl(var(--v4v-food)/0.06)]',
  benefits: 'bg-gradient-to-br from-[hsl(var(--v4v-benefits)/0.03)] via-white to-[hsl(var(--v4v-benefits)/0.06)]',
  mentalHealth: 'bg-gradient-to-br from-[hsl(var(--v4v-mentalHealth)/0.03)] via-white to-[hsl(var(--v4v-mentalHealth)/0.06)]',
  supportServices: 'bg-gradient-to-br from-[hsl(var(--v4v-supportServices)/0.03)] via-white to-[hsl(var(--v4v-supportServices)/0.06)]',
  healthcare: 'bg-gradient-to-br from-[hsl(var(--v4v-healthcare)/0.03)] via-white to-[hsl(var(--v4v-healthcare)/0.06)]',
  education: 'bg-gradient-to-br from-[hsl(var(--v4v-education)/0.03)] via-white to-[hsl(var(--v4v-education)/0.06)]',
  financial: 'bg-gradient-to-br from-[hsl(var(--v4v-financial)/0.03)] via-white to-[hsl(var(--v4v-financial)/0.06)]',
};

// Card border colors on hover
const cardHoverBorders: Record<string, string> = {
  employment: 'hover:border-[hsl(var(--v4v-employment)/0.3)]',
  training: 'hover:border-[hsl(var(--v4v-training)/0.3)]',
  housing: 'hover:border-[hsl(var(--v4v-housing)/0.3)]',
  legal: 'hover:border-[hsl(var(--v4v-legal)/0.3)]',
  food: 'hover:border-[hsl(var(--v4v-food)/0.3)]',
  benefits: 'hover:border-[hsl(var(--v4v-benefits)/0.3)]',
  mentalHealth: 'hover:border-[hsl(var(--v4v-mentalHealth)/0.3)]',
  supportServices: 'hover:border-[hsl(var(--v4v-supportServices)/0.3)]',
  healthcare: 'hover:border-[hsl(var(--v4v-healthcare)/0.3)]',
  education: 'hover:border-[hsl(var(--v4v-education)/0.3)]',
  financial: 'hover:border-[hsl(var(--v4v-financial)/0.3)]',
  family: 'hover:border-[hsl(var(--v4v-family)/0.3)]',
};

// Badge styling using design system - text is foreground (black) for readability
const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment)/0.12)] text-foreground border-[hsl(var(--v4v-employment)/0.25)]',
  training: 'bg-[hsl(var(--v4v-training)/0.12)] text-foreground border-[hsl(var(--v4v-training)/0.25)]',
  housing: 'bg-[hsl(var(--v4v-housing)/0.12)] text-foreground border-[hsl(var(--v4v-housing)/0.25)]',
  legal: 'bg-[hsl(var(--v4v-legal)/0.12)] text-foreground border-[hsl(var(--v4v-legal)/0.25)]',
  food: 'bg-[hsl(var(--v4v-food)/0.12)] text-foreground border-[hsl(var(--v4v-food)/0.25)]',
  benefits: 'bg-[hsl(var(--v4v-benefits)/0.12)] text-foreground border-[hsl(var(--v4v-benefits)/0.25)]',
  mentalHealth: 'bg-[hsl(var(--v4v-mentalHealth)/0.12)] text-foreground border-[hsl(var(--v4v-mentalHealth)/0.25)]',
  supportServices: 'bg-[hsl(var(--v4v-supportServices)/0.12)] text-foreground border-[hsl(var(--v4v-supportServices)/0.25)]',
  healthcare: 'bg-[hsl(var(--v4v-healthcare)/0.12)] text-foreground border-[hsl(var(--v4v-healthcare)/0.25)]',
  education: 'bg-[hsl(var(--v4v-education)/0.12)] text-foreground border-[hsl(var(--v4v-education)/0.25)]',
  financial: 'bg-[hsl(var(--v4v-financial)/0.12)] text-foreground border-[hsl(var(--v4v-financial)/0.25)]',
  family: 'bg-[hsl(var(--v4v-family)/0.12)] text-foreground border-[hsl(var(--v4v-family)/0.25)]',
};

// Category icons
const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: BookOpen,
  housing: Home,
  legal: Scale,
  food: UtensilsCrossed,
  benefits: Award,
  mentalHealth: Brain,
  supportServices: HeartHandshake,
  healthcare: HeartPulse,
  education: School,
  financial: Wallet,
  family: Users,
};

// Export for use in other components
export const categoryColors = categoryBadgeStyles;

// Source tier badge configuration
export type SourceTierBadge = {
  text: string;
  icon: string;
  className: string;
} | null;

export function getSourceTierBadge(tier: number | null, sourceName: string | null): SourceTierBadge {
  switch (tier) {
    case 1:
      return {
        text: 'Official',
        icon: '\u{1F3DB}\uFE0F', // Building emoji
        className: 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/50 dark:text-blue-200 dark:border-blue-700',
      };
    case 2:
      return {
        text: 'Nonprofit',
        icon: '\u2713', // Checkmark
        className: 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/50 dark:text-green-200 dark:border-green-700',
      };
    case 3:
      return {
        text: 'State Agency',
        icon: '\u{1F3DB}\uFE0F', // Building emoji
        className: 'bg-purple-100 text-purple-800 border-purple-300 dark:bg-purple-900/50 dark:text-purple-200 dark:border-purple-700',
      };
    case 4:
      // Tier 4: show source name only, no special badge styling
      return sourceName ? null : null;
    default:
      return null;
  }
}

// Border colors for logo container
const logoBorderColors: Record<string, string> = {
  employment: 'border-[hsl(var(--v4v-employment))]',
  training: 'border-[hsl(var(--v4v-training))]',
  housing: 'border-[hsl(var(--v4v-housing))]',
  legal: 'border-[hsl(var(--v4v-legal))]',
  food: 'border-[hsl(var(--v4v-food))]',
  benefits: 'border-[hsl(var(--v4v-benefits))]',
  mentalHealth: 'border-[hsl(var(--v4v-mentalHealth))]',
  supportServices: 'border-[hsl(var(--v4v-supportServices))]',
  healthcare: 'border-[hsl(var(--v4v-healthcare))]',
  education: 'border-[hsl(var(--v4v-education))]',
  financial: 'border-[hsl(var(--v4v-financial))]',
  family: 'border-[hsl(var(--v4v-family))]',
};

function ResourceLogo({
  logoUrl,
  fallbackIcon: FallbackIcon,
  size = 24,
  category,
}: {
  logoUrl: string | null;
  fallbackIcon: typeof Briefcase;
  size?: number;
  category?: string;
}) {
  const [hasError, setHasError] = useState(false);

  if (!logoUrl || hasError) {
    return <FallbackIcon className="h-5 w-5" />;
  }

  const borderColor = category ? logoBorderColors[category] || 'border-gray-300' : 'border-gray-300';

  return (
    <div className={`rounded-md border-2 ${borderColor} bg-slate-100 p-1 shadow-sm`}>
      <Image
        src={logoUrl}
        alt=""
        width={size}
        height={size}
        className="rounded-sm"
        onError={() => setHasError(true)}
        unoptimized
      />
    </div>
  );
}

function CardInner({
  resource,
  explanations: _explanations,
  showBookmark = false,
  renderBookmark = false,
  /** When true, phone numbers render as plain text (to avoid nested <a> in <Link>) */
  disablePhoneLinks = false,
  /** Distance in miles from search location */
  distance,
  /** Hide Local Provider section to save space */
  compact = false,
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
  /** Hide Local Provider section to save space */
  compact?: boolean;
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

      {/* Floating logo in top-left corner */}
      {resource.logo_url && (
        <div className="absolute left-3 top-3 z-10 transition-transform duration-300 group-hover:scale-110">
          <ResourceLogo
            logoUrl={resource.logo_url}
            fallbackIcon={CategoryIcon}
            size={28}
            category={primaryCategory}
          />
        </div>
      )}

      <CardHeader className={`pb-1 px-4 ${resource.logo_url ? 'pl-14 pt-3' : 'pt-4'}`}>
        {/* Top row: Icon + Badge + Bookmark */}
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2">
            {!resource.logo_url && (
              <div className={`shrink-0 rounded-lg p-2 ${accentBarColors[primaryCategory] || accentBarColors.employment} text-white transition-transform duration-300 group-hover:scale-110`}>
                <CategoryIcon className="h-5 w-5" />
              </div>
            )}
            {(() => {
              const tierBadge = getSourceTierBadge(resource.trust.source_tier, resource.trust.source_name);
              if (tierBadge) {
                return (
                  <Badge variant="outline" className={`text-xs ${tierBadge.className}`}>
                    <span>{tierBadge.icon}</span>
                    {tierBadge.text}
                  </Badge>
                );
              }
              // Tier 4: show source name only
              if (resource.trust.source_tier === 4 && resource.trust.source_name) {
                return (
                  <span className="text-xs text-muted-foreground">
                    via {resource.trust.source_name}
                  </span>
                );
              }
              return null;
            })()}
          </div>
          {/* Placeholder for bookmark button spacing */}
          {(showBookmark || renderBookmark) && <div className="h-6 w-6 shrink-0" />}
        </div>

        {/* Title - full width */}
        {resource.website && !disablePhoneLinks ? (
          <a
            href={resource.website}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="group/title block hover:underline"
          >
            <CardTitle className="font-display line-clamp-2 text-lg text-[hsl(var(--v4v-navy))] dark:text-foreground inline">
              {resource.title}
            </CardTitle>
            <ExternalLink className="h-3.5 w-3.5 ml-1 inline-block align-middle text-muted-foreground opacity-40 group-hover/title:opacity-100" />
          </a>
        ) : (
          <CardTitle className="font-display line-clamp-2 text-lg text-[hsl(var(--v4v-navy))] dark:text-foreground">
            {resource.title}
          </CardTitle>
        )}

        {/* Organization name */}
        <p className="text-sm text-muted-foreground mt-0.5">
          {resource.organization.name}
        </p>
      </CardHeader>

      <CardContent className="pt-0 px-4">
        {/* Description - truncated to 4 lines, full text shown on detail page */}
        <p className="mb-2 text-sm leading-relaxed text-muted-foreground line-clamp-4">
          {resource.summary || resource.description}
        </p>

        {/* Category and location badges */}
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
              className="gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.12)] text-foreground font-medium"
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
                className="gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.12)] text-foreground font-medium"
              >
                <MapPin className="h-3 w-3" />
                {state}
              </Badge>
            ))
          )}
          {resource.scope === 'national' && (
            <Badge
              variant="outline"
              className="gap-1 border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.12)] text-foreground font-medium"
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

        {/* Local provider contact info - hidden in compact mode */}
        {!compact && resource.location && (resource.location.intake?.phone || resource.location.intake?.hours) && (
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
  enableLayoutId = false,
  distance,
  compact = false,
}: ResourceCardProps) {
  const primaryCategory = resource.categories[0] || 'employment';

  // For modal/selectable variants, render bookmark inside card so it animates with the card
  const renderBookmarkInside = variant === 'modal' || variant === 'selectable';
  // For link variant, disable phone links to avoid nested <a> tags
  const isLinkVariant = variant === 'link';

  const cardContent = (
    <Card
      className={`category-card group relative h-full overflow-hidden border py-0 transition-all duration-300 ${
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
        compact={compact}
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
  const href = `/resources/${resource.id}`;

  return withBookmark(
    <Link href={href} className="block h-full">
      {cardContent}
    </Link>
  );
}
