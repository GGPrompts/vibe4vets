'use client';

import { useEffect, useCallback, useRef, useState } from 'react';
import Image from 'next/image';
import { motion, AnimatePresence, useDragControls, PanInfo } from 'framer-motion';
// Radix Dialog removed - using plain motion components for simpler state management
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useOptionalMagnifier } from '@/context/magnifier-context';
import {
  Phone,
  Globe,
  MapPin,
  Clock,
  FileText,
  CheckCircle2,
  AlertCircle,
  X,
  ExternalLink,
  Briefcase,
  BookOpen,
  Home,
  Scale,
  ChevronDown,
  UtensilsCrossed,
  Award,
  Tag,
} from 'lucide-react';
import { BookmarkButton } from '@/components/bookmark-button';
import { ReportFeedbackModal } from '@/components/ReportFeedbackModal';
import type { Resource, MatchExplanation } from '@/lib/api';
import { cn } from '@/lib/utils';

interface ResourceDetailModalProps {
  resource: Resource | null;
  explanations?: MatchExplanation[];
  isOpen: boolean;
  onClose: () => void;
}

// Category styles - use CSS variables for consistency
const categoryGradients: Record<string, string> = {
  employment: 'bg-gradient-to-br from-[hsl(var(--v4v-employment))] to-[hsl(215,70%,40%)]',
  training: 'bg-gradient-to-br from-[hsl(var(--v4v-training))] to-[hsl(165,55%,32%)]',
  housing: 'bg-gradient-to-br from-[hsl(var(--v4v-housing))] to-[hsl(24,75%,42%)]',
  legal: 'bg-gradient-to-br from-[hsl(var(--v4v-legal))] to-[hsl(265,50%,45%)]',
  food: 'bg-gradient-to-br from-[hsl(var(--v4v-food))] to-[hsl(145,55%,32%)]',
  benefits: 'bg-gradient-to-br from-[hsl(var(--v4v-benefits))] to-[hsl(340,55%,40%)]',
};

// Body background tints - solid white for readability (no gradient transparency)
const bodyBackgrounds: Record<string, string> = {
  employment: 'bg-white',
  training: 'bg-white',
  housing: 'bg-white',
  legal: 'bg-white',
  food: 'bg-white',
  benefits: 'bg-white',
};

// Decorative orb colors
const decorativeOrbs: Record<string, string> = {
  employment: 'bg-[hsl(var(--v4v-employment))]',
  training: 'bg-[hsl(var(--v4v-training))]',
  housing: 'bg-[hsl(var(--v4v-housing))]',
  legal: 'bg-[hsl(var(--v4v-legal))]',
  food: 'bg-[hsl(var(--v4v-food))]',
  benefits: 'bg-[hsl(var(--v4v-benefits))]',
};

const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: BookOpen,
  housing: Home,
  legal: Scale,
  food: UtensilsCrossed,
  benefits: Award,
};

// Badge styles for header - white background with category color text for contrast
const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-white/90 text-[hsl(var(--v4v-employment))]',
  training: 'bg-white/90 text-[hsl(var(--v4v-training))]',
  housing: 'bg-white/90 text-[hsl(var(--v4v-housing))]',
  legal: 'bg-white/90 text-[hsl(var(--v4v-legal))]',
  food: 'bg-white/90 text-[hsl(var(--v4v-food))]',
  benefits: 'bg-white/90 text-[hsl(var(--v4v-benefits))]',
};

// Section card styling
const sectionCardStyle = 'rounded-xl border bg-white p-4 shadow-sm';

function ResourceModalLogo({
  logoUrl,
  fallbackIcon: FallbackIcon,
  size = 24,
}: {
  logoUrl: string | null;
  fallbackIcon: typeof Briefcase;
  size?: number;
}) {
  const [hasError, setHasError] = useState(false);

  if (!logoUrl || hasError) {
    return <FallbackIcon className="h-6 w-6" />;
  }

  return (
    <Image
      src={logoUrl}
      alt=""
      width={size}
      height={size}
      className="rounded-sm"
      onError={() => setHasError(true)}
      unoptimized
    />
  );
}

