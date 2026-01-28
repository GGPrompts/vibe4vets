'use client';

import { Briefcase, GraduationCap, Home as HomeIcon, Scale, UtensilsCrossed, FileCheck, Brain, HeartHandshake, HeartPulse, School, Wallet, Users } from 'lucide-react';

const categories = [
  {
    name: 'Employment',
    slug: 'employment',
    description: 'Job placement, career services, and Veteran-friendly employers',
    icon: Briefcase,
    colorClass: 'bg-v4v-employment',
    mutedBgClass: 'bg-v4v-employment-muted',
    textClass: 'text-v4v-employment',
  },
  {
    name: 'Training',
    slug: 'training',
    description: 'Vocational rehabilitation, certifications, and skill-building programs',
    icon: GraduationCap,
    colorClass: 'bg-v4v-training',
    mutedBgClass: 'bg-v4v-training-muted',
    textClass: 'text-v4v-training',
  },
  {
    name: 'Housing',
    slug: 'housing',
    description: 'HUD-VASH, SSVF, transitional housing, and shelter resources',
    icon: HomeIcon,
    colorClass: 'bg-v4v-housing',
    mutedBgClass: 'bg-v4v-housing-muted',
    textClass: 'text-v4v-housing',
  },
  {
    name: 'Legal',
    slug: 'legal',
    description: 'Legal aid, VA appeals assistance, and advocacy services',
    icon: Scale,
    colorClass: 'bg-v4v-legal',
    mutedBgClass: 'bg-v4v-legal-muted',
    textClass: 'text-v4v-legal',
  },
  {
    name: 'Food',
    slug: 'food',
    description: 'Food pantries, meal programs, and emergency food assistance',
    icon: UtensilsCrossed,
    colorClass: 'bg-v4v-food',
    mutedBgClass: 'bg-v4v-food-muted',
    textClass: 'text-v4v-food',
  },
  {
    name: 'Benefits',
    slug: 'benefits',
    description: 'VA claims assistance, benefits counseling, and VSO services',
    icon: FileCheck,
    colorClass: 'bg-v4v-benefits',
    mutedBgClass: 'bg-v4v-benefits-muted',
    textClass: 'text-v4v-benefits',
  },
  {
    name: 'Mental Health',
    slug: 'mentalHealth',
    description: 'Counseling, PTSD support, crisis services, and mental wellness programs',
    icon: Brain,
    colorClass: 'bg-v4v-mentalHealth',
    mutedBgClass: 'bg-v4v-mentalHealth-muted',
    textClass: 'text-v4v-mentalHealth',
  },
  {
    name: 'Support Services',
    slug: 'supportServices',
    description: 'General veteran support, peer mentoring, and case management',
    icon: HeartHandshake,
    colorClass: 'bg-v4v-supportServices',
    mutedBgClass: 'bg-v4v-supportServices-muted',
    textClass: 'text-v4v-supportServices',
  },
  {
    name: 'Healthcare',
    slug: 'healthcare',
    description: 'Medical care, VA health services, and wellness programs',
    icon: HeartPulse,
    colorClass: 'bg-v4v-healthcare',
    mutedBgClass: 'bg-v4v-healthcare-muted',
    textClass: 'text-v4v-healthcare',
  },
  {
    name: 'Education',
    slug: 'education',
    description: 'College programs, scholarships, and academic support',
    icon: School,
    colorClass: 'bg-v4v-education',
    mutedBgClass: 'bg-v4v-education-muted',
    textClass: 'text-v4v-education',
  },
  {
    name: 'Financial',
    slug: 'financial',
    description: 'Financial counseling, emergency assistance, and debt relief',
    icon: Wallet,
    colorClass: 'bg-v4v-financial',
    mutedBgClass: 'bg-v4v-financial-muted',
    textClass: 'text-v4v-financial',
  },
  {
    name: 'Family',
    slug: 'family',
    description: 'Resources for spouses, dependents, survivors, and childcare support',
    icon: Users,
    colorClass: 'bg-v4v-family',
    mutedBgClass: 'bg-v4v-family-muted',
    textClass: 'text-v4v-family',
  },
];

interface CategoryCardsProps {
  selectedCategories: string[];
  onToggleCategory: (category: string) => void;
}

export function CategoryCards({ selectedCategories, onToggleCategory }: CategoryCardsProps) {
  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {categories.map((category) => {
        const Icon = category.icon;
        const isSelected = selectedCategories.includes(category.slug);
        return (
          <button
            key={category.slug}
            type="button"
            onClick={() => onToggleCategory(category.slug)}
            className={`soft-card category-card group relative overflow-hidden p-5 text-left transition-all duration-200 ${
              isSelected
                ? 'ring-2 ring-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.05)]'
                : ''
            }`}
          >
            {/* Color accent bar */}
            <div
              className={`absolute left-0 top-0 w-full transition-all duration-300 ${category.colorClass} ${
                isSelected ? 'h-1.5' : 'h-1 group-hover:h-1.5'
              }`}
            />

            {/* Icon */}
            <div
              className={`mb-3 inline-flex rounded-lg p-2.5 ${category.mutedBgClass} transition-transform duration-300 group-hover:scale-110`}
            >
              <Icon className={`h-5 w-5 ${category.textClass}`} />
            </div>

            {/* Content */}
            <h3 className="font-display text-lg font-medium text-foreground">
              {category.name}
            </h3>
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
              {category.description}
            </p>

            {/* Selected indicator */}
            {isSelected && (
              <div className="absolute right-3 top-3">
                <div className="h-2.5 w-2.5 rounded-full bg-[hsl(var(--v4v-gold))]" />
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}

export { categories };
