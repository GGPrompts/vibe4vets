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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { MapPin, X, Locate, Loader2 } from 'lucide-react';
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
  /** Called when user clicks "Use my location" and geolocation succeeds */
  onGeolocation?: (lat: number, lng: number) => void;
  placeholder?: string;
  showRadiusSelect?: boolean;
  /** Show the "Use my location" button */
  showGeolocation?: boolean;
  className?: string;
  compact?: boolean;
  /** Whether currently using geolocation (shows "Using location" indicator) */
  isUsingGeolocation?: boolean;
}

export function ZipCodeInput({
  zip,
  radius,
  onZipChange,
  onRadiusChange,
  onClear,
  onSubmit,
  onGeolocation,
  placeholder = 'ZIP code',
  showRadiusSelect = true,
  showGeolocation = false,
  className,
  compact = false,
  isUsingGeolocation = false,
}: ZipCodeInputProps) {
  const [inputValue, setInputValue] = useState(zip);
  const [isLocating, setIsLocating] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      // Only allow digits, max 5 characters
      const value = e.target.value.replace(/\D/g, '').slice(0, 5);
      setInputValue(value);
      setLocationError(null); // Clear any location error when typing
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
    setLocationError(null);
    onZipChange('');
    onClear?.();
  }, [onZipChange, onClear]);

  const handleRadiusChange = useCallback(
    (value: string) => {
      onRadiusChange(parseInt(value, 10));
    },
    [onRadiusChange]
  );

  const handleGeolocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation not supported by your browser');
      return;
    }

    setIsLocating(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsLocating(false);
        const { latitude, longitude } = position.coords;
        // Clear zip input when using geolocation
        setInputValue('');
        onGeolocation?.(latitude, longitude);
      },
      (error) => {
        setIsLocating(false);
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setLocationError('Location access denied. Enter a ZIP code instead.');
            break;
          case error.POSITION_UNAVAILABLE:
            setLocationError('Location unavailable. Enter a ZIP code instead.');
            break;
          case error.TIMEOUT:
            setLocationError('Location request timed out. Try again or enter a ZIP code.');
            break;
          default:
            setLocationError('Unable to get location. Enter a ZIP code instead.');
        }
      },
      {
        enableHighAccuracy: false, // Faster, good enough for city-level
        timeout: 10000, // 10 second timeout
        maximumAge: 300000, // Accept cached position up to 5 minutes old
      }
    );
  }, [onGeolocation]);

  return (
    <div className={cn('space-y-2', className)}>
      <div className={cn('flex gap-2', compact ? 'flex-col' : '')}>
        <div className="relative flex-1 min-w-0">
          <MapPin className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={isUsingGeolocation ? 'Using location...' : placeholder}
            disabled={isUsingGeolocation}
            className={cn(
              'pl-8 pr-8 bg-muted/50',
              compact ? 'h-9 text-sm' : 'h-10',
              isUsingGeolocation && 'text-muted-foreground'
            )}
          />
          {(inputValue || isUsingGeolocation) && (
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
            <SelectTrigger className={cn(compact ? 'w-full h-9 text-sm' : 'w-[110px] h-10')}>
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

      {/* Geolocation button */}
      {showGeolocation && onGeolocation && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size={compact ? 'sm' : 'default'}
                onClick={handleGeolocation}
                disabled={isLocating}
                className={cn(
                  'w-full gap-2',
                  compact && 'h-8 text-xs',
                  isUsingGeolocation && 'border-[hsl(var(--v4v-gold))] bg-[hsl(var(--v4v-gold)/0.1)]'
                )}
              >
                {isLocating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Getting location...
                  </>
                ) : isUsingGeolocation ? (
                  <>
                    <Locate className="h-4 w-4 text-[hsl(var(--v4v-gold))]" />
                    Using my location
                  </>
                ) : (
                  <>
                    <Locate className="h-4 w-4" />
                    Use my location
                  </>
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xs">Find resources near your current location</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      {/* Error message */}
      {locationError && (
        <p className="text-xs text-destructive">{locationError}</p>
      )}
    </div>
  );
}

export { RADIUS_OPTIONS };
