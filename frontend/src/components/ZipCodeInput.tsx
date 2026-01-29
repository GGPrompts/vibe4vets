'use client';

import { useState, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { MapPin, X } from 'lucide-react';
import { cn } from '@/lib/utils';

const RADIUS_OPTIONS = [
  { value: '10', label: '10 miles' },
  { value: '25', label: '25 miles' },
  { value: '50', label: '50 miles' },
  { value: '100', label: '100 miles' },
] as const;

interface ZipCodeInputProps {
  zip: string;
  radius: number;
  onZipChange: (zip: string) => void;
  onRadiusChange: (radius: number) => void;
  onClear?: () => void;
  onSubmit?: () => void;
  placeholder?: string;
  showRadiusSelect?: boolean;
  className?: string;
  compact?: boolean;
}

export function ZipCodeInput({
  zip,
  radius,
  onZipChange,
  onRadiusChange,
  onClear,
  onSubmit,
  placeholder = 'ZIP code',
  showRadiusSelect = true,
  className,
  compact = false,
}: ZipCodeInputProps) {
  const [inputValue, setInputValue] = useState(zip);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      // Only allow digits, max 5 characters
      const value = e.target.value.replace(/\D/g, '').slice(0, 5);
      setInputValue(value);
      if (value.length === 5) {
        onZipChange(value);
      } else if (value.length === 0) {
        onZipChange('');
      }
    },
    [onZipChange]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter' && inputValue.length === 5 && onSubmit) {
        onSubmit();
      }
    },
    [inputValue, onSubmit]
  );

  const handleClear = useCallback(() => {
    setInputValue('');
    onZipChange('');
    onClear?.();
  }, [onZipChange, onClear]);

  const handleRadiusChange = useCallback(
    (value: string) => {
      onRadiusChange(parseInt(value, 10));
    },
    [onRadiusChange]
  );

  return (
    <div className={cn('flex gap-2', className)}>
      <div className="relative flex-1">
        <MapPin className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            'pl-8 pr-8 bg-muted/50',
            compact ? 'h-9 text-sm' : 'h-10'
          )}
        />
        {inputValue && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="absolute right-1 top-1/2 h-6 w-6 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>

      {showRadiusSelect && (
        <Select value={String(radius)} onValueChange={handleRadiusChange}>
          <SelectTrigger className={cn('w-[110px]', compact ? 'h-9 text-sm' : 'h-10')}>
            <SelectValue placeholder="Radius" />
          </SelectTrigger>
          <SelectContent>
            {RADIUS_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
    </div>
  );
}

export { RADIUS_OPTIONS };
