'use client';

import { cn } from '@/lib/utils';
import { Clock, ArrowDownAZ, Shuffle } from 'lucide-react';
import type { SortOption } from '@/components/sort-dropdown-header';

interface SortChipItem {
  value: SortOption;
  label: string;
  icon: React.ReactNode;
}

const SORT_CHIP_ITEMS: SortChipItem[] = [
  {
    value: 'shuffle',
    label: 'Shuffle',
    icon: <Shuffle className="w-4 h-4" />,
  },
  {
    value: 'newest',
    label: 'Newest',
    icon: <Clock className="w-4 h-4" />,
  },
  {
    value: 'alpha',
    label: 'A-Z',
    icon: <ArrowDownAZ className="w-4 h-4" />,
  },
];

interface SortChipsProps {
  selectedSort: SortOption;
  onSortChange: (sort: SortOption) => void;
  className?: string;
}

export function SortChips({
  selectedSort,
  onSortChange,
  className,
}: SortChipsProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className="text-sm text-muted-foreground mr-1">Sort by:</span>
      <div className="flex items-center gap-2">
        {SORT_CHIP_ITEMS.map((item) => {
          const isSelected = item.value === selectedSort;
          return (
            <button
              key={item.value}
              type="button"
              onClick={() => onSortChange(item.value)}
              className={cn(
                'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full',
                'text-sm font-medium transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[hsl(var(--v4v-gold)/0.5)]',
                isSelected
                  ? 'bg-[hsl(var(--v4v-navy))] text-white shadow-sm'
                  : 'bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
