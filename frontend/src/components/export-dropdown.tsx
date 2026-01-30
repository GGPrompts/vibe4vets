'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Download, FileSpreadsheet, FileText, Mail, Loader2, Check } from 'lucide-react';
import type { Resource } from '@/lib/api';
import { useAnalytics } from '@/lib/useAnalytics';

interface ExportDropdownProps {
  resources: Resource[];
}

export function ExportDropdown({ resources }: ExportDropdownProps) {
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const { trackExport } = useAnalytics();

  const exportToExcel = async () => {
    // Dynamic import to keep bundle size down
    const XLSX = await import('xlsx');

    // Prepare data for Excel
    const data = resources.map((r) => ({
      Title: r.title,
      Organization: r.organization.name,
      Phone: r.phone || '',
      Website: r.website || '',
      Category: r.categories.join(', '),
      'State(s)': r.scope === 'national' ? 'Nationwide' : r.states.join(', '),
      Description: r.summary || r.description,
      'How to Apply': r.how_to_apply || '',
      Eligibility: r.eligibility || '',
    }));

    // Create workbook and worksheet
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Saved Resources');

    // Auto-fit column widths
    const colWidths = Object.keys(data[0] || {}).map((key) => ({
      wch: Math.max(
        key.length,
        ...data.map((row) => String(row[key as keyof typeof row] || '').length)
      ),
    }));
    ws['!cols'] = colWidths.map((w) => ({ wch: Math.min(w.wch, 50) }));

    // Download
    XLSX.writeFile(wb, 'vetrd-saved-resources.xlsx');
    trackExport('excel', resources.length);
  };

  const exportToPDF = async () => {
    // Dynamic import to keep bundle size down
    const jsPDFModule = await import('jspdf');
    const jsPDF = jsPDFModule.default;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 20;
    const contentWidth = pageWidth - margin * 2;
    let y = 20;

    // Title
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('My Saved Resources', margin, y);
    y += 10;

    // Subtitle
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100);
    doc.text(`Exported from VetRD on ${new Date().toLocaleDateString()}`, margin, y);
    doc.setTextColor(0);
    y += 15;

    // Resources
    resources.forEach((resource, index) => {
      // Check if we need a new page
      if (y > 260) {
        doc.addPage();
        y = 20;
      }

      // Resource number and title
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      const title = `${index + 1}. ${resource.title}`;
      const titleLines = doc.splitTextToSize(title, contentWidth);
      doc.text(titleLines, margin, y);
      y += titleLines.length * 5 + 2;

      // Organization
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(resource.organization.name, margin, y);
      y += 5;

      // Contact info
      const contactParts: string[] = [];
      if (resource.phone) contactParts.push(`Phone: ${resource.phone}`);
      if (resource.website) contactParts.push(`Website: ${resource.website}`);
      if (contactParts.length > 0) {
        doc.text(contactParts.join(' | '), margin, y);
        y += 5;
      }

      // Categories and location
      const categoryText = `Categories: ${resource.categories.join(', ')}`;
      const locationText = resource.scope === 'national'
        ? 'Coverage: Nationwide'
        : `States: ${resource.states.join(', ')}`;
      doc.text(`${categoryText} | ${locationText}`, margin, y);
      y += 5;

      // Description (truncated)
      if (resource.summary || resource.description) {
        doc.setTextColor(80);
        const desc = resource.summary || resource.description;
        const descLines = doc.splitTextToSize(desc.slice(0, 200) + (desc.length > 200 ? '...' : ''), contentWidth);
        doc.text(descLines, margin, y);
        y += descLines.length * 4 + 3;
        doc.setTextColor(0);
      }

      // Separator line
      doc.setDrawColor(200);
      doc.line(margin, y, pageWidth - margin, y);
      y += 10;
    });

    // Footer - use type assertion for method not in types
    const docAny = doc as unknown as { getNumberOfPages: () => number; setPage: (n: number) => void };
    const pageCount = docAny.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      docAny.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(
        `Page ${i} of ${pageCount} | Generated by VetRD`,
        pageWidth / 2,
        doc.internal.pageSize.getHeight() - 10,
        { align: 'center' }
      );
    }

    // Download
    doc.save('vetrd-saved-resources.pdf');
    trackExport('pdf', resources.length);
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSending(true);
    setEmailError(null);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE}/api/v1/email-resources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          resource_ids: resources.map((r) => r.id),
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to send email' }));
        throw new Error(error.detail || 'Failed to send email');
      }

      setEmailSent(true);
      trackExport('email', resources.length);
      setTimeout(() => {
        setEmailDialogOpen(false);
        setEmailSent(false);
        setEmail('');
      }, 2000);
    } catch (err) {
      setEmailError(err instanceof Error ? err.message : 'Failed to send email');
    } finally {
      setIsSending(false);
    }
  };

  if (resources.length === 0) {
    return null;
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={exportToExcel}>
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            Download as Excel
          </DropdownMenuItem>
          <DropdownMenuItem onClick={exportToPDF}>
            <FileText className="mr-2 h-4 w-4" />
            Download as PDF
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => setEmailDialogOpen(true)}>
            <Mail className="mr-2 h-4 w-4" />
            Email to myself
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Email Dialog */}
      <Dialog open={emailDialogOpen} onOpenChange={setEmailDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Email saved resources</DialogTitle>
            <DialogDescription>
              We&apos;ll send a formatted list of your {resources.length} saved resource{resources.length !== 1 ? 's' : ''} to your email.
            </DialogDescription>
          </DialogHeader>

          {emailSent ? (
            <div className="flex flex-col items-center py-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                <Check className="h-6 w-6 text-green-600" />
              </div>
              <p className="text-center font-medium">Email sent!</p>
              <p className="text-center text-sm text-muted-foreground">Check your inbox at {email}</p>
            </div>
          ) : (
            <form onSubmit={handleEmailSubmit}>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={isSending}
                  />
                </div>
                {emailError && (
                  <p className="text-sm text-destructive">{emailError}</p>
                )}
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setEmailDialogOpen(false)} disabled={isSending}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isSending || !email}>
                  {isSending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Send Email
                    </>
                  )}
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
