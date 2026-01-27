'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import {
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
} from 'lucide-react';
import api, { type SourceHealthDetail, type ErrorRecord } from '@/lib/api';

const STATUS_CONFIG = {
  healthy: {
    textColor: 'text-green-700 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-950',
    borderColor: 'border-green-200 dark:border-green-800',
    dotColor: 'bg-green-500',
    icon: CheckCircle2,
    label: 'Healthy',
  },
  degraded: {
    textColor: 'text-yellow-700 dark:text-yellow-400',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    dotColor: 'bg-yellow-500',
    icon: AlertTriangle,
    label: 'Degraded',
  },
  failing: {
    textColor: 'text-red-700 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-950',
    borderColor: 'border-red-200 dark:border-red-800',
    dotColor: 'bg-red-500',
    icon: AlertCircle,
    label: 'Failing',
  },
} as const;

const TIER_LABELS: Record<number, string> = {
  1: 'Tier 1 (Official)',
  2: 'Tier 2 (Verified)',
  3: 'Tier 3 (State)',
  4: 'Tier 4 (Community)',
};

function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return 'Never';

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

function StatusBadge({ status }: { status: SourceHealthDetail['status'] }) {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${config.bgColor} ${config.textColor} border ${config.borderColor}`}
    >
      <Icon className="h-3 w-3" />
      {config.label}
    </div>
  );
}

function TierBadge({ tier }: { tier: number }) {
  const variants: Record<number, string> = {
    1: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    2: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    3: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    4: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  };

  return (
    <Badge variant="secondary" className={variants[tier] || variants[4]}>
      Tier {tier}
    </Badge>
  );
}

function SourceDetailDialog({
  source,
  open,
  onOpenChange,
}: {
  source: SourceHealthDetail | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  if (!source) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {source.name}
            <StatusBadge status={source.status} />
          </DialogTitle>
          <DialogDescription>
            <div className="flex items-center gap-2">
              {source.url}
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:text-primary/80"
                aria-label={`Visit ${source.name} website`}
              >
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            <p className="sr-only">
              Source status: {source.status}. Resources: {source.resource_count}. Success rate: {Math.round(source.success_rate * 100)}%
            </p>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-lg bg-muted p-3">
              <p className="text-xs text-muted-foreground">Resources</p>
              <p className="text-2xl font-bold">{source.resource_count}</p>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <p className="text-xs text-muted-foreground">Success Rate</p>
              <p className="text-2xl font-bold">
                {Math.round(source.success_rate * 100)}%
              </p>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <p className="text-xs text-muted-foreground">Freshness</p>
              <p className="text-2xl font-bold">
                {Math.round(source.average_freshness * 100)}%
              </p>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <p className="text-xs text-muted-foreground">Errors</p>
              <p
                className={`text-2xl font-bold ${source.error_count > 0 ? 'text-red-600' : ''}`}
              >
                {source.error_count}
              </p>
            </div>
          </div>

          {/* Source Info */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Source Information</h4>
            <div className="rounded-lg border p-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tier</span>
                <span>{TIER_LABELS[source.tier] || `Tier ${source.tier}`}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type</span>
                <span className="capitalize">{source.source_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Frequency</span>
                <span className="capitalize">{source.frequency}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Run</span>
                <span>{formatRelativeTime(source.last_run)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Success</span>
                <span>{formatRelativeTime(source.last_success)}</span>
              </div>
            </div>
          </div>

          {/* Resources by Status */}
          {Object.keys(source.resources_by_status).length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Resources by Status</h4>
              <div className="flex flex-wrap gap-2">
                {Object.entries(source.resources_by_status).map(
                  ([status, count]) => (
                    <Badge key={status} variant="outline">
                      {status}: {count}
                    </Badge>
                  )
                )}
              </div>
            </div>
          )}

          {/* Recent Errors */}
          {source.errors.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-red-600">Recent Errors</h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {source.errors.map((error: ErrorRecord) => (
                  <div
                    key={error.id}
                    className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-3 text-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-medium text-red-800 dark:text-red-200">
                          {error.error_type}
                        </p>
                        <p className="text-red-700 dark:text-red-300 mt-1">
                          {error.message}
                        </p>
                      </div>
                      <span className="text-xs text-red-600 dark:text-red-400 whitespace-nowrap">
                        {formatRelativeTime(error.occurred_at)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function SourcesPage() {
  const [sources, setSources] = useState<SourceHealthDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState<SourceHealthDetail | null>(
    null
  );
  const [detailOpen, setDetailOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchSources = useCallback(async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);

    try {
      const response = await api.admin.getSourcesHealth();
      setSources(response.sources);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sources');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchSources();
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchSources]);

  const handleSourceClick = (source: SourceHealthDetail) => {
    setSelectedSource(source);
    setDetailOpen(true);
  };

  const handleManualRefresh = () => {
    fetchSources(true);
  };

  // Calculate summary stats
  const healthySources = sources.filter((s) => s.status === 'healthy').length;
  const degradedSources = sources.filter((s) => s.status === 'degraded').length;
  const failingSources = sources.filter((s) => s.status === 'failing').length;
  const totalResources = sources.reduce((sum, s) => sum + s.resource_count, 0);

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 mb-3">
              <div className="h-px w-8 bg-gradient-to-r from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
              <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]">Data Sources</span>
              <div className="h-px w-8 bg-gradient-to-l from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
            </div>
            <h1 className="font-display text-3xl font-semibold text-foreground">Source Health</h1>
            <p className="mt-1 text-muted-foreground">
              Monitor source health and data freshness
            </p>
          </div>
          <div className="flex items-center gap-4">
            {lastUpdated && (
              <span className="text-sm text-muted-foreground">
                Updated {formatRelativeTime(lastUpdated.toISOString())}
              </span>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleManualRefresh}
              disabled={refreshing}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`}
              />
              Refresh
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[hsl(var(--v4v-gold))]" />
                Total Sources
              </CardDescription>
              <CardTitle className="text-3xl">
                {loading ? <Skeleton className="h-9 w-12" /> : sources.length}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500" />
                Healthy
              </CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {loading ? <Skeleton className="h-9 w-12" /> : healthySources}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-yellow-500" />
                Degraded
              </CardDescription>
              <CardTitle className="text-3xl text-yellow-600">
                {loading ? <Skeleton className="h-9 w-12" /> : degradedSources}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500" />
                Failing
              </CardDescription>
              <CardTitle className="text-3xl text-red-600">
                {loading ? <Skeleton className="h-9 w-12" /> : failingSources}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Sources Table */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="font-display">All Sources</CardTitle>
            <CardDescription>
              {loading ? (
                <Skeleton className="h-4 w-48" />
              ) : (
                `${sources.length} sources providing ${totalResources} resources`
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : error ? (
              <div className="py-8 text-center">
                <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
                <p className="text-destructive">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleManualRefresh}
                  className="mt-4"
                >
                  Try Again
                </Button>
              </div>
            ) : sources.length === 0 ? (
              <p className="py-8 text-center text-muted-foreground">
                No data sources configured
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Source</TableHead>
                    <TableHead>Tier</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Resources</TableHead>
                    <TableHead className="text-right">Errors</TableHead>
                    <TableHead>Last Refresh</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sources.map((source) => (
                    <TableRow
                      key={source.source_id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSourceClick(source)}
                    >
                      <TableCell>
                        <div>
                          <p className="font-medium">{source.name}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-xs">
                            {source.url}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <TierBadge tier={source.tier} />
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={source.status} />
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {source.resource_count}
                      </TableCell>
                      <TableCell className="text-right">
                        <span
                          className={
                            source.error_count > 0 ? 'text-red-600 font-medium' : ''
                          }
                        >
                          {source.error_count}
                        </span>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatRelativeTime(source.last_run)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Source Detail Dialog */}
        <SourceDetailDialog
          source={selectedSource}
          open={detailOpen}
          onOpenChange={setDetailOpen}
        />
      </div>
    </div>
  );
}
