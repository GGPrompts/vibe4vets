'use client';

import { cn } from '@/lib/utils';
import { Clock, ArrowDownAZ, Shuffle, MapPin } from 'lucide-react';
import { Input } from '@/components/ui/input';
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
  zipCode?: string;
  onZipChange?: (zip: string) => void;
  className?: string;
}

export function SortChips({
  selectedSort,
  onSortChange,
  zipCode = '',
  onZipChange,
  className,
}: SortChipsProps) {
  const isDistanceSelected = selectedSort === 'distance';
  const hasValidZip = zipCode.length === 5;

  const handleZipChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 5);
    onZipChange?.(value);
  };

  const handleDistanceClick = () => {
    onSortChange('distance');
  };

  return (
    <div className={cn('flex flex-col items-center gap-3', className)}>
      <span className="text-sm text-muted-foreground">Sort by:</span>
      <div className="flex flex-wrap items-center justify-center gap-2">
        {/* Distance chip with inline zip input */}
        <div
          className={cn(
            'inline-flex items-center gap-1.5 rounded-full transition-all duration-200',
            isDistanceSelected
              ? 'bg-[hsl(var(--v4v-navy))] text-white shadow-sm'
              : 'bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground'
          )}
        >
          <button
            type="button"
            onClick={handleDistanceClick}
            className={cn(
              'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full',
              'text-sm font-medium transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[hsl(var(--v4v-gold)/0.5)]'
            )}
          >
            <MapPin className="w-4 h-4" />
            <span>Distance</span>
          </button>
          {isDistanceSelected && (
            <div className="flex items-center pr-1.5">
              <Input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                value={zipCode}
                onChange={handleZipChange}
                placeholder="ZIP"
                className={cn(
                  'h-7 w-20 rounded-full border-0 bg-white/20 px-2 text-center text-sm',
                  'placeholder:text-white/50 focus:bg-white/30 focus:ring-1 focus:ring-white/50',
                  hasValidZip && 'bg-[hsl(var(--v4v-gold)/0.3)] text-white font-medium'
                )}
                autoFocus
              />
            </div>
          )}
        </div>

        {/* Other sort options */}
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
      {isDistanceSelected && !hasValidZip && (
        <p className="text-xs text-muted-foreground">
          Enter your 5-digit ZIP code to sort by distance
        </p>
      )}
      {isDistanceSelected && hasValidZip && (
        <p className="text-xs text-[hsl(var(--v4v-gold-dark))] font-medium">
          Results will show closest to {zipCode} first
        </p>
      )}
    </div>
  );
}
