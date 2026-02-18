'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Search,
  Eye,
  MessageSquare,
  Filter,
  TrendingUp,
  Target,
  MapPin,
  FileText,
} from 'lucide-react';
import api, { type AnalyticsDashboardResponse } from '@/lib/api';

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState<AnalyticsDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const initialLoadDone = useRef(false);

  const fetchAnalytics = useCallback(async (daysParam: number, isInitialLoad = false) => {
    if (isInitialLoad) {
      setLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError(null);
    try {
      const data = await api.analytics.getDashboard(daysParam);
      setDashboard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (!initialLoadDone.current) {
      fetchAnalytics(days, true);
      initialLoadDone.current = true;
    } else {
      fetchAnalytics(days, false);
    }
  }, [days, fetchAnalytics]);

  const summary = dashboard?.summary;
  const popular_searches = dashboard?.popular_searches ?? [];
  const popular_categories = dashboard?.popular_categories ?? [];
  const popular_states = dashboard?.popular_states ?? [];
  const popular_resources = dashboard?.popular_resources ?? [];
  const wizard_funnel = dashboard?.wizard_funnel;

  // Show error state
  if (error && !dashboard) {
    return (
      <div className="p-6 lg:p-8">
        <div className="mx-auto max-w-6xl">
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <p className="text-destructive">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const showSkeleton = loading && !dashboard;
  const contentOpacity = isRefreshing ? 'opacity-60' : 'opacity-100';

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 mb-3">
            <div className="h-px w-8 bg-gradient-to-r from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
            <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]">Analytics</span>
            <div className="h-px w-8 bg-gradient-to-l from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
          </div>
          <h1 className="font-display text-3xl font-semibold text-foreground">Usage Analytics</h1>
          <p className="mt-1 text-muted-foreground">
            Privacy-respecting usage metrics (no PII collected)
          </p>
        </div>
        <Select value={String(days)} onValueChange={(v) => setDays(Number(v))}>
          <SelectTrigger className="w-40 bg-card border-border/50" aria-label="Select time period">
            <SelectValue placeholder="Time period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
            <SelectItem value="365">Last year</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Summary Stats */}
      <div className={`mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4 transition-opacity duration-150 ${contentOpacity}`}>
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Searches</CardTitle>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[hsl(var(--v4v-employment)/0.1)]">
              <Search className="h-4 w-4 text-[hsl(var(--v4v-employment))]" />
            </div>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold">{summary?.total_searches.toLocaleString() ?? 0}</div>
            )}
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Resource Views</CardTitle>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[hsl(var(--v4v-training)/0.1)]">
              <Eye className="h-4 w-4 text-[hsl(var(--v4v-training))]" />
            </div>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold">{summary?.total_resource_views.toLocaleString() ?? 0}</div>
            )}
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Chat Sessions</CardTitle>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[hsl(var(--v4v-housing)/0.1)]">
              <MessageSquare className="h-4 w-4 text-[hsl(var(--v4v-housing))]" />
            </div>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <>
                <Skeleton className="h-9 w-20" />
                <Skeleton className="mt-1 h-4 w-24" />
              </>
            ) : (
              <>
                <div className="text-3xl font-bold">{summary?.chat_sessions.toLocaleString() ?? 0}</div>
                <p className="text-xs text-muted-foreground">
                  {summary?.chat_messages.toLocaleString() ?? 0} messages
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Filter Usage</CardTitle>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[hsl(var(--v4v-legal)/0.1)]">
              <Filter className="h-4 w-4 text-[hsl(var(--v4v-legal))]" />
            </div>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold">{summary?.filter_usage.toLocaleString() ?? 0}</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Wizard Funnel */}
      <Card className={`mb-8 border-border/50 bg-card/80 backdrop-blur-sm transition-opacity duration-150 ${contentOpacity}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-display">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[hsl(var(--v4v-gold)/0.15)]">
              <Target className="h-5 w-5 text-[hsl(var(--v4v-gold-dark))]" />
            </div>
            Eligibility Wizard Funnel
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-8">
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">Started</p>
              {showSkeleton ? (
                <Skeleton className="h-9 w-16" />
              ) : (
                <p className="text-3xl font-bold">{wizard_funnel?.starts.toLocaleString() ?? 0}</p>
              )}
            </div>
            <TrendingUp className="h-6 w-6 text-[hsl(var(--v4v-gold))]" />
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">Completed</p>
              {showSkeleton ? (
                <Skeleton className="h-9 w-16" />
              ) : (
                <p className="text-3xl font-bold">{wizard_funnel?.completions.toLocaleString() ?? 0}</p>
              )}
            </div>
            <div className="ml-auto">
              {showSkeleton ? (
                <Skeleton className="h-6 w-32" />
              ) : (
                <Badge
                  variant={(wizard_funnel?.completion_rate ?? 0) >= 50 ? 'default' : 'secondary'}
                  className={(wizard_funnel?.completion_rate ?? 0) >= 50 ? 'bg-green-600 hover:bg-green-700' : ''}
                >
                  {wizard_funnel?.completion_rate ?? 0}% completion rate
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detail Grids */}
      <div className={`grid gap-6 lg:grid-cols-2 transition-opacity duration-150 ${contentOpacity}`}>
        {/* Popular Searches */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg font-display">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--v4v-employment)/0.1)]">
                <Search className="h-4 w-4 text-[hsl(var(--v4v-employment))]" />
              </div>
              Popular Searches
            </CardTitle>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border px-3 py-2">
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-6 w-6 rounded-full" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                    <Skeleton className="h-5 w-10" />
                  </div>
                ))}
              </div>
            ) : popular_searches.length === 0 ? (
              <p className="text-sm text-muted-foreground">No search data yet</p>
            ) : (
              <ul className="space-y-2">
                {popular_searches.map((item, index) => (
                  <li
                    key={item.query}
                    className="flex items-center justify-between rounded-lg border px-3 py-2"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-medium">
                        {index + 1}
                      </span>
                      <span className="font-medium">{item.query}</span>
                    </div>
                    <Badge variant="secondary">{item.count}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Popular Categories */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg font-display">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--v4v-training)/0.1)]">
                <Filter className="h-4 w-4 text-[hsl(var(--v4v-training))]" />
              </div>
              Popular Categories
            </CardTitle>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <div className="space-y-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border px-3 py-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-10" />
                  </div>
                ))}
              </div>
            ) : popular_categories.length === 0 ? (
              <p className="text-sm text-muted-foreground">No category data yet</p>
            ) : (
              <ul className="space-y-2">
                {popular_categories.map((item) => (
                  <li
                    key={item.category}
                    className="flex items-center justify-between rounded-lg border px-3 py-2"
                  >
                    <span className="font-medium capitalize">{item.category}</span>
                    <Badge variant="secondary">{item.count}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Popular States */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg font-display">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--v4v-housing)/0.1)]">
                <MapPin className="h-4 w-4 text-[hsl(var(--v4v-housing))]" />
              </div>
              Popular States
            </CardTitle>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border px-3 py-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-5 w-10" />
                  </div>
                ))}
              </div>
            ) : popular_states.length === 0 ? (
              <p className="text-sm text-muted-foreground">No state data yet</p>
            ) : (
              <ul className="space-y-2">
                {popular_states.map((item) => (
                  <li
                    key={item.state}
                    className="flex items-center justify-between rounded-lg border px-3 py-2"
                  >
                    <span className="font-medium">{item.state}</span>
                    <Badge variant="secondary">{item.count}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Most Viewed Resources */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg font-display">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--v4v-legal)/0.1)]">
                <FileText className="h-4 w-4 text-[hsl(var(--v4v-legal))]" />
              </div>
              Most Viewed Resources
            </CardTitle>
          </CardHeader>
          <CardContent>
            {showSkeleton ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border px-3 py-2">
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-6 w-6 rounded-full" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                    <Skeleton className="h-5 w-10" />
                  </div>
                ))}
              </div>
            ) : popular_resources.length === 0 ? (
              <p className="text-sm text-muted-foreground">No resource view data yet</p>
            ) : (
              <ul className="space-y-2">
                {popular_resources.map((item, index) => (
                  <li
                    key={item.resource_id}
                    className="flex items-center justify-between rounded-lg border px-3 py-2"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium">
                        {index + 1}
                      </span>
                      <span className="line-clamp-1 font-medium">
                        {item.resource_title || 'Unknown Resource'}
                      </span>
                    </div>
                    <Badge variant="secondary" className="shrink-0">
                      {item.count}
                    </Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Privacy Notice */}
      <div className="mt-8 rounded-xl border border-green-200 bg-green-50/80 p-5 dark:border-green-900 dark:bg-green-950/50">
        <p className="text-sm text-green-800 dark:text-green-200">
          <strong>Privacy Notice:</strong> All analytics data is anonymous. No personal
          information, IP addresses, or user identifiers are collected or stored. This helps us
          understand aggregate usage patterns to improve the service for Veterans.
        </p>
      </div>
      </div>
    </div>
  );
}
