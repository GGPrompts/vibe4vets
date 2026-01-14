'use client';

import { useEffect, useState } from 'react';

const SCROLL_THRESHOLD = 50;

interface ScrollDirectionState {
  scrollDirection: 'up' | 'down' | null;
  scrollY: number;
  isAtTop: boolean;
}

export function useScrollDirection(): ScrollDirectionState {
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down' | null>(null);
  const [scrollY, setScrollY] = useState(0);
  const [isAtTop, setIsAtTop] = useState(true);

  useEffect(() => {
    let lastScrollY = window.scrollY;
    let ticking = false;

    const updateScrollDirection = () => {
      const currentScrollY = window.scrollY;

      setScrollY(currentScrollY);
      setIsAtTop(currentScrollY < SCROLL_THRESHOLD);

      // Only update direction after passing threshold
      if (Math.abs(currentScrollY - lastScrollY) < 10) {
        ticking = false;
        return;
      }

      if (currentScrollY > lastScrollY && currentScrollY > SCROLL_THRESHOLD) {
        setScrollDirection('down');
      } else if (currentScrollY < lastScrollY) {
        setScrollDirection('up');
      }

      lastScrollY = currentScrollY;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(updateScrollDirection);
        ticking = true;
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });

    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return { scrollDirection, scrollY, isAtTop };
}
