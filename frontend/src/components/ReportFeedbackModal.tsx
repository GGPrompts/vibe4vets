'use client';

import { useState } from 'react';
import { AlertTriangle, CheckCircle2, Flag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import api, { type FeedbackIssueType } from '@/lib/api';

interface ReportFeedbackModalProps {
  resourceId: string;
  resourceTitle: string;
}

const issueTypes: { value: FeedbackIssueType; label: string }[] = [
  { value: 'phone', label: 'Phone number is wrong' },
  { value: 'address', label: 'Address is wrong' },
  { value: 'hours', label: 'Hours are wrong' },
  { value: 'website', label: 'Website is wrong or broken' },
  { value: 'closed', label: 'This resource is closed' },
  { value: 'eligibility', label: 'Eligibility info is wrong' },
  { value: 'other', label: 'Other issue' },
];

export function ReportFeedbackModal({
  resourceId,
  resourceTitle,
}: ReportFeedbackModalProps) {
  const [open, setOpen] = useState(false);
  const [issueType, setIssueType] = useState<FeedbackIssueType>('other');
  const [description, setDescription] = useState('');
  const [suggestedCorrection, setSuggestedCorrection] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (description.length < 10) {
      setError('Please provide more details (at least 10 characters)');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await api.feedback.submit({
        resource_id: resourceId,
        issue_type: issueType,
        description,
        suggested_correction: suggestedCorrection || undefined,
      });
      setIsSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    // Reset form after close animation
    setTimeout(() => {
      setIssueType('other');
      setDescription('');
      setSuggestedCorrection('');
      setIsSuccess(false);
      setError(null);
    }, 200);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          type="button"
        >
          <Flag className="h-4 w-4" />
          Report an issue
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        {isSuccess ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                Thank you!
              </DialogTitle>
              <DialogDescription>
                Your feedback has been submitted. Our team will review it and update
                the resource information if needed.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button onClick={handleClose}>Close</Button>
            </DialogFooter>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                Report an Issue
              </DialogTitle>
              <DialogDescription>
                Help us keep resource information accurate. No account required.
              </DialogDescription>
            </DialogHeader>

            <div className="mt-4 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="resource">Resource</Label>
                <p className="text-sm font-medium text-muted-foreground">
                  {resourceTitle}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="issue-type">What&apos;s wrong?</Label>
                <Select
                  value={issueType}
                  onValueChange={(value) => setIssueType(value as FeedbackIssueType)}
                >
                  <SelectTrigger id="issue-type" className="w-full">
                    <SelectValue placeholder="Select an issue type" />
                  </SelectTrigger>
                  <SelectContent>
                    {issueTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">
                  Description <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="description"
                  placeholder="Please describe what's incorrect..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
                <p className="text-xs text-muted-foreground">
                  Minimum 10 characters
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="suggested-correction">
                  Correct information (optional)
                </Label>
                <Textarea
                  id="suggested-correction"
                  placeholder="If you know the correct info, please share it..."
                  value={suggestedCorrection}
                  onChange={(e) => setSuggestedCorrection(e.target.value)}
                  rows={2}
                />
              </div>

              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
            </div>

            <DialogFooter className="mt-6">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Submitting...' : 'Submit Report'}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
