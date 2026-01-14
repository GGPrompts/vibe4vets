'use client';

import { useEffect } from 'react';

/**
 * Prevents Radix UI scroll lock from adding padding to body
 * by observing and resetting the style attribute
 */
export function ScrollLockFix() {
  useEffect(() => {
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
          const body = document.body;
          if (body.style.paddingRight || body.style.marginRight) {
            body.style.paddingRight = '';
            body.style.marginRight = '';
            body.style.overflow = '';
          }
        }
      }
    });

    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['style'],
    });

    return () => observer.disconnect();
  }, []);

  return null;
}
