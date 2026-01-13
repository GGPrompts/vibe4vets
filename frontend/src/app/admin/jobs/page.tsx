'use client';

import { useEffect, useState } from 'react';
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
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Play, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface ScheduledJob {
  name: string;
  description: string;
  schedule: string;
  enabled: boolean;
  last_run: string | null;
  next_run: string | null;
  last_status: 'success' | 'failed' | 'running' | null;
}

interface JobHistory {
  id: string;
  job_name: string;
  started_at: string;
  completed_at: string | null;
  status: 'success' | 'failed' | 'running';
  error_message: string | null;
  records_processed: number;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<ScheduledJob[]>([]);
  const [history, setHistory] = useState<JobHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runningJob, setRunningJob] = useState<string | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<ScheduledJob | null>(null);

  const fetchData = async () => {
    try {
      const [jobsRes, historyRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/admin/jobs`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/admin/jobs/history?limit=10`),
      ]);

      if (!jobsRes.ok || !historyRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const jobsData = await jobsRes.json();
      const historyData = await historyRes.json();

      setJobs(jobsData.jobs || []);
      setHistory(historyData.history || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRunJob = async () => {
    if (!selectedJob) return;

    setRunningJob(selectedJob.name);
    setConfirmDialogOpen(false);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/admin/jobs/${selectedJob.name}/run`,
        { method: 'POST' }
      );

      if (!res.ok) {
        throw new Error('Failed to trigger job');
      }

      // Refresh data after a short delay
      setTimeout(() => {
        fetchData();
        setRunningJob(null);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run job');
      setRunningJob(null);
    }
  };

  const openConfirmDialog = (job: ScheduledJob) => {
    setSelectedJob(job);
    setConfirmDialogOpen(true);
  };

  const getStatusIcon = (status: string | null) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string | null) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-green-100 text-green-800">Success</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'running':
        return <Badge className="bg-blue-100 text-blue-800">Running</Badge>;
      default:
        return <Badge variant="secondary">Never Run</Badge>;
    }
  };

  const formatDuration = (start: string, end: string | null) => {
    if (!end) return 'In progress';
    const ms = new Date(end).getTime() - new Date(start).getTime();
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Scheduled Jobs</h1>
          <p className="text-muted-foreground">
            Manage data refresh and maintenance tasks
          </p>
        </div>

        {/* Jobs Table */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Active Jobs</CardTitle>
            <CardDescription>
              Scheduled tasks for data collection and maintenance
            </CardDescription>
          </CardHeader>
          <CardContent>
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
                No jobs configured
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Job</TableHead>
                    <TableHead>Schedule</TableHead>
                    <TableHead>Last Status</TableHead>
                    <TableHead>Last Run</TableHead>
                    <TableHead>Next Run</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.name}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.last_status)}
                          <div>
                            <span className="font-medium">{job.name}</span>
                            <p className="text-xs text-muted-foreground">
                              {job.description}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                          {job.schedule}
                        </code>
                      </TableCell>
                      <TableCell>{getStatusBadge(job.last_status)}</TableCell>
                      <TableCell>
                        {job.last_run
                          ? new Date(job.last_run).toLocaleString()
                          : 'Never'}
                      </TableCell>
                      <TableCell>
                        {job.next_run
                          ? new Date(job.next_run).toLocaleString()
                          : 'Not scheduled'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => openConfirmDialog(job)}
                          disabled={runningJob === job.name || !job.enabled}
                        >
                          {runningJob === job.name ? (
                            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                          ) : (
                            <Play className="mr-1 h-3 w-3" />
                          )}
                          Run Now
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* History Table */}
        <Card>
          <CardHeader>
            <CardTitle>Recent History</CardTitle>
            <CardDescription>Last 10 job executions</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
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
                    <TableHead>Started</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Records</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="font-medium">
                        {entry.job_name}
                      </TableCell>
                      <TableCell>
                        {new Date(entry.started_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {formatDuration(entry.started_at, entry.completed_at)}
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(entry.status)}
                        {entry.error_message && (
                          <p className="mt-1 text-xs text-destructive">
                            {entry.error_message}
                          </p>
                        )}
                      </TableCell>
                      <TableCell>
                        {entry.records_processed.toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Confirm Dialog */}
        <Dialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Run Job Manually</DialogTitle>
              <DialogDescription>
                Are you sure you want to run "{selectedJob?.name}"? This will
                execute the job immediately outside of its normal schedule.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setConfirmDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleRunJob}>
                <Play className="mr-1 h-4 w-4" />
                Run Job
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
