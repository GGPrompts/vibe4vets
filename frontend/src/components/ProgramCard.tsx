'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Folder, ChevronDown, ChevronRight, MapPin, Building2 } from 'lucide-react';
import type { Program, Resource, MatchExplanation } from '@/lib/api';
import { ResourceCard } from './resource-card';

interface ProgramCardProps {
  program: Program;
  resources: Resource[];
  explanationsMap?: Map<string, MatchExplanation[]>;
  defaultExpanded?: boolean;
  onResourceClick?: (resource: Resource, explanations?: MatchExplanation[]) => void;
}

// Program type display names
const programTypeLabels: Record<string, string> = {
  ssvf: 'SSVF',
  hud_vash: 'HUD-VASH',
  gpd: 'GPD',
  hchv: 'HCHV',
  vets: 'VETS',
  other: 'Program',
};

// Program type descriptions
const programTypeDescriptions: Record<string, string> = {
  ssvf: 'Supportive Services for Veteran Families',
  hud_vash: 'HUD-VA Supportive Housing',
  gpd: 'Grant and Per Diem',
  hchv: 'Health Care for Homeless Veterans',
  vets: 'Veterans Employment and Training',
  other: 'Veteran Program',
};

export function ProgramCard({
  program,
  resources,
  explanationsMap,
  defaultExpanded = false,
  onResourceClick,
}: ProgramCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // Get unique states from resources
  const uniqueStates = [...new Set(resources.flatMap((r) => r.states))].slice(0, 5);
  const hasMoreStates = resources.flatMap((r) => r.states).length > 5;

  // Get program type label and description
  const typeLabel = programTypeLabels[program.program_type] || program.program_type.toUpperCase();
  const typeDescription = programTypeDescriptions[program.program_type] || '';

  return (
    <div className="space-y-3">
      {/* Program Header Card */}
      <Card
        className="group relative cursor-pointer overflow-hidden border-2 border-[hsl(var(--v4v-navy)/0.15)] bg-gradient-to-br from-[hsl(var(--v4v-navy)/0.03)] via-white to-[hsl(var(--v4v-navy)/0.06)] transition-all duration-300 hover:border-[hsl(var(--v4v-navy)/0.3)] hover:shadow-md"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* Accent bar - navy/indigo to differentiate from regular cards */}
        <div className="absolute left-0 top-0 h-1.5 w-full bg-[hsl(var(--v4v-navy))]" />

        {/* Decorative folder corner */}
        <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-[hsl(var(--v4v-navy))] opacity-[0.07] blur-2xl" />

        <CardHeader className="pb-3 pt-4">
          <div className="flex items-start gap-3">
            {/* Folder icon */}
            <div className="shrink-0 rounded-lg bg-[hsl(var(--v4v-navy))] p-2 text-white transition-transform duration-300 group-hover:scale-110">
              <Folder className="h-5 w-5" />
            </div>

            <div className="min-w-0 flex-1">
              {/* Program type badge */}
              <div className="mb-1 flex items-center gap-2">
                <Badge
                  variant="outline"
                  className="border-[hsl(var(--v4v-navy)/0.3)] bg-[hsl(var(--v4v-navy)/0.1)] text-[hsl(var(--v4v-navy))] font-semibold"
                >
                  {typeLabel}
                </Badge>
                {typeDescription && (
                  <span className="text-xs text-muted-foreground">{typeDescription}</span>
                )}
              </div>

              {/* Program name */}
              <CardTitle className="font-display line-clamp-2 text-lg text-[hsl(var(--v4v-navy))] dark:text-foreground">
                {program.name}
              </CardTitle>

              {/* Organization count */}
              <p className="mt-1 flex items-center gap-1.5 text-sm text-muted-foreground">
                <Building2 className="h-3.5 w-3.5" />
                {resources.length} provider{resources.length !== 1 ? 's' : ''}
              </p>
            </div>

            {/* Expand/collapse button */}
            <Button
              variant="ghost"
              size="sm"
              className="shrink-0 text-muted-foreground hover:text-foreground"
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-5 w-5" />
              ) : (
                <ChevronRight className="h-5 w-5" />
              )}
            </Button>
          </div>
        </CardHeader>

        <CardContent className="pt-0">
          {/* Program description */}
          {program.description && (
            <p className="mb-3 line-clamp-2 text-sm leading-relaxed text-muted-foreground">
              {program.description}
            </p>
          )}

          {/* Services offered */}
          {program.services_offered && program.services_offered.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-1.5">
              {program.services_offered.slice(0, 4).map((service) => (
                <Badge
                  key={service}
                  variant="outline"
                  className="border-muted-foreground/20 bg-muted/50 text-muted-foreground text-xs py-0 h-5 font-normal"
                >
                  {service.replace(/_/g, ' ')}
                </Badge>
              ))}
              {program.services_offered.length > 4 && (
                <Badge
                  variant="outline"
                  className="border-muted-foreground/20 bg-muted/50 text-muted-foreground text-xs py-0 h-5 font-normal"
                >
                  +{program.services_offered.length - 4}
                </Badge>
              )}
            </div>
          )}

          {/* Coverage states */}
          {uniqueStates.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
              {uniqueStates.map((state) => (
                <Badge
                  key={state}
                  variant="outline"
                  className="border-[hsl(var(--v4v-gold)/0.4)] bg-[hsl(var(--v4v-gold)/0.08)] text-[hsl(var(--v4v-gold))] text-xs py-0 h-5 font-medium"
                >
                  {state}
                </Badge>
              ))}
              {hasMoreStates && (
                <span className="text-xs text-muted-foreground">
                  & more
                </span>
              )}
            </div>
          )}

          {/* Expand hint */}
          <p className="mt-3 text-xs text-muted-foreground">
            {isExpanded ? 'Click to collapse' : 'Click to see providers'}
          </p>
        </CardContent>
      </Card>

      {/* Expanded Resources */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="ml-4 space-y-3 border-l-2 border-[hsl(var(--v4v-navy)/0.15)] pl-4">
              {resources.map((resource) => (
                <ResourceCard
                  key={resource.id}
                  resource={resource}
                  explanations={explanationsMap?.get(resource.id)}
                  variant="modal"
                  onClick={() => onResourceClick?.(resource, explanationsMap?.get(resource.id))}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
