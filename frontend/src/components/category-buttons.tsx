'use client';

import Link from 'next/link';
import { Briefcase, GraduationCap, Home, Scale } from 'lucide-react';

const categories = [
  {
    name: 'Employment',
    slug: 'employment',
    icon: Briefcase,
    color: 'bg-[hsl(210,70%,45%)]',
    hoverColor: 'hover:bg-[hsl(210,70%,40%)]',
  },
  {
    name: 'Training',
    slug: 'training',
    icon: GraduationCap,
    color: 'bg-[hsl(160,50%,40%)]',
    hoverColor: 'hover:bg-[hsl(160,50%,35%)]',
  },
  {
    name: 'Housing',
    slug: 'housing',
    icon: Home,
    color: 'bg-[hsl(25,70%,50%)]',
    hoverColor: 'hover:bg-[hsl(25,70%,45%)]',
  },
  {
    name: 'Legal',
    slug: 'legal',
    icon: Scale,
    color: 'bg-[hsl(280,40%,45%)]',
    hoverColor: 'hover:bg-[hsl(280,40%,40%)]',
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
