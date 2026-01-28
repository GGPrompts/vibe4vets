'use client';

import Link from 'next/link';
import { Briefcase, GraduationCap, Home, Scale, UtensilsCrossed, FileCheck, Brain, HeartHandshake, HeartPulse, School, Wallet } from 'lucide-react';

const categories = [
  {
    name: 'Employment',
    slug: 'employment',
    icon: Briefcase,
    color: 'bg-[hsl(var(--v4v-employment))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-employment-light))]',
  },
  {
    name: 'Training',
    slug: 'training',
    icon: GraduationCap,
    color: 'bg-[hsl(var(--v4v-training))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-training-light))]',
  },
  {
    name: 'Housing',
    slug: 'housing',
    icon: Home,
    color: 'bg-[hsl(var(--v4v-housing))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-housing-light))]',
  },
  {
    name: 'Legal',
    slug: 'legal',
    icon: Scale,
    color: 'bg-[hsl(var(--v4v-legal))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-legal-light))]',
  },
  {
    name: 'Food',
    slug: 'food',
    icon: UtensilsCrossed,
    color: 'bg-[hsl(var(--v4v-food))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-food-light))]',
  },
  {
    name: 'Benefits',
    slug: 'benefits',
    icon: FileCheck,
    color: 'bg-[hsl(var(--v4v-benefits))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-benefits-light))]',
  },
  {
    name: 'Mental Health',
    slug: 'mentalHealth',
    icon: Brain,
    color: 'bg-[hsl(var(--v4v-mentalHealth))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-mentalHealth-light))]',
  },
  {
    name: 'Support',
    slug: 'supportServices',
    icon: HeartHandshake,
    color: 'bg-[hsl(var(--v4v-supportServices))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-supportServices-light))]',
  },
  {
    name: 'Healthcare',
    slug: 'healthcare',
    icon: HeartPulse,
    color: 'bg-[hsl(var(--v4v-healthcare))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-healthcare-light))]',
  },
  {
    name: 'Education',
    slug: 'education',
    icon: School,
    color: 'bg-[hsl(var(--v4v-education))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-education-light))]',
  },
  {
    name: 'Financial',
    slug: 'financial',
    icon: Wallet,
    color: 'bg-[hsl(var(--v4v-financial))]',
    hoverColor: 'hover:bg-[hsl(var(--v4v-financial-light))]',
  },
];

interface CategoryButtonsProps {
  variant?: 'default' | 'compact';
}

export function CategoryButtons({ variant = 'default' }: CategoryButtonsProps) {
  const isCompact = variant === 'compact';

  return (
    <div className="flex flex-wrap justify-center gap-3">
      {categories.map((cat) => {
        const Icon = cat.icon;
        return (
          <Link
            key={cat.slug}
            href={`/search?category=${cat.slug}`}
            className={`group inline-flex items-center gap-2 rounded-lg font-medium text-white transition-all duration-200 ${cat.color} ${cat.hoverColor} ${
              isCompact ? 'px-3 py-2 text-sm' : 'px-4 py-2.5'
            }`}
          >
            <Icon className={`transition-transform duration-200 group-hover:scale-110 ${isCompact ? 'h-4 w-4' : 'h-5 w-5'}`} />
            <span>{cat.name}</span>
          </Link>
        );
      })}
    </div>
  );
}
