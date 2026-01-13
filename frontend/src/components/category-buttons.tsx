'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';

const categories = [
  { name: 'Employment', icon: '💼', slug: 'employment' },
  { name: 'Training', icon: '📚', slug: 'training' },
  { name: 'Housing', icon: '🏠', slug: 'housing' },
  { name: 'Legal', icon: '⚖️', slug: 'legal' },
];

export function CategoryButtons() {
  return (
    <div className="flex flex-wrap justify-center gap-4">
      {categories.map((cat) => (
        <Link key={cat.slug} href={`/search?category=${cat.slug}`}>
          <Button
            variant="outline"
            className="flex items-center gap-2 px-4 py-2"
          >
            <span>{cat.icon}</span>
            <span>{cat.name}</span>
          </Button>
        </Link>
      ))}
    </div>
  );
}
