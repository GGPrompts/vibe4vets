'use client';

import { useState } from 'react';
import { CheckCircle2, Lightbulb, Plus } from 'lucide-react';
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import api, { type ResourceSuggest } from '@/lib/api';
import { cn } from '@/lib/utils';

// Categories available for suggestions
const categories = [
  { value: 'employment', label: 'Employment' },
  { value: 'training', label: 'Training & Education' },
  { value: 'housing', label: 'Housing' },
  { value: 'legal', label: 'Legal' },
  { value: 'food', label: 'Food Assistance' },
  { value: 'benefits', label: 'Benefits Consultation' },
  { value: 'mentalHealth', label: 'Mental Health' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'financial', label: 'Financial' },
  { value: 'supportServices', label: 'Support Services' },
  { value: 'education', label: 'Education' },
  { value: 'family', label: 'Family' },
];

// US states for dropdown
const states = [
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DE', label: 'Delaware' },
  { value: 'DC', label: 'District of Columbia' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'PR', label: 'Puerto Rico' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' },
];

interface SuggestResourceModalProps {
  trigger?: React.ReactNode;
  className?: string;
}

export function SuggestResourceModal({
  trigger,
  className,
}: SuggestResourceModalProps) {
  const [open, setOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [website, setWebsite] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [submitterEmail, setSubmitterEmail] = useState('');
  const [notes, setNotes] = useState('');

  const resetForm = () => {
    setName('');
    setDescription('');
    setCategory('');
    setWebsite('');
    setPhone('');
    setAddress('');
    setCity('');
    setState('');
    setZipCode('');
    setSubmitterEmail('');
    setNotes('');
    setError(null);
    setIsSuccess(false);
  };

  const handleClose = () => {
    setOpen(false);
    // Reset form after close animation
    setTimeout(resetForm, 200);
  };

  const validateForm = (): string | null => {
    if (!name.trim() || name.trim().length < 3) {
      return 'Please enter a resource name (at least 3 characters)';
    }
    if (!description.trim() || description.trim().length < 20) {
      return 'Please provide a description (at least 20 characters)';
    }
    if (!category) {
      return 'Please select a category';
    }
    if (!website && !phone) {
      return 'Please provide at least a website or phone number';
    }
    if (website && !website.match(/^https?:\/\/.+/)) {
      return 'Please enter a valid website URL (starting with http:// or https://)';
    }
    if (submitterEmail && !submitterEmail.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      return 'Please enter a valid email address';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const data: ResourceSuggest = {
        name: name.trim(),
        description: description.trim(),
        category,
        website: website.trim() || undefined,
        phone: phone.trim() || undefined,
        address: address.trim() || undefined,
        city: city.trim() || undefined,
        state: state || undefined,
        zip_code: zipCode.trim() || undefined,
        submitter_email: submitterEmail.trim() || undefined,
        notes: notes.trim() || undefined,
      };

      await api.resources.suggest(data);
      setIsSuccess(true);
    } catch (err) {
      if (err instanceof Error) {
        // Handle rate limit error specifically
        if (err.message.includes('Rate limit')) {
          setError('You have submitted too many suggestions. Please try again in an hour.');
        } else {
          setError(err.message);
        }
      } else {
        setError('Failed to submit suggestion. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const defaultTrigger = (
    <Button
      variant="ghost"
      size="sm"
      className={cn(
        "gap-1.5 text-white/80 hover:text-[hsl(var(--v4v-gold))] hover:bg-white/10",
        className
      )}
    >
      <Plus className="h-4 w-4" />
      <span className="hidden sm:inline">Suggest Resource</span>
    </Button>
  );

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto z-[200]" overlayClassName="z-[150]">
        {isSuccess ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                Thank you!
              </DialogTitle>
              <DialogDescription>
                Your resource suggestion has been submitted. Our team will review it
                and add it to the directory if it meets our criteria. This usually
                takes 1-3 business days.
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
                <Lightbulb className="h-5 w-5 text-amber-500" />
                Suggest a Resource
              </DialogTitle>
              <DialogDescription>
                Know a Veteran resource that&apos;s not in our directory? Help us help
                Veterans by suggesting it below. No account required.
              </DialogDescription>
            </DialogHeader>

            <div className="mt-4 space-y-4">
              {/* Resource Name */}
              <div className="space-y-2">
                <Label htmlFor="name">
                  Resource Name <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="name"
                  placeholder="e.g., Veterans Community Center Job Fair"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={255}
                />
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label htmlFor="category">
                  Category <span className="text-destructive">*</span>
                </Label>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger id="category">
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent className="z-[250]">
                    {categories.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">
                  Description <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this resource offers to Veterans..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  maxLength={2000}
                />
                <p className="text-xs text-muted-foreground">
                  Minimum 20 characters ({description.length}/2000)
                </p>
              </div>

              {/* Contact Info */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">
                  Contact Info <span className="text-muted-foreground">(at least one required)</span>
                </Label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="website" className="sr-only">Website</Label>
                    <Input
                      id="website"
                      placeholder="Website URL"
                      value={website}
                      onChange={(e) => setWebsite(e.target.value)}
                      type="url"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone" className="sr-only">Phone</Label>
                    <Input
                      id="phone"
                      placeholder="Phone number"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      type="tel"
                    />
                  </div>
                </div>
              </div>

              {/* Location */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">
                  Location <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  id="address"
                  placeholder="Street address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="mb-2"
                />
                <div className="grid grid-cols-3 gap-2">
                  <Input
                    id="city"
                    placeholder="City"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                  />
                  <Select value={state} onValueChange={setState}>
                    <SelectTrigger id="state">
                      <SelectValue placeholder="State" />
                    </SelectTrigger>
                    <SelectContent className="z-[250] max-h-[200px]">
                      {states.map((st) => (
                        <SelectItem key={st.value} value={st.value}>
                          {st.value}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    id="zipCode"
                    placeholder="ZIP"
                    value={zipCode}
                    onChange={(e) => setZipCode(e.target.value)}
                    maxLength={10}
                  />
                </div>
              </div>

              {/* Additional Notes */}
              <div className="space-y-2">
                <Label htmlFor="notes">
                  Additional Notes <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Textarea
                  id="notes"
                  placeholder="Any other helpful info (hours, eligibility requirements, etc.)"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                  maxLength={1000}
                />
              </div>

              {/* Submitter Email */}
              <div className="space-y-2">
                <Label htmlFor="email">
                  Your Email <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="For follow-up questions only"
                  value={submitterEmail}
                  onChange={(e) => setSubmitterEmail(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  We&apos;ll only contact you if we need clarification
                </p>
              </div>

              {/* Error message */}
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
                {isSubmitting ? 'Submitting...' : 'Submit Suggestion'}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
