'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
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
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Globe,
  Phone,
  MapPin,
  ExternalLink,
  AlertCircle,
} from 'lucide-react';
import api, { type ReviewQueueItem, type DashboardStats, type FeedbackStats, type Resource } from '@/lib/api';
import { FeedbackAdminTab } from '@/components/FeedbackAdminTab';

export default function AdminPage() {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<ReviewQueueItem | null>(null);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [resourceLoading, setResourceLoading] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [action, setAction] = useState<'approve' | 'reject' | null>(null);
  const [reviewer, setReviewer] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('pending');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [mainTab, setMainTab] = useState<'reviews' | 'feedback'>('reviews');

  // Ref to track the current fetch request and cancel stale ones
  const fetchAbortControllerRef = useRef<AbortController | null>(null);

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

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [dashboardData, feedbackData] = await Promise.all([
          api.admin.getDashboardStats(),
          api.admin.getFeedbackStats(),
        ]);
        setStats(dashboardData);
        setFeedbackStats(feedbackData);
      } catch {
        // Stats fetch failure is non-critical, just leave as null
      } finally {
        setStatsLoading(false);
      }
    };
    fetchStats();
  }, []);

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
      closeSheet();
      // Refresh the queue
      fetchQueue(activeTab);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  // Fetch resource details when opening the review sheet
  // Uses AbortController to cancel pending requests when a new one starts,
  // preventing race conditions where a slow response overwrites newer data.
  const fetchResourceDetails = useCallback(async (resourceId: string) => {
    // Cancel any pending fetch before starting a new one
    if (fetchAbortControllerRef.current) {
      fetchAbortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    fetchAbortControllerRef.current = abortController;

    setResourceLoading(true);
    try {
      const resource = await api.resources.get(resourceId);

      // Only update state if this request wasn't aborted
      if (!abortController.signal.aborted) {
        setSelectedResource(resource);
      }
    } catch {
      // Only update state if this request wasn't aborted
      if (!abortController.signal.aborted) {
        setSelectedResource(null);
      }
    } finally {
      // Only update loading state if this request wasn't aborted
      if (!abortController.signal.aborted) {
        setResourceLoading(false);
      }
    }
  }, []);

  const openReviewSheet = (
    item: ReviewQueueItem,
    actionType: 'approve' | 'reject'
  ) => {
    setSelectedItem(item);
    setAction(actionType);
    setSheetOpen(true);
    fetchResourceDetails(item.resource_id);
  };

  const closeSheet = () => {
    // Cancel any pending resource fetch
    if (fetchAbortControllerRef.current) {
      fetchAbortControllerRef.current.abort();
      fetchAbortControllerRef.current = null;
    }
    setResourceLoading(false);
    setSheetOpen(false);
    setSelectedItem(null);
    setSelectedResource(null);
    setAction(null);
    setReviewer('');
    setNotes('');
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <div className="h-px w-8 bg-gradient-to-r from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
            <span className="text-sm font-medium uppercase tracking-widest text-[hsl(var(--v4v-gold-dark))]">Dashboard</span>
            <div className="h-px w-8 bg-gradient-to-l from-transparent to-[hsl(var(--v4v-gold)/0.5)]" />
          </div>
          <h1 className="font-display text-3xl font-semibold text-foreground">Review Queue</h1>
          <p className="mt-1 text-muted-foreground">
            Resources pending human verification
          </p>
        </div>

        {/* Stats Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-amber-500" />
                Pending Reviews
              </CardDescription>
              <CardTitle className="text-3xl text-amber-600">
                {statsLoading ? (
                  <Skeleton className="h-9 w-16" />
                ) : (
                  stats?.pending_reviews ?? '-'
                )}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500" />
                Pending Feedback
              </CardDescription>
              <CardTitle className="text-3xl text-blue-600">
                {statsLoading ? (
                  <Skeleton className="h-9 w-16" />
                ) : (
                  feedbackStats?.pending ?? '-'
                )}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500" />
                Approved Today
              </CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {statsLoading ? (
                  <Skeleton className="h-9 w-16" />
                ) : (
                  stats?.approved_today ?? '-'
                )}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-200">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[hsl(var(--v4v-gold))]" />
                Total Resources
              </CardDescription>
              <CardTitle className="text-3xl">
                {statsLoading ? (
                  <Skeleton className="h-9 w-16" />
                ) : (
                  stats?.total_resources ?? '-'
                )}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Main Tab Navigation */}
        <Tabs value={mainTab} onValueChange={(v) => setMainTab(v as 'reviews' | 'feedback')} className="mb-6">
          <TabsList className="bg-muted/50">
            <TabsTrigger value="reviews" className="data-[state=active]:bg-card data-[state=active]:shadow-sm">
              Review Queue {stats?.pending_reviews ? `(${stats.pending_reviews})` : ''}
            </TabsTrigger>
            <TabsTrigger value="feedback" className="data-[state=active]:bg-card data-[state=active]:shadow-sm">
              User Feedback {feedbackStats?.pending ? `(${feedbackStats.pending})` : ''}
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Review Queue - shown when mainTab is 'reviews' */}
        {mainTab === 'reviews' && (
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="font-display">Review Queue</CardTitle>
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
                    <div className="overflow-x-auto rounded-md border">
                      <TooltipProvider>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead className="min-w-[200px]">Resource</TableHead>
                              <TableHead className="min-w-[150px]">Organization</TableHead>
                              <TableHead className="min-w-[200px]">Reason</TableHead>
                              <TableHead className="min-w-[80px]">Status</TableHead>
                              <TableHead className="min-w-[100px]">Date</TableHead>
                              <TableHead className="sticky right-0 bg-background min-w-[160px] text-right">Actions</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {items.map((item) => (
                              <TableRow key={item.id}>
                                <TableCell className="font-medium">
                                  <Link
                                    href={`/resources/${item.resource_id}`}
                                    target="_blank"
                                    className="flex items-center gap-1 hover:underline"
                                  >
                                    <span className="line-clamp-2">{item.resource_title}</span>
                                    <ExternalLink className="h-3 w-3 flex-shrink-0 text-muted-foreground" />
                                  </Link>
                                </TableCell>
                                <TableCell className="text-sm text-muted-foreground">
                                  {item.organization_name}
                                </TableCell>
                                <TableCell>
                                  <Tooltip>
                                    <TooltipTrigger asChild>
                                      <div className="max-w-[200px] cursor-help">
                                        <p className="line-clamp-2 text-sm">
                                          {item.reason || 'Manual entry'}
                                        </p>
                                      </div>
                                    </TooltipTrigger>
                                    <TooltipContent side="bottom" className="max-w-sm">
                                      <p className="text-sm">{item.reason || 'Manual entry'}</p>
                                    </TooltipContent>
                                  </Tooltip>
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
                                <TableCell className="text-sm text-muted-foreground">
                                  {new Date(item.created_at).toLocaleDateString()}
                                </TableCell>
                                <TableCell className="sticky right-0 bg-background">
                                  {item.status === 'pending' && (
                                    <div className="flex justify-end gap-2">
                                      <Button
                                        size="sm"
                                        onClick={() =>
                                          openReviewSheet(item, 'approve')
                                        }
                                      >
                                        Approve
                                      </Button>
                                      <Button
                                        size="sm"
                                        variant="destructive"
                                        onClick={() =>
                                          openReviewSheet(item, 'reject')
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
                      </TooltipProvider>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}

        {/* User Feedback - shown when mainTab is 'feedback' */}
        {mainTab === 'feedback' && (
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="font-display">User Feedback</CardTitle>
              <CardDescription>
                Reports from users about outdated or incorrect resource information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FeedbackAdminTab />
            </CardContent>
          </Card>
        )}

        {/* Review Sheet (Side Panel) */}
        <Sheet open={sheetOpen} onOpenChange={(open) => !open && closeSheet()}>
          <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
            <SheetHeader>
              <SheetTitle className="flex items-center gap-2">
                {action === 'approve' ? (
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300">
                    Approve
                  </Badge>
                ) : (
                  <Badge variant="destructive">Reject</Badge>
                )}
                Review Resource
              </SheetTitle>
              <SheetDescription>
                Review the resource details below and submit your decision
              </SheetDescription>
            </SheetHeader>

            <ScrollArea className="h-[calc(100vh-220px)] pr-4">
              <div className="space-y-6 py-4">
                {/* Resource Details */}
                {resourceLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                ) : selectedResource ? (
                  <>
                    {/* Title & Organization */}
                    <div>
                      <h3 className="text-lg font-semibold">{selectedResource.title}</h3>
                      <p className="text-sm text-muted-foreground">
                        {selectedResource.organization.name}
                      </p>
                    </div>

                    {/* Categories & States */}
                    <div className="flex flex-wrap gap-2">
                      {selectedResource.categories.map((cat) => (
                        <Badge key={cat} variant="outline" className="capitalize">
                          {cat}
                        </Badge>
                      ))}
                      {selectedResource.scope === 'national' ? (
                        <Badge variant="secondary">Nationwide</Badge>
                      ) : (
                        selectedResource.states.map((state) => (
                          <Badge key={state} variant="secondary">
                            {state}
                          </Badge>
                        ))
                      )}
                    </div>

                    <Separator />

                    {/* Description */}
                    <div>
                      <h4 className="mb-2 text-sm font-medium text-muted-foreground">Description</h4>
                      <p className="text-sm whitespace-pre-wrap">{selectedResource.description}</p>
                    </div>

                    {/* Eligibility */}
                    {selectedResource.eligibility && (
                      <div>
                        <h4 className="mb-2 text-sm font-medium text-muted-foreground">Eligibility</h4>
                        <p className="text-sm whitespace-pre-wrap">{selectedResource.eligibility}</p>
                      </div>
                    )}

                    {/* How to Apply */}
                    {selectedResource.how_to_apply && (
                      <div>
                        <h4 className="mb-2 text-sm font-medium text-muted-foreground">How to Apply</h4>
                        <p className="text-sm whitespace-pre-wrap">{selectedResource.how_to_apply}</p>
                      </div>
                    )}

                    <Separator />

                    {/* Contact Info */}
                    <div className="space-y-3">
                      <h4 className="text-sm font-medium text-muted-foreground">Contact Information</h4>
                      {selectedResource.website && (
                        <a
                          href={selectedResource.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 text-sm text-primary hover:underline"
                        >
                          <Globe className="h-4 w-4" />
                          {selectedResource.website}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                      {selectedResource.phone && (
                        <a
                          href={`tel:${selectedResource.phone}`}
                          className="flex items-center gap-2 text-sm text-primary hover:underline"
                        >
                          <Phone className="h-4 w-4" />
                          {selectedResource.phone}
                        </a>
                      )}
                      {selectedResource.location && (
                        <div className="flex items-start gap-2 text-sm">
                          <MapPin className="h-4 w-4 mt-0.5 text-muted-foreground" />
                          <span>
                            {selectedResource.location.address && (
                              <>{selectedResource.location.address}, </>
                            )}
                            {selectedResource.location.city}, {selectedResource.location.state}
                          </span>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-sm font-medium">{selectedItem?.resource_title}</p>
                    <p className="text-xs text-muted-foreground">{selectedItem?.organization_name}</p>
                  </div>
                )}

                <Separator />

                {/* Review Reason */}
                {selectedItem?.reason && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-900 dark:bg-amber-900/20">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-5 w-5 mt-0.5 text-amber-600 dark:text-amber-400" />
                      <div>
                        <h4 className="text-sm font-medium text-amber-800 dark:text-amber-300">
                          Review Reason
                        </h4>
                        <p className="mt-1 text-sm text-amber-700 dark:text-amber-200">
                          {selectedItem.reason}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recent Changes */}
                {selectedItem?.changes_summary && selectedItem.changes_summary.length > 0 && (
                  <div>
                    <h4 className="mb-2 text-sm font-medium text-muted-foreground">Recent Changes</h4>
                    <div className="rounded-md bg-muted p-3 text-sm space-y-1">
                      {selectedItem.changes_summary.map((change, i) => (
                        <p key={i}>{change}</p>
                      ))}
                    </div>
                  </div>
                )}

                <Separator />

                {/* Review Form */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">
                      Reviewer Name <span className="text-destructive">*</span>
                    </label>
                    <Input
                      value={reviewer}
                      onChange={(e) => setReviewer(e.target.value)}
                      placeholder="Your name"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Notes (optional)</label>
                    <Input
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Add any notes..."
                      className="mt-1"
                    />
                  </div>
                </div>

                {/* View Resource Link */}
                {selectedItem && (
                  <div className="pt-2">
                    <Link
                      href={`/resources/${selectedItem.resource_id}`}
                      target="_blank"
                      className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                    >
                      View full resource page
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  </div>
                )}
              </div>
            </ScrollArea>

            <SheetFooter className="mt-4 flex gap-2 sm:justify-between">
              <Button variant="outline" onClick={closeSheet}>
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
                  ? 'Approve Resource'
                  : 'Reject Resource'}
              </Button>
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </div>
    </div>
  );
}
