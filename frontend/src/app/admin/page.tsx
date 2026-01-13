'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
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
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import api, { type ReviewQueueItem } from '@/lib/api';

export default function AdminPage() {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<ReviewQueueItem | null>(null);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [action, setAction] = useState<'approve' | 'reject' | null>(null);
  const [reviewer, setReviewer] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('pending');

  const fetchQueue = async (status: string) => {
    setLoading(true);
    try {
      const response = await api.admin.getReviewQueue({
        status: status === 'all' ? undefined : status,
      });
      setItems(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load queue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue(activeTab);
  }, [activeTab]);

  const handleAction = async () => {
    if (!selectedItem || !action || !reviewer.trim()) return;

    setSubmitting(true);
    try {
      await api.admin.reviewResource(
        selectedItem.id,
        action,
        reviewer.trim(),
        notes.trim() || undefined
      );
      setActionDialogOpen(false);
      setSelectedItem(null);
      setAction(null);
      setReviewer('');
      setNotes('');
      // Refresh the queue
      fetchQueue(activeTab);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  const openActionDialog = (
    item: ReviewQueueItem,
    actionType: 'approve' | 'reject'
  ) => {
    setSelectedItem(item);
    setAction(actionType);
    setActionDialogOpen(true);
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Review Queue</h1>
          <p className="text-muted-foreground">
            Resources pending human verification
          </p>
        </div>

        {/* Stats Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Pending Reviews</CardDescription>
              <CardTitle className="text-3xl">
                {loading ? <Skeleton className="h-9 w-16" /> : items.length}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Approved Today</CardDescription>
              <CardTitle className="text-3xl">-</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Resources</CardDescription>
              <CardTitle className="text-3xl">-</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Review Queue */}
        <Card>
          <CardHeader>
            <CardTitle>Review Queue</CardTitle>
            <CardDescription>
              Resources pending human verification
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList>
                <TabsTrigger value="pending">Pending</TabsTrigger>
                <TabsTrigger value="approved">Approved</TabsTrigger>
                <TabsTrigger value="rejected">Rejected</TabsTrigger>
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
                    No items in queue
                  </p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Resource</TableHead>
                        <TableHead>Organization</TableHead>
                        <TableHead>Reason</TableHead>
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
                          </TableCell>
                          <TableCell>{item.organization_name}</TableCell>
                          <TableCell className="max-w-xs truncate">
                            {item.reason || 'Manual entry'}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                item.status === 'pending'
                                  ? 'secondary'
                                  : item.status === 'approved'
                                  ? 'default'
                                  : 'destructive'
                              }
                            >
                              {item.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {new Date(item.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="text-right">
                            {item.status === 'pending' && (
                              <div className="flex justify-end gap-2">
                                <Button
                                  size="sm"
                                  onClick={() =>
                                    openActionDialog(item, 'approve')
                                  }
                                >
                                  Approve
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() =>
                                    openActionDialog(item, 'reject')
                                  }
                                >
                                  Reject
                                </Button>
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Action Dialog */}
        <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {action === 'approve' ? 'Approve' : 'Reject'} Resource
              </DialogTitle>
              <DialogDescription>
                {selectedItem?.resource_title}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">
                  Reviewer Name <span className="text-destructive">*</span>
                </label>
                <Input
                  value={reviewer}
                  onChange={(e) => setReviewer(e.target.value)}
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Notes (optional)</label>
                <Input
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any notes..."
                />
              </div>

              {selectedItem?.changes_summary &&
                selectedItem.changes_summary.length > 0 && (
                  <div>
                    <label className="text-sm font-medium">Recent Changes</label>
                    <div className="mt-1 rounded-md bg-muted p-2 text-sm">
                      {selectedItem.changes_summary.map((change, i) => (
                        <p key={i}>{change}</p>
                      ))}
                    </div>
                  </div>
                )}
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setActionDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant={action === 'approve' ? 'default' : 'destructive'}
                onClick={handleAction}
                disabled={!reviewer.trim() || submitting}
              >
                {submitting
                  ? 'Processing...'
                  : action === 'approve'
                  ? 'Approve'
                  : 'Reject'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
