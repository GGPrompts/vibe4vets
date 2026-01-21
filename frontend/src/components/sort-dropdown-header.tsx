"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ArrowUpDown, Clock, ArrowDownAZ, Sparkles, Shuffle, Check } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export type SortOption = 'relevance' | 'newest' | 'alpha' | 'shuffle';

interface SortItem {
  value: SortOption;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const SORT_ITEMS: SortItem[] = [
  {
    value: 'relevance',
    label: 'Relevance',
    description: 'Best matches first',
    icon: <Sparkles className="w-4 h-4" />,
  },
  {
    value: 'newest',
    label: 'Newest',
    description: 'Recently added',
    icon: <Clock className="w-4 h-4" />,
  },
  {
    value: 'alpha',
    label: 'A-Z',
    description: 'Alphabetical order',
    icon: <ArrowDownAZ className="w-4 h-4" />,
  },
  {
    value: 'shuffle',
    label: 'Shuffle',
    description: 'Randomized order',
    icon: <Shuffle className="w-4 h-4" />,
  },
];

interface SortDropdownHeaderProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
  hasQuery?: boolean;
  className?: string;
}

export function SortDropdownHeader({
  value,
  onChange,
  hasQuery = false,
  className,
}: SortDropdownHeaderProps) {
  // Filter out relevance when there's no search query
  const items = hasQuery
    ? SORT_ITEMS
    : SORT_ITEMS.filter((item) => item.value !== 'relevance');

  const currentItem = SORT_ITEMS.find((item) => item.value === value) || SORT_ITEMS[1];

  return (
    <div className={cn("relative", className)}>
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-full",
              "text-sm font-medium transition-all duration-200",
              "text-white/70 hover:text-[hsl(var(--v4v-gold))]",
              "hover:bg-white/10",
              "border border-white/20",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--v4v-gold)/0.3)]"
            )}
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Sort:</span>
            <span>{currentItem.label}</span>
          </button>
        </DropdownMenuTrigger>

        <DropdownMenuContent
          align="end"
          sideOffset={4}
          className="w-56 p-2 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md border border-zinc-200/60 dark:border-zinc-800/60 rounded-xl shadow-xl shadow-zinc-900/10 dark:shadow-zinc-950/30"
        >
            <div className="space-y-1">
              {items.map((item) => {
                const isSelected = item.value === value;
                return (
                  <DropdownMenuItem
                    key={item.value}
                    onClick={() => onChange(item.value)}
                    className={cn(
                      "flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all duration-200",
                      "hover:bg-zinc-100/80 dark:hover:bg-zinc-800/60",
                      "focus:bg-zinc-100/80 dark:focus:bg-zinc-800/60",
                      isSelected && "bg-[hsl(var(--v4v-gold)/0.1)]"
                    )}
                  >
                    <div className={cn(
                      "flex items-center justify-center w-8 h-8 rounded-lg transition-colors",
                      isSelected
                        ? "bg-[hsl(var(--v4v-gold)/0.2)] text-[hsl(var(--v4v-gold))]"
                        : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400"
                    )}>
                      {item.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={cn(
                        "text-sm font-medium",
                        isSelected
                          ? "text-[hsl(var(--v4v-navy))] dark:text-white"
                          : "text-zinc-700 dark:text-zinc-200"
                      )}>
                        {item.label}
                      </div>
                      <div className="text-xs text-zinc-500 dark:text-zinc-400">
                        {item.description}
                      </div>
                    </div>
                    {isSelected && (
                      <Check className="w-4 h-4 text-[hsl(var(--v4v-gold))] flex-shrink-0" />
                    )}
                  </DropdownMenuItem>
                );
              })}
            </div>
          </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