function IntakeSection({ resource }: { resource: Resource }) {
  const location = resource.location;
  const intake = location?.intake;
  const eligibility = location?.eligibility;
  const verification = location?.verification;

  if (!intake && !eligibility?.docs_required?.length) {
    return null;
  }

  return (
    <div className={cn(sectionCardStyle, 'space-y-4')}>
      <h3 className="flex items-center gap-2 text-lg font-semibold text-[hsl(var(--v4v-navy))]">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--v4v-gold)/0.1)]">
          <FileText className="h-4 w-4 text-[hsl(var(--v4v-gold-dark))]" />
        </div>
        How to Apply
      </h3>

      {/* Intake Contact Methods */}
      <div className="grid gap-3 sm:grid-cols-2">
        {intake?.phone && (
          <a
            href={`tel:${intake.phone}`}
            className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/40">
              <Phone className="h-5 w-5 text-green-700 dark:text-green-400" />
            </div>
            <div className="min-w-0">
              <p className="font-medium">Call to Apply</p>
              <p className="truncate text-sm text-muted-foreground">{intake.phone}</p>
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
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/40">
              <Globe className="h-5 w-5 text-blue-700 dark:text-blue-400" />
            </div>
            <div className="min-w-0">
              <p className="font-medium">Apply Online</p>
              <p className="truncate text-sm text-muted-foreground">Visit website</p>
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
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/40">
              <MapPin className="h-5 w-5 text-purple-700 dark:text-purple-400" />
            </div>
            <div className="min-w-0">
              <p className="font-medium">Get Directions</p>
              <p className="truncate text-sm text-muted-foreground">
                {location.city}, {location.state}
              </p>
            </div>
          </a>
        )}
      </div>

      {/* Intake Hours */}
      {intake?.hours && (
        <div className="flex items-start gap-3 rounded-lg bg-muted/50 p-3">
          <Clock className="mt-0.5 h-4 w-4 text-muted-foreground" />
          <div>
            <p className="text-sm font-medium">Intake Hours</p>
            <p className="text-sm text-muted-foreground">{intake.hours}</p>
          </div>
        </div>
      )}

      {/* Intake Notes */}
      {intake?.notes && (
        <div className="rounded-lg bg-amber-50 p-3 dark:bg-amber-900/20">
          <div className="flex items-start gap-2">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400" />
            <p className="text-sm text-amber-800 dark:text-amber-200">{intake.notes}</p>
          </div>
        </div>
      )}

      {/* Documents Required */}
      {eligibility?.docs_required && eligibility.docs_required.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-medium">What to Bring</p>
          <ul className="space-y-2">
            {eligibility.docs_required.map((doc, index) => (
              <li key={index} className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-green-600 dark:text-green-400" />
                {doc}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Verification & Waitlist */}
      <div className="flex flex-wrap items-center gap-3 pt-2">
        {verification?.last_verified_at && (
          <Badge variant="outline" className="text-xs">
            Verified {new Date(verification.last_verified_at).toLocaleDateString()}
          </Badge>
        )}
        {eligibility?.waitlist_status && (
          <Badge
            className={cn(
              'text-xs',
              eligibility.waitlist_status === 'open'
                ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                : eligibility.waitlist_status === 'closed'
                ? 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                : ''
            )}
          >
            Waitlist: {eligibility.waitlist_status}
          </Badge>
        )}
      </div>
    </div>
  );
}

export function ResourceDetailModal({
  resource,
  explanations,
  isOpen,
  onClose,
}: ResourceDetailModalProps) {
  const dragControls = useDragControls();
  const constraintsRef = useRef<HTMLDivElement>(null);
  const magnifierContext = useOptionalMagnifier();

  // Suppress magnifier when modal is open
  useEffect(() => {
    if (isOpen) {
      magnifierContext?.setSuppressed(true);
      return () => {
        magnifierContext?.setSuppressed(false);
      };
    }
  }, [isOpen, magnifierContext]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

      // Apply styles to lock scroll while maintaining position
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;

      return () => {
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
      };
    }
  }, [isOpen]);

  // Handle mobile swipe to close
  const handleDragEnd = useCallback(
    (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
      if (info.offset.y > 100 || info.velocity.y > 500) {
        onClose();
      }
    },
    [onClose]
  );

  if (!resource) return null;

  const primaryCategory = resource.categories[0] || 'employment';
  const CategoryIcon = categoryIcons[primaryCategory] || Briefcase;
  const gradient = categoryGradients[primaryCategory] || categoryGradients.employment;
  const bodyBg = bodyBackgrounds[primaryCategory] || bodyBackgrounds.employment;
  const orbColor = decorativeOrbs[primaryCategory] || decorativeOrbs.employment;

  return (
    <AnimatePresence mode="wait">
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Content */}
          <motion.div
            ref={constraintsRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            className={cn(
              'fixed inset-x-0 bottom-0 max-h-[90vh] overflow-hidden rounded-t-2xl shadow-2xl outline-none',
              'sm:inset-x-auto sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:max-h-[85vh] sm:w-full sm:max-w-2xl sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl',
              bodyBg
            )}
            layoutId={`resource-card-${resource.id}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ zIndex: 100 }}
            transition={{
              layout: {
                type: 'spring',
                damping: 25,
                stiffness: 200,
              },
              opacity: { duration: 0.2 },
            }}
            drag="y"
            dragControls={dragControls}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.5 }}
            onDragEnd={handleDragEnd}
          >
                {/* Mobile drag handle */}
                <div className="flex justify-center py-3 sm:hidden">
                  <div className="h-1.5 w-12 rounded-full bg-muted-foreground/30" />
                </div>

                {/* Header with gradient background */}
                <div className={cn('p-6 text-white', gradient)}>
                  {/* Header action buttons */}
                  <div className="absolute right-4 top-4 flex items-center gap-2">
                    {/* Bookmark button */}
                    <BookmarkButton
                      resourceId={resource.id}
                      variant="gold"
                      size="default"
                      showTooltip={false}
                      className="bg-white/20 border-0 hover:bg-white/30 text-white hover:text-[hsl(var(--v4v-gold))]"
                    />
                    {/* Close button */}
                    <button
                      onClick={onClose}
                      type="button"
                      className="rounded-full bg-white/20 p-2 transition-colors hover:bg-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
                      aria-label="Close"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  {/* Mobile: pull down indicator */}
                  <div className="absolute left-1/2 top-4 -translate-x-1/2 sm:hidden">
                    <ChevronDown className="h-5 w-5 animate-bounce opacity-60" />
                  </div>

                  {/* Logo/Category icon and badges */}
                  <div className="mb-4 flex items-center gap-3">
                    <div className="rounded-xl bg-white/20 p-3">
                      <ResourceModalLogo
                        logoUrl={resource.logo_url}
                        fallbackIcon={CategoryIcon}
                        size={24}
                      />
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {resource.categories.map((cat) => (
                        <Badge
                          key={cat}
                          className={cn(
                            'border-0 font-medium capitalize',
                            categoryBadgeStyles[cat] || ''
                          )}
                        >
                          {cat}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Title */}
                  <h2 id="modal-title" className="font-display mb-2 text-2xl font-bold leading-tight sm:text-3xl">
                    {resource.title}
                  </h2>

                  {/* Organization */}
                  <p className="text-white/90">{resource.organization.name}</p>

                  {/* Match reasons if available */}
                  {explanations && explanations.length > 0 && (
                    <div className="mt-4 rounded-lg bg-white/10 p-3">
                      <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Why this matched
                      </p>
                      <ul className="space-y-1">
                        {explanations.slice(0, 3).map((exp, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-white/90">
                            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-white/70" />
                            {exp.reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Scrollable content */}
                <div className="relative max-h-[calc(90vh-280px)] overflow-x-hidden overflow-y-auto overscroll-contain p-6 sm:max-h-[calc(85vh-280px)]">
                  {/* Decorative orbs */}
                  <div
                    className={cn(
                      'pointer-events-none absolute -right-20 top-20 h-40 w-40 rounded-full opacity-[0.04] blur-3xl',
                      orbColor
                    )}
                  />
                  <div
                    className={cn(
                      'pointer-events-none absolute -left-20 bottom-40 h-32 w-32 rounded-full opacity-[0.03] blur-3xl',
                      orbColor
                    )}
                  />
                  {/* Primary CTAs */}
                  <div className="mb-6 flex flex-wrap gap-3">
                    {resource.website && (
                      <Button asChild className="gap-2">
                        <a href={resource.website} target="_blank" rel="noopener noreferrer">
                          <Globe className="h-4 w-4" />
                          Visit Website
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </Button>
                    )}
                    {resource.phone && (
                      <Button variant="outline" asChild className="gap-2">
                        <a href={`tel:${resource.phone}`}>
                          <Phone className="h-4 w-4" />
                          {resource.phone}
                        </a>
                      </Button>
                    )}
                    {resource.location && (
                      <Button variant="outline" asChild className="gap-2">
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

                  {/* Description */}
                  <div className={cn(sectionCardStyle, 'relative mb-6')}>
                    <h3 className="mb-3 text-lg font-semibold text-[hsl(var(--v4v-navy))]">About This Resource</h3>
                    <p className="whitespace-pre-wrap leading-relaxed text-muted-foreground">
                      {resource.description}
                    </p>
                  </div>

                  {/* Local Provider Contact */}
                  {resource.location && (resource.location.address || resource.location.intake?.phone) && (
                    <div className={cn(sectionCardStyle, 'relative mb-6 border-l-4 border-l-[hsl(var(--v4v-gold))]')}>
                      <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-[hsl(var(--v4v-navy))]">
                        <MapPin className="h-5 w-5 text-[hsl(var(--v4v-gold-dark))]" />
                        Local Provider Contact
                      </h3>
                      <div className="space-y-3">
                        {/* Address */}
                        {resource.location.address && (
                          <a
                            href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                              `${resource.location.address}, ${resource.location.city}, ${resource.location.state}`
                            )}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-start gap-3 rounded-lg p-2 transition-colors hover:bg-muted/50"
                          >
                            <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--v4v-gold-dark))]" />
                            <div>
                              <p className="font-medium">{resource.location.address}</p>
                              <p className="text-sm text-muted-foreground">
                                {resource.location.city}, {resource.location.state}
                              </p>
                            </div>
                          </a>
                        )}

                        {/* Phone */}
                        {resource.location.intake?.phone && (
                          <a
                            href={`tel:${resource.location.intake.phone}`}
                            className="flex items-center gap-3 rounded-lg p-2 transition-colors hover:bg-muted/50"
                          >
                            <Phone className="h-5 w-5 shrink-0 text-green-600" />
                            <div>
                              <p className="font-medium">{resource.location.intake.phone}</p>
                              <p className="text-sm text-muted-foreground">Call for intake</p>
                            </div>
                          </a>
                        )}

                        {/* Hours */}
                        {resource.location.intake?.hours && (
                          <div className="flex items-center gap-3 p-2">
                            <Clock className="h-5 w-5 shrink-0 text-muted-foreground" />
                            <div>
                              <p className="text-sm text-muted-foreground">{resource.location.intake.hours}</p>
                            </div>
                          </div>
                        )}

                        {/* Service Area */}
                        {resource.location.service_area && resource.location.service_area.length > 0 && (
                          <div className="flex items-start gap-3 p-2">
                            <Globe className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
                            <div>
                              <p className="text-sm font-medium">Service Area</p>
                              <p className="text-sm text-muted-foreground">
                                {resource.location.service_area.join(', ')}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Eligibility */}
                  {resource.eligibility && (
                    <div className={cn(sectionCardStyle, 'relative mb-6')}>
                      <h3 className="mb-3 text-lg font-semibold text-[hsl(var(--v4v-navy))]">Eligibility</h3>
                      <p className="whitespace-pre-wrap leading-relaxed text-muted-foreground">
                        {resource.eligibility}
                      </p>
                    </div>
                  )}

                  <Separator className="my-6" />

                  {/* Intake section */}
                  <IntakeSection resource={resource} />

                  {/* Additional Info */}
                  <div className={cn(sectionCardStyle, 'mt-6')}>
                    <h3 className="mb-4 text-lg font-semibold text-[hsl(var(--v4v-navy))]">Details</h3>
                    <div className="space-y-4">
                      {resource.hours && (
                        <div className="flex items-start gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[hsl(var(--v4v-navy)/0.08)]">
                            <Clock className="h-4 w-4 text-[hsl(var(--v4v-navy))]" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">Hours</p>
                            <p className="text-sm text-muted-foreground">{resource.hours}</p>
                          </div>
                        </div>
                      )}

                      {resource.cost && (
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-green-100">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                          </div>
                          <p className="font-medium text-green-600 dark:text-green-400">
                            {resource.cost}
                          </p>
                        </div>
                      )}

                      {/* Coverage */}
                      <div className="flex items-start gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[hsl(var(--v4v-gold)/0.1)]">
                          <Globe className="h-4 w-4 text-[hsl(var(--v4v-gold-dark))]" />
                        </div>
                        <div>
                          <p className="mb-1 text-sm font-medium">Coverage</p>
                          <div className="flex flex-wrap gap-1">
                            {resource.scope === 'national' ? (
                              <Badge variant="outline" className="border-[hsl(var(--v4v-gold)/0.3)] bg-[hsl(var(--v4v-gold)/0.08)]">Nationwide</Badge>
                            ) : (
                              resource.states.map((state) => (
                                <Badge key={state} variant="outline">
                                  {state}
                                </Badge>
                              ))
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Languages */}
                      {resource.languages.length > 0 && (
                        <div className="flex items-start gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[hsl(var(--v4v-legal)/0.08)]">
                            <FileText className="h-4 w-4 text-[hsl(var(--v4v-legal))]" />
                          </div>
                          <div>
                            <p className="mb-1 text-sm font-medium">Languages</p>
                            <div className="flex flex-wrap gap-1">
                              {resource.languages.map((lang) => (
                                <Badge key={lang} variant="secondary">
                                  {lang.toUpperCase()}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Tags - at bottom as metadata */}
                  {resource.tags && resource.tags.length > 0 && (
                    <div className={cn(sectionCardStyle, 'mt-6')}>
                      <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-[hsl(var(--v4v-navy))]">
                        <Tag className="h-5 w-5 text-muted-foreground" />
                        Tags
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {resource.tags.map((tag) => (
                          <Badge
                            key={tag}
                            variant="outline"
                            className="gap-1 border-muted-foreground/20 bg-muted/50 text-muted-foreground"
                          >
                            <span className="capitalize">{tag.replace(/_/g, ' ')}</span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Report Issue */}
                  <div className="mt-6 flex justify-center border-t pt-6">
                    <ReportFeedbackModal
                      resourceId={resource.id}
                      resourceTitle={resource.title}
                    />
                  </div>
                </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default ResourceDetailModal;
