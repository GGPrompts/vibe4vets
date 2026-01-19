'use client';

import { useEffect, useState } from 'react';
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
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    async function fetchAnalytics() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.analytics.getDashboard(days);
        setDashboard(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, [days]);

  if (loading) {
    return (
      <div className="p-6">
        <div className="mb-6 flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-5 w-32" />
              </CardHeader>
              <CardContent className="space-y-2">
                {[...Array(5)].map((_, j) => (
                  <div key={j} className="flex justify-between">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-12" />
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="p-6">
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
          <p className="text-destructive">{error || 'Failed to load analytics'}</p>
        </div>
      </div>
    );
  }

  const { summary, popular_searches, popular_categories, popular_states, popular_resources, wizard_funnel } = dashboard;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Usage Analytics</h1>
          <p className="text-muted-foreground">
            Privacy-respecting usage metrics (no PII collected)
          </p>
        </div>
        <Select value={String(days)} onValueChange={(v) => setDays(Number(v))}>
          <SelectTrigger className="w-40">
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
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Searches</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_searches.toLocaleString()}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Resource Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_resource_views.toLocaleString()}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Chat Sessions</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.chat_sessions.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {summary.chat_messages.toLocaleString()} messages
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Filter Usage</CardTitle>
            <Filter className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.filter_usage.toLocaleString()}</div>
          </CardContent>
        </Card>
      </div>

      {/* Wizard Funnel */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Eligibility Wizard Funnel
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-8">
            <div>
              <p className="text-sm text-muted-foreground">Started</p>
              <p className="text-2xl font-bold">{wizard_funnel.starts.toLocaleString()}</p>
            </div>
            <TrendingUp className="h-6 w-6 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold">{wizard_funnel.completions.toLocaleString()}</p>
            </div>
            <div className="ml-auto">
              <Badge variant={wizard_funnel.completion_rate >= 50 ? 'default' : 'secondary'}>
                {wizard_funnel.completion_rate}% completion rate
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detail Grids */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Popular Searches */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Search className="h-5 w-5" />
              Popular Searches
            </CardTitle>
          </CardHeader>
          <CardContent>
            {popular_searches.length === 0 ? (
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Filter className="h-5 w-5" />
              Popular Categories
            </CardTitle>
          </CardHeader>
          <CardContent>
            {popular_categories.length === 0 ? (
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <MapPin className="h-5 w-5" />
              Popular States
            </CardTitle>
          </CardHeader>
          <CardContent>
            {popular_states.length === 0 ? (
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="h-5 w-5" />
              Most Viewed Resources
            </CardTitle>
          </CardHeader>
          <CardContent>
            {popular_resources.length === 0 ? (
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
      <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-900 dark:bg-green-950">
        <p className="text-sm text-green-800 dark:text-green-200">
          <strong>Privacy Notice:</strong> All analytics data is anonymous. No personal
          information, IP addresses, or user identifiers are collected or stored. This helps us
          understand aggregate usage patterns to improve the service for veterans.
        </p>
      </div>
    </div>
  );
}
