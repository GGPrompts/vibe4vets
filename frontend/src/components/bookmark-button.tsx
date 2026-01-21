'use client';

import { Bookmark } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useSavedResources } from '@/context/saved-resources-context';
import { useAnalytics } from '@/lib/useAnalytics';
import { cn } from '@/lib/utils';

interface BookmarkButtonProps {
  resourceId: string;
  className?: string;
  size?: 'default' | 'sm' | 'lg';
  showTooltip?: boolean;
  variant?: 'default' | 'gold';
}

export function BookmarkButton({
  resourceId,
  className,
  size = 'default',
  showTooltip = true,
  variant = 'default',
}: BookmarkButtonProps) {
  const { isSaved, toggleSaved } = useSavedResources();
  const { trackResourceSave } = useAnalytics();
  const saved = isSaved(resourceId);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const newState = !saved;
    toggleSaved(resourceId);
    trackResourceSave(resourceId, newState ? 'save' : 'unsave');
  };

  // Size mappings
  const sizeClasses = {
    default: 'h-8 w-8',
    sm: 'h-6 w-6',
    lg: 'h-10 w-10',
  };

  const iconSizes = {
    default: 'h-4 w-4',
    sm: 'h-3.5 w-3.5',
    lg: 'h-5 w-5',
  };

  // Color scheme based on variant
  const colorClasses = variant === 'gold'
    ? saved
      ? 'text-[hsl(var(--v4v-gold))] hover:text-[hsl(var(--v4v-gold-dark))] hover:bg-[hsl(var(--v4v-gold)/0.1)]'
      : 'text-gray-500 hover:text-[hsl(var(--v4v-gold))] hover:bg-[hsl(var(--v4v-gold)/0.1)]'
    : saved
      ? 'text-red-500 hover:text-red-600 hover:bg-red-50'
      : 'text-gray-500 hover:text-red-500 hover:bg-red-50';

  const button = (
    <Button
      variant="ghost"
      size="icon"
      type="button"
      onClick={handleClick}
      className={cn(
        sizeClasses[size],
        'shrink-0 rounded-full transition-colors duration-200 bg-white/80 border border-gray-300 shadow-sm',
        colorClasses,
        className
      )}
      aria-label={saved ? 'Remove from saved' : 'Save to this device'}
    >
      <Bookmark
        className={cn(
          iconSizes[size],
          saved && 'fill-current'
        )}
      />
    </Button>
  );

  if (!showTooltip) {
    return button;
  }

  return (
    <TooltipProvider delayDuration={300}>
      <Tooltip>
        <TooltipTrigger asChild>{button}</TooltipTrigger>
        <TooltipContent side="top" className="text-xs">
          {saved ? 'Saved to this device' : 'Save to this device'}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
