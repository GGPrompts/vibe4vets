'use client';

import { useState, useEffect } from 'react';
import { ZoomIn } from 'lucide-react';
import { useOptionalMagnifier } from '@/context/magnifier-context';
import { cn } from '@/lib/utils';

export function MagnifierToggle() {
  const magnifierContext = useOptionalMagnifier();
  const [isMounted, setIsMounted] = useState(false);
  const [isMobile, setIsMobile] = useState(true);

  useEffect(() => {
    setIsMounted(true);
    const checkMobile = () => {
      setIsMobile(window.matchMedia('(pointer: coarse)').matches);
    };
    checkMobile();
    const mediaQuery = window.matchMedia('(pointer: coarse)');
    mediaQuery.addEventListener('change', checkMobile);
    return () => mediaQuery.removeEventListener('change', checkMobile);
  }, []);

  // Don't render on mobile or before hydration
  if (!isMounted || isMobile || !magnifierContext?.isHydrated) {
    return null;
  }

  const { enabled, toggleEnabled } = magnifierContext;

  return (
    <button
      type="button"
      onClick={toggleEnabled}
      aria-pressed={enabled}
      aria-label={enabled ? 'Disable magnifier' : 'Enable magnifier'}
      title={enabled ? 'Disable magnifier (Alt+M)' : 'Enable magnifier (Alt+M)'}
      className={cn(
        'hidden md:flex items-center justify-center w-9 h-9 rounded-full transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-[hsl(var(--v4v-gold))] focus:ring-offset-2 focus:ring-offset-[hsl(var(--v4v-navy))]',
        enabled
          ? 'bg-[hsl(var(--v4v-gold))] text-[hsl(var(--v4v-navy))]'
          : 'bg-white/10 text-white/80 hover:bg-white/20 hover:text-[hsl(var(--v4v-gold))]'
      )}
    >
      <ZoomIn className="h-5 w-5" />
    </button>
  );
}
