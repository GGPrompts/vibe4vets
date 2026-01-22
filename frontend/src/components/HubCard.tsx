import { ExternalLink } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface HubResource {
  name: string;
  description: string;
  url: string;
  icon?: LucideIcon;
}

interface HubCardProps {
  resource: HubResource;
  category: 'employment' | 'training' | 'housing' | 'legal' | 'food' | 'benefits';
}

const categoryColors: Record<string, string> = {
  employment: 'bg-v4v-employment',
  training: 'bg-v4v-training',
  housing: 'bg-v4v-housing',
  legal: 'bg-v4v-legal',
  food: 'bg-v4v-food',
  benefits: 'bg-v4v-benefits',
};

export function HubCard({ resource, category }: HubCardProps) {
  const Icon = resource.icon;

  return (
    <a
      href={resource.url}
      target="_blank"
      rel="noopener noreferrer"
      className="category-card group relative overflow-hidden rounded-xl bg-white p-6 shadow-sm"
    >
      {/* Color accent bar */}
      <div className={`absolute left-0 top-0 h-1 w-full ${categoryColors[category]}`} />

      {/* Header with icon */}
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className={`inline-flex rounded-lg ${categoryColors[category]} p-2 text-white transition-transform duration-300 group-hover:scale-110`}>
              <Icon className="h-5 w-5" />
            </div>
          )}
          <h3 className="font-display text-lg text-[hsl(var(--v4v-navy))] group-hover:text-[hsl(var(--v4v-gold))] transition-colors duration-300">
            {resource.name}
          </h3>
        </div>
        <ExternalLink className="h-4 w-4 text-[hsl(var(--muted-foreground))] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
      </div>

      {/* Description */}
      <p className="text-sm leading-relaxed text-[hsl(var(--muted-foreground))]">
        {resource.description}
      </p>

      {/* URL hint */}
      <p className="mt-3 text-xs text-[hsl(var(--v4v-gold))] opacity-0 transition-opacity duration-300 group-hover:opacity-100 truncate">
        {new URL(resource.url).hostname}
      </p>
    </a>
  );
}
