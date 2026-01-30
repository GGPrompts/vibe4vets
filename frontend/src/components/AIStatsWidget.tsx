'use client';

import { useEffect, useState } from 'react';
import {
  Bot,
  Database,
  RefreshCw,
  CheckCircle2,
  Zap,
  Server,
  ChevronDown,
  AlertCircle,
} from 'lucide-react';
import { api, AIStats, ConnectorInfo } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';

function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return 'Never';

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'Yesterday';
  return `${diffDays} days ago`;
}

function StatCard({
  label,
  value,
  icon: Icon,
  subtext,
}: {
  label: string;
  value: string | number;
  icon: typeof Database;
  subtext?: string;
}) {
  return (
    <div className="flex flex-col items-center p-4 rounded-xl bg-[hsl(var(--v4v-bg-elevated))] border border-border/50">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[hsl(var(--v4v-gold)/0.15)] to-[hsl(var(--v4v-gold)/0.05)] mb-2">
        <Icon className="h-5 w-5 text-[hsl(var(--v4v-gold-dark))]" />
      </div>
      <span className="text-2xl font-bold text-foreground">{value}</span>
      <span className="text-xs text-muted-foreground text-center">{label}</span>
      {subtext && (
        <span className="text-xs text-[hsl(var(--v4v-gold-dark))] mt-1">{subtext}</span>
      )}
    </div>
  );
}

function ConnectorCard({ connector }: { connector: ConnectorInfo }) {
  const tierColors: Record<number, string> = {
    1: 'bg-green-500',
    2: 'bg-blue-500',
    3: 'bg-yellow-500',
    4: 'bg-orange-500',
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-[hsl(var(--v4v-bg-base))] border border-border/30">
      <div className={`h-2 w-2 rounded-full ${tierColors[connector.tier] || 'bg-gray-500'}`} />
      <div className="flex-1 min-w-0">
        <span className="font-medium text-sm text-foreground block truncate">
          {connector.display_name}
        </span>
        <span className="text-xs text-muted-foreground truncate block">
          {connector.frequency} refresh
        </span>
      </div>
      <span className="text-xs px-2 py-0.5 rounded-full bg-[hsl(var(--v4v-gold)/0.15)] text-[hsl(var(--v4v-gold-dark))]">
        Tier {connector.tier}
      </span>
    </div>
  );
}

function AIStatsWidgetSkeleton() {
  return (
    <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm overflow-hidden shadow-sm">
      <div className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <Skeleton className="h-14 w-14 rounded-xl" />
          <div className="flex-1">
            <Skeleton className="h-6 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex flex-col items-center p-4 rounded-xl bg-muted/50">
              <Skeleton className="h-10 w-10 rounded-lg mb-2" />
              <Skeleton className="h-7 w-16 mb-1" />
              <Skeleton className="h-3 w-20" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function AIStatsWidget() {
  const [stats, setStats] = useState<AIStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showConnectors, setShowConnectors] = useState(false);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await api.stats.getAIStats();
        setStats(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load AI stats');
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  if (loading) {
    return <AIStatsWidgetSkeleton />;
  }

  if (error || !stats) {
    return (
      <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm overflow-hidden shadow-sm p-6">
        <div className="flex items-center gap-3 text-muted-foreground">
          <AlertCircle className="h-5 w-5" />
          <span>Unable to load AI statistics</span>
        </div>
      </div>
    );
  }

  const totalByCategory = Object.values(stats.resources_by_category).reduce((a, b) => a + b, 0);

  return (
    <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm overflow-hidden shadow-sm">
      {/* Header with Robot Mascot */}
      <div className="p-6 pb-0">
        <div className="flex items-start gap-4 mb-6">
          {/* Robot mascot placeholder - stylized bot icon */}
          <div className="relative flex-shrink-0">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-v4v-navy to-v4v-navy/80 shadow-lg">
              <Bot className="h-8 w-8 text-[hsl(var(--v4v-gold))]" />
            </div>
            {/* Status indicator */}
            <div
              className={`absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-2 border-white ${
                stats.scheduler_status === 'Running' ? 'bg-green-500' : 'bg-yellow-500'
              }`}
            />
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="font-display text-xl font-medium text-foreground mb-1">
              AI-Powered Resource Discovery
            </h3>
            <p className="text-sm text-muted-foreground">
              Our AI agents work around the clock to discover and verify Veteran resources.
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <StatCard
            label="Resources Found"
            value={stats.total_resources.toLocaleString()}
            icon={Database}
          />
          <StatCard
            label="Verified"
            value={stats.resources_verified.toLocaleString()}
            icon={CheckCircle2}
            subtext={stats.total_resources > 0
              ? `${Math.round((stats.resources_verified / stats.total_resources) * 100)}%`
              : undefined}
          />
          <StatCard
            label="Trust Score"
            value={`${Math.round(stats.average_trust_score * 100)}%`}
            icon={Zap}
          />
          <StatCard
            label="Last Refresh"
            value={formatRelativeTime(stats.last_refresh)}
            icon={RefreshCw}
          />
        </div>

        {/* Category breakdown */}
        {totalByCategory > 0 && (
          <div className="mb-6">
            <div className="text-sm font-medium text-foreground mb-3">Resources by Category</div>
            <div className="flex gap-2 flex-wrap">
              {Object.entries(stats.resources_by_category).map(([category, count]) => (
                <span
                  key={category}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-[hsl(var(--v4v-bg-elevated))] border border-border/50"
                >
                  <span className={`h-2 w-2 rounded-full ${
                    category === 'employment' ? 'bg-v4v-employment' :
                    category === 'training' ? 'bg-v4v-training' :
                    category === 'housing' ? 'bg-v4v-housing' :
                    category === 'legal' ? 'bg-v4v-legal' : 'bg-gray-400'
                  }`} />
                  <span className="capitalize">{category}</span>
                  <span className="text-muted-foreground">{count}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Expandable Connectors Section */}
      <div className="border-t border-border/50">
        <button
          onClick={() => setShowConnectors(!showConnectors)}
          className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-[hsl(var(--v4v-bg-elevated)/0.5)] transition-colors"
        >
          <div className="flex items-center gap-3">
            <Server className="h-5 w-5 text-[hsl(var(--v4v-gold-dark))]" />
            <span className="text-sm font-medium text-foreground">
              Active Data Connectors ({stats.connectors_active.length})
            </span>
          </div>
          <ChevronDown
            className={`h-5 w-5 text-muted-foreground transition-transform duration-200 ${
              showConnectors ? 'rotate-180' : ''
            }`}
          />
        </button>

        {showConnectors && (
          <div className="px-6 pb-6 pt-2 space-y-2">
            {stats.connectors_active.map((connector) => (
              <ConnectorCard key={connector.name} connector={connector} />
            ))}
            {stats.connectors_active.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                No connectors currently configured
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer with system status */}
      <div className="bg-[hsl(var(--v4v-bg-muted))] px-6 py-3 flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full ${
            stats.scheduler_status === 'Running' ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
          }`} />
          <span>Scheduler: {stats.scheduler_status}</span>
        </div>
        <span>{stats.total_sources} data sources</span>
      </div>
    </div>
  );
}
