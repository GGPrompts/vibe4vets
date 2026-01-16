'use client';

import { Suspense, useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Compass } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DiscoveryFeed } from '@/components/DiscoveryFeed';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

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

function FeedFallback() {
  return (
    <div className="space-y-8">
      <div>
        <Skeleton className="mb-4 h-8 w-48" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg" />
          ))}
        </div>
      </div>
      <div>
        <Skeleton className="mb-4 h-8 w-48" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg" />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function DiscoverPage() {
  const router = useRouter();

  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('all');
  const [state, setState] = useState('all');

  const handleCategoryChange = useCallback((value: string) => {
    setCategory(value);
  }, []);

  const handleStateChange = useCallback((value: string) => {
    setState(value);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();

    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (category && category !== 'all') params.set('category', category);
    if (state && state !== 'all') params.set('state', state);

    router.push(`/search?${params.toString()}`);
  };

  return (
    <main className="min-h-screen bg-[hsl(var(--v4v-cream))] pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[hsl(var(--v4v-navy))] text-white">
        <div className="absolute right-0 top-0 h-full w-1/3 opacity-10">
          <div className="h-full w-full bg-gradient-to-l from-[hsl(var(--v4v-gold))] to-transparent" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6 py-16 lg:py-20">
          <Link
            href="/"
            className="mb-6 inline-flex items-center gap-2 text-sm text-white/70 transition-colors hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>

          <div className="flex items-center gap-4">
            <div className="rounded-xl bg-[hsl(var(--v4v-gold)/0.2)] p-4">
              <Compass className="h-12 w-12 text-[hsl(var(--v4v-gold))]" />
            </div>
            <div>
              <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl">
                Explore Resources
              </h1>
              <p className="mt-2 text-lg text-white/80">
                Browse veteran resources by category and location
              </p>
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[hsl(var(--v4v-gold))] to-transparent opacity-50" />
      </section>

      {/* Filters Section */}
      <section className="border-b border-[hsl(var(--border))] bg-white py-4">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <form
            onSubmit={handleSearch}
            className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:gap-4"
          >
            <div className="relative w-full sm:max-w-md">
              <Input
                type="text"
                placeholder="Search resources..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="h-11 w-full pr-24"
              />
              <Button type="submit" className="absolute right-1.5 top-1/2 -translate-y-1/2">
                Search
              </Button>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:gap-4">
              <Select value={category} onValueChange={handleCategoryChange}>
                <SelectTrigger className="w-full min-h-[44px] sm:w-[160px]">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent
                  position="popper"
                  className="border border-[hsl(var(--border))] bg-white text-[hsl(var(--v4v-navy))]"
                >
                  {CATEGORIES.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={state} onValueChange={handleStateChange}>
                <SelectTrigger className="w-full min-h-[44px] sm:w-[160px]">
                  <SelectValue placeholder="State" />
                </SelectTrigger>
                <SelectContent
                  position="popper"
                  className="max-h-[300px] border border-[hsl(var(--border))] bg-white text-[hsl(var(--v4v-navy))]"
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
        </div>
      </section>

      {/* Discovery Feed */}
      <section className="py-12 lg:py-16">
        <div className="mx-auto max-w-6xl px-6">
          <Suspense fallback={<FeedFallback />}>
            <DiscoveryFeed
              category={category !== 'all' ? category : undefined}
              state={state !== 'all' ? state : undefined}
            />
          </Suspense>
        </div>
      </section>
    </main>
  );
}
