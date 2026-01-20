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

export type SortOption = 'relevance' | 'newest' | 'alpha' | 'shuffle';

export const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
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
  // Filter out relevance option when there's no search query
  const options = hasQuery
    ? SORT_OPTIONS
    : SORT_OPTIONS.filter((opt) => opt.value !== 'relevance');

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
