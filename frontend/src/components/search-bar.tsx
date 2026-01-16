'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search } from 'lucide-react';

const CATEGORIES = [
  { value: 'all', label: 'All Categories' },
  { value: 'employment', label: 'Employment' },
  { value: 'training', label: 'Training' },
  { value: 'housing', label: 'Housing' },
  { value: 'legal', label: 'Legal' },
];

const STATES = [
  { value: 'all', label: 'All States' },
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AS', label: 'American Samoa' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DC', label: 'District of Columbia' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'GU', label: 'Guam' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MP', label: 'Northern Mariana Islands' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'PR', label: 'Puerto Rico' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VI', label: 'U.S. Virgin Islands' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' },
];

interface SearchBarProps {
  initialQuery?: string;
  initialCategory?: string;
  initialState?: string;
  onSearch?: (query: string, category: string, state: string) => void;
  variant?: 'default' | 'hero';
}

export function SearchBar({
  initialQuery = '',
  initialCategory = 'all',
  initialState = 'all',
  onSearch,
  variant = 'hero',
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState(initialCategory);
  const [state, setState] = useState(initialState);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (onSearch) {
      onSearch(query, category, state);
    } else {
      const params = new URLSearchParams();
      if (query) params.set('q', query);
      if (category && category !== 'all') params.set('category', category);
      if (state && state !== 'all') params.set('state', state);

      router.push(`/search?${params.toString()}`);
    }
  };

  const isHero = variant === 'hero';

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      {/* Main search input */}
      <div className="relative">
        <div className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2">
          <Search className={`h-5 w-5 ${isHero ? 'text-[hsl(var(--v4v-navy)/0.4)]' : 'text-muted-foreground'}`} />
        </div>
        <Input
          type="text"
          placeholder="Search for resources..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className={`w-full rounded-lg py-6 pl-12 pr-28 text-base shadow-sm transition-all ${
            isHero
              ? 'border-[hsl(var(--v4v-navy)/0.1)] bg-transparent text-[hsl(var(--v4v-navy))] placeholder:text-[hsl(var(--v4v-navy)/0.5)] focus:border-[hsl(var(--v4v-gold))] focus:bg-[hsl(var(--v4v-navy)/0.02)]'
              : 'border-input bg-background'
          }`}
        />
        <Button
          type="submit"
          className={`absolute right-2 top-1/2 -translate-y-1/2 rounded-md px-5 font-semibold transition-all ${
            isHero
              ? 'bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-gold-light))]'
              : ''
          }`}
        >
          Search
        </Button>
      </div>

      {/* Filters row */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger
            className={`w-full sm:w-[160px] min-h-[44px] transition-all ${
              isHero
                ? 'border-[hsl(var(--v4v-navy)/0.15)] bg-[hsl(var(--v4v-navy)/0.05)] text-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.08)] [&>svg]:text-[hsl(var(--v4v-navy)/0.5)]'
                : ''
            }`}
          >
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent
            position="popper"
            className="bg-white text-[hsl(var(--v4v-navy))] border border-[hsl(var(--border))]"
          >
            {CATEGORIES.map((cat) => (
              <SelectItem key={cat.value} value={cat.value}>
                {cat.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={state} onValueChange={setState}>
          <SelectTrigger
            className={`w-full sm:w-[160px] min-h-[44px] transition-all ${
              isHero
                ? 'border-[hsl(var(--v4v-navy)/0.15)] bg-[hsl(var(--v4v-navy)/0.05)] text-[hsl(var(--v4v-navy))] hover:bg-[hsl(var(--v4v-navy)/0.08)] [&>svg]:text-[hsl(var(--v4v-navy)/0.5)]'
                : ''
            }`}
          >
            <SelectValue placeholder="State" />
          </SelectTrigger>
          <SelectContent
            position="popper"
            className="bg-white text-[hsl(var(--v4v-navy))] border border-[hsl(var(--border))] max-h-[300px]"
          >
            {STATES.map((st) => (
              <SelectItem key={st.value} value={st.value}>
                {st.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </form>
  );
}
