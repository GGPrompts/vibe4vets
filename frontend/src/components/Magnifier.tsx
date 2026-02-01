'use client';

import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { usePathname, useSearchParams } from 'next/navigation';
import { useOptionalMagnifier } from '@/context/magnifier-context';
import DOMPurify from 'dompurify';

const MAGNIFIER_WIDTH = 600;
const MAGNIFIER_HEIGHT = 350;

export function Magnifier() {
  const magnifierContext = useOptionalMagnifier();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [mounted, setMounted] = useState(false);
  const [isMobile, setIsMobile] = useState(true);
  const [pos, setPos] = useState({ x: -1000, y: -1000, scrollY: 0 });

  const enabled = magnifierContext?.enabled ?? false;
  const isHydrated = magnifierContext?.isHydrated ?? false;
  const zoomLevel = magnifierContext?.zoomLevel ?? 2;
  const suppressed = magnifierContext?.suppressed ?? false;

  // Hide on resource detail pages or when resource modal is open
  const isResourceDetailPage = pathname?.startsWith('/resources/');
  const isResourceModalOpen = searchParams?.has('resource');

  const toggleEnabled = magnifierContext?.toggleEnabled;

  // Initialize
  useEffect(() => {
    setMounted(true);
    const isCoarse = window.matchMedia('(pointer: coarse)').matches;
    setIsMobile(isCoarse);

    const mediaQuery = window.matchMedia('(pointer: coarse)');
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  // Hotkey: Alt+M to toggle magnifier
  useEffect(() => {
    if (!mounted || isMobile) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key.toLowerCase() === 'm') {
        e.preventDefault();
        toggleEnabled?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [mounted, isMobile, toggleEnabled]);

  // Right-click to close magnifier when it's open
  useEffect(() => {
    if (!mounted || !enabled || isMobile) return;

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
      toggleEnabled?.();
    };

    document.addEventListener('contextmenu', handleContextMenu);
    return () => document.removeEventListener('contextmenu', handleContextMenu);
  }, [mounted, enabled, isMobile, toggleEnabled]);

  // Track mouse and scroll
  useEffect(() => {
    if (!mounted || !enabled || isMobile) return;

    let rafId: number;
    let currentX = -1000;
    let currentY = -1000;
    let currentScrollY = window.scrollY;

    const update = () => {
      setPos({ x: currentX, y: currentY, scrollY: currentScrollY });
      rafId = requestAnimationFrame(update);
    };

    const handleMouseMove = (e: MouseEvent) => {
      currentX = e.clientX;
      currentY = e.clientY;
    };

    const handleScroll = () => {
      currentScrollY = window.scrollY;
    };

    const handleMouseLeave = () => {
      currentX = -1000;
      currentY = -1000;
    };

    document.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('scroll', handleScroll, { passive: true });
    rafId = requestAnimationFrame(update);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('scroll', handleScroll);
      cancelAnimationFrame(rafId);
    };
  }, [mounted, enabled, isMobile]);

  if (!mounted || !enabled || !isHydrated || isMobile || isResourceDetailPage || isResourceModalOpen || suppressed || pos.x < 0) {
    return null;
  }

  // Calculate magnifier position (centered on cursor, clamped to viewport)
  const halfW = MAGNIFIER_WIDTH / 2;
  const halfH = MAGNIFIER_HEIGHT / 2;
  const left = Math.max(0, Math.min(window.innerWidth - MAGNIFIER_WIDTH, pos.x - halfW));
  const top = Math.max(0, Math.min(window.innerHeight - MAGNIFIER_HEIGHT, pos.y - halfH));

  // The background position to show magnified area centered on cursor
  // We use the page as background and position it so cursor point is at center
  const bgX = -pos.x * zoomLevel + halfW;
  const bgY = -(pos.y + pos.scrollY) * zoomLevel + halfH;

  const magnifierElement = (
    <div
      data-magnifier
      aria-hidden="true"
      style={{
        position: 'fixed',
        left: `${left}px`,
        top: `${top}px`,
        width: `${MAGNIFIER_WIDTH}px`,
        height: `${MAGNIFIER_HEIGHT}px`,
        zIndex: 9999,
        pointerEvents: 'none',
        overflow: 'hidden',
        border: '3px solid hsl(var(--v4v-gold))',
        borderRadius: '8px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        background: 'white',
      }}
    >
      {/* Scaled clone of page content */}
      <MagnifierContent
        zoomLevel={zoomLevel}
        offsetX={bgX}
        offsetY={bgY}
      />
      {/* Crosshair */}
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          width: '20px',
          height: '20px',
          marginLeft: '-10px',
          marginTop: '-10px',
          border: '2px solid hsl(var(--v4v-gold))',
          borderRadius: '50%',
          pointerEvents: 'none',
          opacity: 0.8,
          boxShadow: '0 0 0 1px rgba(0,0,0,0.2)',
        }}
      />
    </div>
  );

  return createPortal(magnifierElement, document.body);
}

// Separate component to render cloned content
function MagnifierContent({
  zoomLevel,
  offsetX,
  offsetY
}: {
  zoomLevel: number;
  offsetX: number;
  offsetY: number;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [html, setHtml] = useState('');

  // Capture page HTML periodically
  useEffect(() => {
    const capture = () => {
      // Get body content excluding the magnifier
      const clone = document.body.cloneNode(true) as HTMLElement;
      const magnifier = clone.querySelector('[data-magnifier]');
      if (magnifier) magnifier.remove();

      setHtml(clone.innerHTML);
    };

    capture();
    const intervalId = setInterval(capture, 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        position: 'absolute',
        left: `${offsetX}px`,
        top: `${offsetY}px`,
        width: `${document.documentElement.scrollWidth}px`,
        height: `${document.documentElement.scrollHeight}px`,
        transform: `scale(${zoomLevel})`,
        transformOrigin: 'top left',
        pointerEvents: 'none',
        overflow: 'visible',
      }}
      className={document.body.className}
      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }}
    />
  );
}
