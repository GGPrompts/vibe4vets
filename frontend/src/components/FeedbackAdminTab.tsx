'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import api, {
  type FeedbackAdminResponse,
  type FeedbackStatus,
  type FeedbackStats,
} from '@/lib/api';

const issueTypeLabels: Record<string, string> = {
  phone: 'Phone',
  address: 'Address',
  hours: 'Hours',
  website: 'Website',
  closed: 'Closed',
  eligibility: 'Eligibility',
  other: 'Other',
};

const statusColors: Record<FeedbackStatus, string> = {
  pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  reviewed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  applied: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  dismissed: 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300',
};

export function FeedbackAdminTab() {
  const [items, setItems] = useState<FeedbackAdminResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<FeedbackStatus | 'all'>('pending');
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Review dialog state
  const [selectedItem, setSelectedItem] = useState<FeedbackAdminResponse | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState<FeedbackStatus>('reviewed');
  const [reviewer, setReviewer] = useState('');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const initialLoadDone = useRef(false);

  const fetchFeedback = useCallback(async (status: FeedbackStatus | 'all', isInitialLoad = false) => {
    if (isInitialLoad) {
      setLoading(true);
    } else {
      setIsRefreshing(true);
    }
    try {
      const response = await api.admin.getFeedback({
        status: status === 'all' ? undefined : status,
      });
      setItems(response.items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load feedback');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const data = await api.admin.getFeedbackStats();
      setStats(data);
    } catch {
      // Non-critical failure
    } finally {
      setStatsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!initialLoadDone.current) {
      fetchFeedback(activeTab, true);
      initialLoadDone.current = true;
    } else {
      fetchFeedback(activeTab, false);
    }
  }, [activeTab, fetchFeedback]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const openReviewDialog = (item: FeedbackAdminResponse) => {
    setSelectedItem(item);
    setNewStatus('reviewed');
    setReviewer('');
    setReviewerNotes('');
    setDialogOpen(true);
  };

  const handleReview = async () => {
    if (!selectedItem || !reviewer.trim()) return;

    setSubmitting(true);
    try {
      await api.admin.reviewFeedback(
        selectedItem.id,
        newStatus,
        reviewer.trim(),
        reviewerNotes.trim() || undefined
      );
      setDialogOpen(false);
      setSelectedItem(null);
      fetchFeedback(activeTab);
      fetchStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to review feedback');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid gap-4 md:grid-cols-4">
        {(['pending', 'reviewed', 'applied', 'dismissed'] as const).map((status) => (
          <div
            key={status}
            className="rounded-lg border p-4"
          >
            <div className="text-sm text-muted-foreground capitalize">{status}</div>
            <div className="text-2xl font-bold">
              {statsLoading ? (
                <Skeleton className="h-8 w-12" />
              ) : (
                stats?.[status] ?? 0
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Feedback List */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as FeedbackStatus | 'all')}>
        <TabsList>
          <TabsTrigger value="pending">
            Pending {stats?.pending ? `(${stats.pending})` : ''}
          </TabsTrigger>
          <TabsTrigger value="reviewed">Reviewed</TabsTrigger>
          <TabsTrigger value="applied">Applied</TabsTrigger>
          <TabsTrigger value="dismissed">Dismissed</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          {loading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : error ? (
            <p className="py-8 text-center text-destructive">{error}</p>
          ) : items.length === 0 ? (
            <p className="py-8 text-center text-muted-foreground">
              No feedback reports
            </p>
          ) : (
            <Table className={`transition-opacity duration-150 ${isRefreshing ? 'opacity-60' : 'opacity-100'}`}>
              <TableHeader>
                <TableRow>
                  <TableHead>Resource</TableHead>
                  <TableHead>Issue Type</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Link
                        href={`/resources/${item.resource_id}`}
                        className="font-medium hover:underline"
                      >
                        {item.resource_title}
                      </Link>
                      <p className="text-xs text-muted-foreground">
                        {item.organization_name}
                      </p>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {issueTypeLabels[item.issue_type] || item.issue_type}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <p className="line-clamp-2 text-sm">{item.description}</p>
                      {item.suggested_correction && (
                        <p className="mt-1 line-clamp-1 text-xs text-muted-foreground">
                          Suggested: {item.suggested_correction}
                        </p>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColors[item.status]}>
                        {item.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(item.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant={item.status === 'pending' ? 'default' : 'outline'}
                        onClick={() => openReviewDialog(item)}
                      >
                        {item.status === 'pending' ? 'Review' : 'Update'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>
      </Tabs>

      {/* Review Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Review Feedback</DialogTitle>
            <DialogDescription>
              {selectedItem?.resource_title || 'Review feedback details'}
            </DialogDescription>
          </DialogHeader>

          {selectedItem && (
            <div className="space-y-4 py-4">
              <div className="rounded-lg bg-muted p-4 space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Issue Type</p>
                  <p className="text-sm">
                    {issueTypeLabels[selectedItem.issue_type] || selectedItem.issue_type}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Description</p>
                  <p className="text-sm">{selectedItem.description}</p>
                </div>
                {selectedItem.suggested_correction && (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Suggested Correction</p>
                    <p className="text-sm">{selectedItem.suggested_correction}</p>
                  </div>
                )}
                {selectedItem.source_of_correction && (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Source</p>
                    <p className="text-sm">{selectedItem.source_of_correction}</p>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">
                    New Status <span className="text-destructive">*</span>
                  </label>
                  <Select value={newStatus} onValueChange={(v) => setNewStatus(v as FeedbackStatus)}>
                    <SelectTrigger className="mt-1 w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="reviewed">Reviewed</SelectItem>
                      <SelectItem value="applied">Applied (correction made)</SelectItem>
                      <SelectItem value="dismissed">Dismissed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">
                    Reviewer Name <span className="text-destructive">*</span>
                  </label>
                  <Input
                    className="mt-1"
                    value={reviewer}
                    onChange={(e) => setReviewer(e.target.value)}
                    placeholder="Your name"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Notes (optional)</label>
                  <Textarea
                    className="mt-1"
                    value={reviewerNotes}
                    onChange={(e) => setReviewerNotes(e.target.value)}
                    placeholder="Add any notes about this review..."
                    rows={3}
                  />
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleReview} disabled={!reviewer.trim() || submitting}>
              {submitting ? 'Saving...' : 'Save Review'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
