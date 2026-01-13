'use client';

import { useEffect, useState } from 'react';
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
import { Skeleton } from '@/components/ui/skeleton';
import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react';

interface SourceHealth {
  id: string;
  name: string;
  tier: number;
  status: 'healthy' | 'degraded' | 'failing';
  last_run: string | null;
  success_rate: number;
  resources_count: number;
  error_message: string | null;
}

interface DashboardStats {
  total_sources: number;
  healthy_sources: number;
  degraded_sources: number;
  failing_sources: number;
  total_resources: number;
  pending_reviews: number;
}

export default function SourcesPage() {
  const [sources, setSources] = useState<SourceHealth[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sourcesRes, statsRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/admin/dashboard/sources`),
          fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/admin/dashboard/stats`),
        ]);

        if (!sourcesRes.ok || !statsRes.ok) {
          throw new Error('Failed to fetch data');
        }

        const sourcesData = await sourcesRes.json();
        const statsData = await statsRes.json();

        setSources(sourcesData.sources || []);
        setStats(statsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load sources');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'failing':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <Badge className="bg-green-100 text-green-800">Healthy</Badge>;
      case 'degraded':
        return <Badge className="bg-yellow-100 text-yellow-800">Degraded</Badge>;
      case 'failing':
        return <Badge variant="destructive">Failing</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getTierLabel = (tier: number) => {
    const labels: Record<number, string> = {
      1: 'Official',
      2: 'VSO',
      3: 'State',
      4: 'Community',
    };
    return labels[tier] || `Tier ${tier}`;
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Data Sources</h1>
          <p className="text-muted-foreground">
            Monitor connector health and data freshness
          </p>
        </div>

        {/* Stats Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Sources</CardDescription>
              <CardTitle className="text-3xl">
                {loading ? <Skeleton className="h-9 w-12" /> : stats?.total_sources ?? 0}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <CheckCircle className="h-3 w-3 text-green-500" />
                Healthy
              </CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {loading ? <Skeleton className="h-9 w-12" /> : stats?.healthy_sources ?? 0}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <AlertCircle className="h-3 w-3 text-yellow-500" />
                Degraded
              </CardDescription>
              <CardTitle className="text-3xl text-yellow-600">
                {loading ? <Skeleton className="h-9 w-12" /> : stats?.degraded_sources ?? 0}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <XCircle className="h-3 w-3 text-red-500" />
                Failing
              </CardDescription>
              <CardTitle className="text-3xl text-red-600">
                {loading ? <Skeleton className="h-9 w-12" /> : stats?.failing_sources ?? 0}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Sources Table */}
        <Card>
          <CardHeader>
            <CardTitle>Source Health</CardTitle>
            <CardDescription>
              Status of all configured data connectors
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : error ? (
              <p className="py-8 text-center text-destructive">{error}</p>
            ) : sources.length === 0 ? (
              <p className="py-8 text-center text-muted-foreground">
                No sources configured
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Source</TableHead>
                    <TableHead>Tier</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Success Rate</TableHead>
                    <TableHead>Resources</TableHead>
                    <TableHead>Last Run</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sources.map((source) => (
                    <TableRow key={source.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(source.status)}
                          <span className="font-medium">{source.name}</span>
                        </div>
                        {source.error_message && (
                          <p className="mt-1 text-xs text-destructive">
                            {source.error_message}
                          </p>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{getTierLabel(source.tier)}</Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(source.status)}</TableCell>
                      <TableCell>
                        <span
                          className={
                            source.success_rate >= 90
                              ? 'text-green-600'
                              : source.success_rate >= 70
                              ? 'text-yellow-600'
                              : 'text-red-600'
                          }
                        >
                          {source.success_rate.toFixed(0)}%
                        </span>
                      </TableCell>
                      <TableCell>{source.resources_count.toLocaleString()}</TableCell>
                      <TableCell>
                        {source.last_run
                          ? new Date(source.last_run).toLocaleString()
                          : 'Never'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
