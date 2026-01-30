'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import {
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

function StatCard({
  label,
  value,
  icon: Icon,
  subtext,
  accentColor = 'gold',
}: {
  label: string;
  value: string | number;
  icon: typeof Database;
  subtext?: string;
  accentColor?: 'gold' | 'green' | 'blue' | 'purple';
}) {
  const colorClasses = {
    gold: 'from-[hsl(var(--v4v-gold))] to-amber-500',
    green: 'from-emerald-400 to-green-500',
    blue: 'from-blue-400 to-indigo-500',
    purple: 'from-purple-400 to-violet-500',
  };

  return (
    <div className="group relative flex flex-col items-center p-4 rounded-xl bg-white/80 dark:bg-zinc-800/80 border border-white/50 dark:border-zinc-700/50 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-0.5">
      <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${colorClasses[accentColor]} shadow-lg mb-2`}>
        <Icon className="h-5 w-5 text-white" />
      </div>
      <span className="text-2xl font-bold text-foreground">{value}</span>
      <span className="text-xs text-muted-foreground text-center">{label}</span>
      {subtext && (
        <span className="text-xs font-medium text-[hsl(var(--v4v-gold-dark))] mt-1">{subtext}</span>
      )}
    </div>
  );
}

function ConnectorCard({ connector }: { connector: ConnectorInfo }) {
  const tierColors: Record<number, string> = {
    1: 'bg-emerald-500',
    2: 'bg-blue-500',
    3: 'bg-amber-500',
    4: 'bg-orange-500',
  };

  const tierBg: Record<number, string> = {
    1: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
    2: 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
    3: 'bg-amber-500/10 text-amber-700 dark:text-amber-400',
    4: 'bg-orange-500/10 text-orange-700 dark:text-orange-400',
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-white/60 dark:bg-zinc-800/60 border border-white/50 dark:border-zinc-700/50 hover:bg-white/80 dark:hover:bg-zinc-800/80 transition-colors">
      <div className={`h-2.5 w-2.5 rounded-full ${tierColors[connector.tier] || 'bg-gray-500'} shadow-sm`} />
      <div className="flex-1 min-w-0">
        <span className="font-medium text-sm text-foreground block truncate">
          {connector.display_name}
        </span>
        <span className="text-xs text-muted-foreground truncate block">
          {connector.frequency} refresh
        </span>
      </div>
      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${tierBg[connector.tier] || 'bg-gray-100 text-gray-600'}`}>
        Tier {connector.tier}
      </span>
    </div>
  );
}

function AIStatsWidgetSkeleton() {
  return (
    <div className="rounded-2xl overflow-hidden shadow-xl border-2 border-[hsl(var(--v4v-gold)/0.3)] bg-gradient-to-br from-slate-50 via-white to-amber-50/30 dark:from-v4v-navy dark:via-v4v-navy/95 dark:to-slate-900">
      <div className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <Skeleton className="h-20 w-20 rounded-xl" />
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
      <div className="rounded-2xl overflow-hidden shadow-xl border-2 border-border/50 bg-gradient-to-br from-slate-50 via-white to-amber-50/30 dark:from-v4v-navy dark:via-v4v-navy/95 dark:to-slate-900 p-6">
        <div className="flex items-center gap-3 text-muted-foreground">
          <AlertCircle className="h-5 w-5" />
          <span>Unable to load AI statistics</span>
        </div>
      </div>
    );
  }

  const totalByCategory = Object.values(stats.resources_by_category).reduce((a, b) => a + b, 0);

  return (
    <div className="relative rounded-2xl overflow-hidden shadow-xl border-2 border-[hsl(var(--v4v-gold)/0.3)] bg-gradient-to-br from-slate-50 via-white to-amber-50/30 dark:from-v4v-navy dark:via-v4v-navy/95 dark:to-slate-900">
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-[hsl(var(--v4v-gold))] opacity-10 dark:opacity-5 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-blue-500 opacity-10 dark:opacity-5 blur-3xl rounded-full translate-y-1/2 -translate-x-1/2" />

      {/* Content */}
      <div className="relative">
        {/* Header with Robot Mascots */}
        <div className="p-6 pb-4">
          <div className="flex items-center gap-4 mb-6">
            {/* Robot mascot - searching */}
            <div className="relative flex-shrink-0">
              <div className="relative h-20 w-20 rounded-xl overflow-hidden bg-gradient-to-br from-[hsl(var(--v4v-gold)/0.15)] to-[hsl(var(--v4v-gold)/0.05)] border border-[hsl(var(--v4v-gold)/0.2)] p-1">
                <Image
                  src="/about/vetrdbotsearching.png"
                  alt="VetRD Bot searching"
                  width={80}
                  height={80}
                  className="object-contain drop-shadow-lg"
                />
              </div>
              {/* Status indicator */}
              <div
                className={`absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-2 border-white dark:border-v4v-navy shadow-lg ${
                  stats.scheduler_status === 'Running' ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              />
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="font-display text-xl font-semibold text-foreground mb-1">
                AI-Powered Resource Discovery
              </h3>
              <p className="text-sm text-muted-foreground">
                Our AI agents work around the clock to discover and verify Veteran resources.
              </p>
            </div>

            {/* Robot mascot - researching (hidden on mobile) */}
            <div className="hidden sm:block relative flex-shrink-0">
              <div className="relative h-20 w-20 rounded-xl overflow-hidden bg-gradient-to-br from-[hsl(var(--v4v-gold)/0.15)] to-[hsl(var(--v4v-gold)/0.05)] border border-[hsl(var(--v4v-gold)/0.2)] p-1">
                <Image
                  src="/about/vetrdbotresearching.png"
                  alt="VetRD Bot researching"
                  width={80}
                  height={80}
                  className="object-contain drop-shadow-lg"
                />
              </div>
            </div>
          </div>

          {/* Stats Grid - glass cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <StatCard
              label="Resources Found"
              value={stats.total_resources.toLocaleString()}
              icon={Database}
              accentColor="gold"
            />
            <StatCard
              label="Verified"
              value={stats.resources_verified.toLocaleString()}
              icon={CheckCircle2}
              accentColor="green"
              subtext={stats.total_resources > 0
                ? `${Math.round((stats.resources_verified / stats.total_resources) * 100)}%`
                : undefined}
            />
            <StatCard
              label="Trust Score"
              value={`${Math.round(stats.average_trust_score * 100)}%`}
              icon={Zap}
              accentColor="purple"
            />
            <StatCard
              label="Auto-Refresh"
              value="Scheduled"
              icon={RefreshCw}
              accentColor="blue"
              subtext="Daily updates"
            />
          </div>

          {/* Category breakdown */}
          {totalByCategory > 0 && (
            <div className="mb-4">
              <div className="text-sm font-medium text-foreground mb-3">Resources by Category</div>
              <div className="flex gap-2 flex-wrap">
                {Object.entries(stats.resources_by_category).map(([category, count]) => (
                  <span
                    key={category}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-muted/80 border border-border/50 text-foreground"
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
            className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-muted/50 transition-colors"
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
        <div className="bg-muted/50 px-6 py-3 flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${
              stats.scheduler_status === 'Running' ? 'bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50' : 'bg-amber-400'
            }`} />
            <span>Scheduler: {stats.scheduler_status}</span>
          </div>
          <span>{stats.total_sources} data sources</span>
        </div>
      </div>
    </div>
  );
}
