'use client';

import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Play,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import api, {
  type JobInfo,
  type JobHistoryEntry,
  type ConnectorInfo,
} from '@/lib/api';

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [schedulerRunning, setSchedulerRunning] = useState(false);
  const [history, setHistory] = useState<JobHistoryEntry[]>([]);
  const [connectors, setConnectors] = useState<ConnectorInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('jobs');

  // Run job dialog state
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<JobInfo | null>(null);
  const [selectedConnector, setSelectedConnector] = useState<string>('');
  const [dryRun, setDryRun] = useState(false);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.admin.getJobs();
      setJobs(response.jobs);
      setSchedulerRunning(response.scheduler_running);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const response = await api.admin.getJobHistory(50);
      setHistory(response.history);
    } catch (err) {
      // Non-critical, just log
      console.error('Failed to load job history:', err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const fetchConnectors = useCallback(async () => {
    try {
      const response = await api.admin.getConnectors();
      setConnectors(response.connectors);
    } catch (err) {
      console.error('Failed to load connectors:', err);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    fetchConnectors();
  }, [fetchJobs, fetchConnectors]);

  useEffect(() => {
    if (activeTab === 'history') {
      fetchHistory();
    }
  }, [activeTab, fetchHistory]);

  const openRunDialog = (job: JobInfo) => {
    setSelectedJob(job);
    setSelectedConnector('');
    setDryRun(false);
    setRunResult(null);
    setRunDialogOpen(true);
  };

  const handleRunJob = async () => {
    if (!selectedJob) return;

    setRunning(true);
    setRunResult(null);

    try {
      const options: { connector_name?: string; dry_run?: boolean } = {};
      if (selectedConnector && selectedConnector !== 'all') {
        options.connector_name = selectedConnector;
      }
      if (dryRun) {
        options.dry_run = true;
      }

      const result = await api.admin.runJob(selectedJob.name, options);

      setRunResult({
        success: result.status === 'success',
        message: result.message,
      });

      // Refresh data after running
      fetchJobs();
      if (activeTab === 'history') {
        fetchHistory();
      }
    } catch (err) {
      setRunResult({
        success: false,
        message: err instanceof Error ? err.message : 'Failed to run job',
      });
    } finally {
      setRunning(false);
    }
  };

  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString();
  };

  const formatRelativeTime = (dateStr: string | null) => {
    if (!dateStr) return 'Not scheduled';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();

    if (diffMs < 0) return 'Overdue';

    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 60) return `in ${diffMins}m`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `in ${diffHours}h ${diffMins % 60}m`;

    const diffDays = Math.floor(diffHours / 24);
    return `in ${diffDays}d ${diffHours % 24}h`;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return (
          <Badge variant="default" className="gap-1">
            <CheckCircle className="h-3 w-3" />
            Success
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="destructive" className="gap-1">
            <XCircle className="h-3 w-3" />
            Failed
          </Badge>
        );
      case 'running':
        return (
          <Badge variant="secondary" className="gap-1">
            <Loader2 className="h-3 w-3 animate-spin" />
            Running
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-2 mb-3">
              <div className="h-px w-8 bg-gradient-to-r from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
              <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]">Jobs</span>
              <div className="h-px w-8 bg-gradient-to-l from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
            </div>
            <h1 className="font-display text-3xl font-semibold text-foreground">Scheduled Jobs</h1>
            <p className="mt-1 text-muted-foreground">
              Manage and monitor background jobs
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchJobs();
              if (activeTab === 'history') fetchHistory();
            }}
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${schedulerRunning ? 'bg-green-500' : 'bg-red-500'}`} />
                Scheduler Status
              </CardDescription>
              <CardTitle className="text-xl">
                {loading ? (
                  <Skeleton className="h-7 w-20" />
                ) : schedulerRunning ? (
                  <span className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    Running
                  </span>
                ) : (
                  <span className="flex items-center gap-2 text-red-600">
                    <XCircle className="h-5 w-5" />
                    Stopped
                  </span>
                )}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500" />
                Scheduled Jobs
              </CardDescription>
              <CardTitle className="text-3xl text-blue-600">
                {loading ? (
                  <Skeleton className="h-9 w-16" />
                ) : (
                  jobs.filter((j) => j.scheduled).length
                )}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[hsl(var(--v4v-gold))]" />
                Available Connectors
              </CardDescription>
              <CardTitle className="text-3xl">
                {loading ? (
                  <Skeleton className="h-9 w-16" />
                ) : (
                  connectors.length
                )}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Main Content */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="font-display">Job Management</CardTitle>
            <CardDescription>
              View scheduled jobs and execution history
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList>
                <TabsTrigger value="jobs">Scheduled Jobs</TabsTrigger>
                <TabsTrigger value="history">Run History</TabsTrigger>
              </TabsList>

              {/* Jobs Tab */}
              <TabsContent value="jobs" className="mt-4">
                {loading ? (
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                ) : error ? (
                  <p className="py-8 text-center text-destructive">{error}</p>
                ) : jobs.length === 0 ? (
                  <p className="py-8 text-center text-muted-foreground">
                    No scheduled jobs configured
                  </p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Job Name</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Next Run</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {jobs.map((job) => (
                        <TableRow key={job.name}>
                          <TableCell className="font-medium">
                            {job.name}
                          </TableCell>
                          <TableCell className="max-w-xs text-muted-foreground">
                            {job.description}
                          </TableCell>
                          <TableCell>
                            {job.scheduled ? (
                              <Badge variant="default" className="gap-1">
                                <Clock className="h-3 w-3" />
                                Scheduled
                              </Badge>
                            ) : (
                              <Badge variant="outline">Manual</Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <span className="text-sm">
                              {formatRelativeTime(job.next_run)}
                            </span>
                            {job.next_run && (
                              <span className="block text-xs text-muted-foreground">
                                {formatDateTime(job.next_run)}
                              </span>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              size="sm"
                              onClick={() => openRunDialog(job)}
                              className="gap-2"
                            >
                              <Play className="h-3 w-3" />
                              Run Now
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </TabsContent>

              {/* History Tab */}
              <TabsContent value="history" className="mt-4">
                {historyLoading ? (
                  <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                ) : history.length === 0 ? (
                  <p className="py-8 text-center text-muted-foreground">
                    No job history yet
                  </p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Job</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Duration</TableHead>
                        <TableHead>Message</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {history.map((entry) => {
                        const started = new Date(entry.started_at);
                        const completed = entry.completed_at
                          ? new Date(entry.completed_at)
                          : null;
                        const durationMs = completed
                          ? completed.getTime() - started.getTime()
                          : null;
                        const durationStr = durationMs
                          ? durationMs < 1000
                            ? `${durationMs}ms`
                            : durationMs < 60000
                            ? `${(durationMs / 1000).toFixed(1)}s`
                            : `${Math.floor(durationMs / 60000)}m ${Math.floor(
                                (durationMs % 60000) / 1000
                              )}s`
                          : '-';

                        return (
                          <TableRow key={entry.run_id}>
                            <TableCell className="font-medium">
                              {entry.job_name}
                            </TableCell>
                            <TableCell>{getStatusBadge(entry.status)}</TableCell>
                            <TableCell>
                              <span className="text-sm">
                                {formatDateTime(entry.started_at)}
                              </span>
                            </TableCell>
                            <TableCell>{durationStr}</TableCell>
                            <TableCell className="max-w-xs">
                              <span className="line-clamp-2 text-sm">
                                {entry.error || entry.message}
                              </span>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Run Job Dialog */}
        <Dialog open={runDialogOpen} onOpenChange={setRunDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Run Job: {selectedJob?.name}</DialogTitle>
              <DialogDescription>
                {selectedJob?.description || 'Configure and run this scheduled job'}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {selectedJob?.name === 'refresh' && connectors.length > 0 && (
                <div>
                  <label htmlFor="connector-select" className="text-sm font-medium">
                    Connector (optional)
                  </label>
                  <Select
                    value={selectedConnector}
                    onValueChange={setSelectedConnector}
                  >
                    <SelectTrigger id="connector-select" className="mt-1" aria-describedby="connector-help">
                      <SelectValue placeholder="All connectors" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All connectors</SelectItem>
                      {connectors.map((c) => (
                        <SelectItem key={c.name} value={c.name}>
                          {c.display_name} (Tier {c.tier})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p id="connector-help" className="mt-1 text-xs text-muted-foreground">
                    Run a specific connector or all of them
                  </p>
                </div>
              )}

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="dry-run"
                  checked={dryRun}
                  onCheckedChange={(checked) => setDryRun(checked === true)}
                />
                <label
                  htmlFor="dry-run"
                  className="text-sm font-medium leading-none"
                >
                  Dry run (don&apos;t persist changes)
                </label>
              </div>

              {runResult && (
                <div
                  role="alert"
                  aria-live="polite"
                  className={`rounded-md p-3 text-sm ${
                    runResult.success
                      ? 'bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200'
                      : 'bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200'
                  }`}
                >
                  <span className="sr-only">{runResult.success ? 'Success:' : 'Error:'}</span>
                  {runResult.message}
                </div>
              )}
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setRunDialogOpen(false)}
                disabled={running}
              >
                {runResult ? 'Close' : 'Cancel'}
              </Button>
              {!runResult && (
                <Button onClick={handleRunJob} disabled={running}>
                  {running ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Run Job
                    </>
                  )}
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
