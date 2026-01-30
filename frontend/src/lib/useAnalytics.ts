'use client';

/**
 * Analytics hook for privacy-respecting usage tracking.
 *
 * All data is anonymous - no PII, no user identifiers, no IP addresses.
 * Events are sent to the backend where they are stored without any
 * personally identifiable information.
 */

import { useCallback, useRef } from 'react';
import { usePathname } from 'next/navigation';
import api, { AnalyticsEventType } from './api';

interface TrackOptions {
  category?: string;
  state?: string;
  resourceId?: string;
  searchQuery?: string;
  wizardStep?: number;
}

export function useAnalytics() {
  const pathname = usePathname();
  // Prevent duplicate events within short time windows
  const lastEvent = useRef<{ type: string; timestamp: number }>({
    type: '',
    timestamp: 0,
  });

  const track = useCallback(
    async (
      eventType: AnalyticsEventType,
      eventName: string,
      options: TrackOptions = {}
    ) => {
      // Debounce duplicate events (within 500ms)
      const now = Date.now();
      const key = `${eventType}:${eventName}:${options.resourceId || ''}`;
      if (
        lastEvent.current.type === key &&
        now - lastEvent.current.timestamp < 500
      ) {
        return;
      }
      lastEvent.current = { type: key, timestamp: now };

      try {
        await api.analytics.trackEvent({
          event_type: eventType,
          event_name: eventName,
          category: options.category,
          state: options.state,
          resource_id: options.resourceId,
          search_query: options.searchQuery,
          wizard_step: options.wizardStep,
          page_path: pathname,
        });
      } catch (error) {
        // Log to console.warn so it's visible without enabling verbose mode
        console.warn('[Analytics] Event tracking failed:', eventType, error);
      }
    },
    [pathname]
  );

  // Convenience methods for common events
  const trackSearch = useCallback(
    (query: string, category?: string, state?: string) => {
      return track('search', 'search', { searchQuery: query, category, state });
    },
    [track]
  );

  const trackFilter = useCallback(
    (category?: string, state?: string) => {
      return track('search_filter', 'filter', { category, state });
    },
    [track]
  );

  const trackResourceView = useCallback(
    (resourceId: string, category?: string, state?: string) => {
      return track('resource_view', 'resource_view', {
        resourceId,
        category,
        state,
      });
    },
    [track]
  );

  const trackWizardStart = useCallback(() => {
    return track('wizard_start', 'wizard_start');
  }, [track]);

  const trackWizardStep = useCallback(
    (step: number) => {
      return track('wizard_step', 'wizard_step', { wizardStep: step });
    },
    [track]
  );

  const trackWizardComplete = useCallback(() => {
    return track('wizard_complete', 'wizard_complete');
  }, [track]);

  const trackChatStart = useCallback(() => {
    return track('chat_start', 'chat_start');
  }, [track]);

  const trackChatMessage = useCallback(() => {
    return track('chat_message', 'chat_message');
  }, [track]);

  const trackPageView = useCallback(
    (category?: string, state?: string) => {
      return track('page_view', 'page_view', { category, state });
    },
    [track]
  );

  // Save/Export tracking - using page_view type to avoid backend schema changes
  const trackResourceSave = useCallback(
    (resourceId: string, action: 'save' | 'unsave') => {
      return track('page_view', `resource_${action}`, { resourceId });
    },
    [track]
  );

  const trackExport = useCallback(
    (format: 'excel' | 'pdf' | 'email', resourceCount: number) => {
      return track('page_view', `export_${format}`, {
        searchQuery: `${resourceCount} resources`,
      });
    },
    [track]
  );

  return {
    track,
    trackSearch,
    trackFilter,
    trackResourceView,
    trackWizardStart,
    trackWizardStep,
    trackWizardComplete,
    trackChatStart,
    trackChatMessage,
    trackPageView,
    trackResourceSave,
    trackExport,
  };
}
