'use client';

import { useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useDragControls, PanInfo } from 'framer-motion';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
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
} from 'lucide-react';
import type { Resource, MatchExplanation } from '@/lib/api';
import { cn } from '@/lib/utils';

interface ResourceDetailModalProps {
  resource: Resource | null;
  explanations?: MatchExplanation[];
  isOpen: boolean;
  onClose: () => void;
}

// Category styles
const categoryGradients: Record<string, string> = {
  employment: 'from-blue-600 to-blue-800',
  training: 'from-purple-600 to-purple-800',
  housing: 'from-green-600 to-green-800',
  legal: 'from-amber-600 to-amber-800',
};

const categoryIcons: Record<string, typeof Briefcase> = {
  employment: Briefcase,
  training: BookOpen,
  housing: Home,
  legal: Scale,
};

const categoryBadgeStyles: Record<string, string> = {
  employment: 'bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-200',
  training: 'bg-purple-100 text-purple-800 dark:bg-purple-900/60 dark:text-purple-200',
  housing: 'bg-green-100 text-green-800 dark:bg-green-900/60 dark:text-green-200',
  legal: 'bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200',
};

function IntakeSection({ resource }: { resource: Resource }) {
  const location = resource.location;
  const intake = location?.intake;
  const eligibility = location?.eligibility;
  const verification = location?.verification;

  if (!intake && !eligibility?.docs_required?.length) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h3 className="flex items-center gap-2 text-lg font-semibold">
        <FileText className="h-5 w-5 text-[hsl(var(--v4v-gold))]" />
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

  return (
    <DialogPrimitive.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <AnimatePresence>
        {isOpen && (
          <DialogPrimitive.Portal forceMount>
            {/* Overlay */}
            <DialogPrimitive.Overlay asChild>
              <motion.div
                className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                onClick={onClose}
              />
            </DialogPrimitive.Overlay>

            {/* Content */}
            <DialogPrimitive.Content
              asChild
              onOpenAutoFocus={(e) => e.preventDefault()}
              aria-describedby={undefined}
            >
              <motion.div
                ref={constraintsRef}
                className="fixed inset-x-0 bottom-0 z-50 max-h-[90vh] overflow-hidden rounded-t-2xl bg-background shadow-2xl outline-none sm:inset-x-auto sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:max-h-[85vh] sm:w-full sm:max-w-2xl sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl"
                layoutId={`resource-card-${resource.id}`}
                initial={{ y: '100%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: '100%', opacity: 0 }}
                transition={{
                  type: 'spring',
                  damping: 30,
                  stiffness: 300,
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
                <div className={cn('bg-gradient-to-br p-6 text-white', gradient)}>
                  {/* Close button */}
                  <DialogPrimitive.Close
                    className="absolute right-4 top-4 rounded-full bg-white/20 p-2 transition-colors hover:bg-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
                    aria-label="Close"
                  >
                    <X className="h-5 w-5" />
                  </DialogPrimitive.Close>

                  {/* Mobile: pull down indicator */}
                  <div className="absolute left-1/2 top-4 -translate-x-1/2 sm:hidden">
                    <ChevronDown className="h-5 w-5 animate-bounce opacity-60" />
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
                  <DialogPrimitive.Title className="font-display mb-2 text-2xl font-bold leading-tight sm:text-3xl">
                    {resource.title}
                  </DialogPrimitive.Title>

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
                <div className="max-h-[calc(90vh-280px)] overflow-y-auto p-6 sm:max-h-[calc(85vh-280px)]">
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
                  <div className="mb-6">
                    <h3 className="mb-2 text-lg font-semibold">About This Resource</h3>
                    <p className="whitespace-pre-wrap text-muted-foreground">
                      {resource.description}
                    </p>
                  </div>

                  {/* Eligibility */}
                  {resource.eligibility && (
                    <div className="mb-6">
                      <h3 className="mb-2 text-lg font-semibold">Eligibility</h3>
                      <p className="whitespace-pre-wrap text-muted-foreground">
                        {resource.eligibility}
                      </p>
                    </div>
                  )}

                  <Separator className="my-6" />

                  {/* Intake section */}
                  <IntakeSection resource={resource} />

                  {/* Additional Info */}
                  <div className="mt-6 space-y-4">
                    {resource.hours && (
                      <div className="flex items-start gap-3">
                        <Clock className="mt-0.5 h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm font-medium">Hours</p>
                          <p className="text-sm text-muted-foreground">{resource.hours}</p>
                        </div>
                      </div>
                    )}

                    {resource.cost && (
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <p className="font-medium text-green-600 dark:text-green-400">
                          {resource.cost}
                        </p>
                      </div>
                    )}

                    {/* Coverage */}
                    <div>
                      <p className="mb-2 text-sm font-medium">Coverage</p>
                      <div className="flex flex-wrap gap-1">
                        {resource.scope === 'national' ? (
                          <Badge variant="outline">Nationwide</Badge>
                        ) : (
                          resource.states.map((state) => (
                            <Badge key={state} variant="outline">
                              {state}
                            </Badge>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Languages */}
                    {resource.languages.length > 0 && (
                      <div>
                        <p className="mb-2 text-sm font-medium">Languages</p>
                        <div className="flex flex-wrap gap-1">
                          {resource.languages.map((lang) => (
                            <Badge key={lang} variant="secondary">
                              {lang.toUpperCase()}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            </DialogPrimitive.Content>
          </DialogPrimitive.Portal>
        )}
      </AnimatePresence>
    </DialogPrimitive.Root>
  );
}

export default ResourceDetailModal;
