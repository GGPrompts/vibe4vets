'use client';

import { Badge } from '@/components/ui/badge';
import {
  MapPin,
  Calendar,
  DollarSign,
  Home,
  Briefcase,
  GraduationCap,
  Scale,
  Clock,
  Shield,
  UtensilsCrossed,
  CalendarDays,
  Leaf,
  FileCheck,
  Users,
  BadgeCheck,
  Video,
  Coins,
  Brain,
  HeartHandshake,
  HeartPulse,
  School,
  Wallet,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MatchReason {
  type: string;
  label: string;
}

// Color and icon mapping for match reason types
const matchReasonStyles: Record<
  string,
  { bgClass: string; textClass: string; icon: React.ElementType }
> = {
  location: {
    bgClass: 'bg-blue-100 dark:bg-blue-900/40',
    textClass: 'text-blue-800 dark:text-blue-300',
    icon: MapPin,
  },
  age: {
    bgClass: 'bg-purple-100 dark:bg-purple-900/40',
    textClass: 'text-purple-800 dark:text-purple-300',
    icon: Calendar,
  },
  income: {
    bgClass: 'bg-emerald-100 dark:bg-emerald-900/40',
    textClass: 'text-emerald-800 dark:text-emerald-300',
    icon: DollarSign,
  },
  housing_status: {
    bgClass: 'bg-amber-100 dark:bg-amber-900/40',
    textClass: 'text-amber-800 dark:text-amber-300',
    icon: Home,
  },
  category: {
    bgClass: 'bg-slate-100 dark:bg-slate-800',
    textClass: 'text-slate-800 dark:text-slate-300',
    icon: Briefcase,
  },
  veteran_status: {
    bgClass: 'bg-red-100 dark:bg-red-900/40',
    textClass: 'text-red-800 dark:text-red-300',
    icon: Shield,
  },
  discharge: {
    bgClass: 'bg-orange-100 dark:bg-orange-900/40',
    textClass: 'text-orange-800 dark:text-orange-300',
    icon: Shield,
  },
  availability: {
    bgClass: 'bg-green-100 dark:bg-green-900/40',
    textClass: 'text-green-800 dark:text-green-300',
    icon: Clock,
  },
  schedule: {
    bgClass: 'bg-cyan-100 dark:bg-cyan-900/40',
    textClass: 'text-cyan-800 dark:text-cyan-300',
    icon: CalendarDays,
  },
  dietary: {
    bgClass: 'bg-lime-100 dark:bg-lime-900/40',
    textClass: 'text-lime-800 dark:text-lime-300',
    icon: Leaf,
  },
  access: {
    bgClass: 'bg-violet-100 dark:bg-violet-900/40',
    textClass: 'text-violet-800 dark:text-violet-300',
    icon: Video,
  },
  benefits: {
    bgClass: 'bg-indigo-100 dark:bg-indigo-900/40',
    textClass: 'text-indigo-800 dark:text-indigo-300',
    icon: FileCheck,
  },
  representative: {
    bgClass: 'bg-teal-100 dark:bg-teal-900/40',
    textClass: 'text-teal-800 dark:text-teal-300',
    icon: Users,
  },
  accredited: {
    bgClass: 'bg-sky-100 dark:bg-sky-900/40',
    textClass: 'text-sky-800 dark:text-sky-300',
    icon: BadgeCheck,
  },
  cost: {
    bgClass: 'bg-rose-100 dark:bg-rose-900/40',
    textClass: 'text-rose-800 dark:text-rose-300',
    icon: Coins,
  },
};

// Category-specific icons
const categoryIcons: Record<string, React.ElementType> = {
  'Housing assistance': Home,
  'Employment services': Briefcase,
  'Training program': GraduationCap,
  'Legal services': Scale,
  'Food assistance': UtensilsCrossed,
  'Benefits consultation': FileCheck,
  'Mental health': Brain,
  'Support services': HeartHandshake,
  'Healthcare': HeartPulse,
  'Education': School,
  'Financial': Wallet,
};

interface MatchReasonChipsProps {
  reasons: MatchReason[];
  className?: string;
  maxVisible?: number;
}

export function MatchReasonChips({
  reasons,
  className,
  maxVisible = 5,
}: MatchReasonChipsProps) {
  if (!reasons || reasons.length === 0) {
    return null;
  }

  const visibleReasons = reasons.slice(0, maxVisible);
  const hiddenCount = reasons.length - maxVisible;

  return (
    <div className={cn('flex flex-wrap gap-1.5', className)}>
      {visibleReasons.map((reason, index) => {
        const style = matchReasonStyles[reason.type] || {
          bgClass: 'bg-gray-100 dark:bg-gray-800',
          textClass: 'text-gray-800 dark:text-gray-300',
          icon: Shield,
        };

        // Use category-specific icon if available
        const Icon =
          reason.type === 'category'
            ? categoryIcons[reason.label] || style.icon
            : style.icon;

        return (
          <Badge
            key={`${reason.type}-${index}`}
            variant="secondary"
            className={cn(
              'flex items-center gap-1 px-2 py-0.5 text-xs font-normal',
              style.bgClass,
              style.textClass
            )}
          >
            <Icon className="h-3 w-3" />
            {reason.label}
          </Badge>
        );
      })}
      {hiddenCount > 0 && (
        <Badge
          variant="outline"
          className="px-2 py-0.5 text-xs font-normal text-muted-foreground"
        >
          +{hiddenCount} more
        </Badge>
      )}
    </div>
  );
}

export default MatchReasonChips;
