'use client';

import { ArrowUpDown } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

export type SortOption = 'official' | 'relevance' | 'newest' | 'alpha' | 'shuffle' | 'distance';

export const SORT_OPTIONS = [
  { value: 'official', label: 'Official First' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'distance', label: 'Distance' },
  { value: 'newest', label: 'Newest' },
  { value: 'alpha', label: 'A-Z' },
  { value: 'shuffle', label: 'Shuffle' },
] as const;

interface SortDropdownProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
  hasQuery?: boolean;
  className?: string;
}

export function SortDropdown({
  value,
  onChange,
  hasQuery = false,
  className,
}: SortDropdownProps) {
  // Filter options based on context:
  // - 'relevance' only shown when there's a search query
  // - 'official' always shown (sorts by source tier)
  // - 'distance' handled by parent component
  const options = SORT_OPTIONS.filter((opt) => {
    if (opt.value === 'relevance') return hasQuery;
    return true;
  });

  return (
    <Select value={value} onValueChange={(v) => onChange(v as SortOption)}>
      <SelectTrigger
        className={cn(
          'h-9 w-[130px] gap-1 text-sm',
          className
        )}
      >
        <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground" />
        <SelectValue placeholder="Sort by" />
      </SelectTrigger>
      <SelectContent align="end">
        {options.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
