import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export function ResourceCardSkeleton() {
  return (
    <Card className="relative h-full overflow-hidden bg-white dark:bg-card">
      {/* Accent bar placeholder */}
      <Skeleton className="absolute left-0 top-0 h-1 w-full rounded-none" />

      <CardHeader className="pb-3 pt-5">
        {/* Trust indicator row */}
        <div className="mb-2 flex items-center justify-end gap-2">
          <Skeleton className="h-4 w-4 rounded" />
          <Skeleton className="h-2.5 w-20 rounded-full" />
          <Skeleton className="h-3 w-8" />
        </div>

        {/* Title with icon */}
        <div className="flex items-start gap-3">
          {/* Icon box */}
          <Skeleton className="h-9 w-9 shrink-0 rounded-lg" />
          <div className="min-w-0 flex-1 space-y-2">
            {/* Title - two lines */}
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-5 w-3/4" />
            {/* Organization name */}
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Description - two lines */}
        <div className="mb-4 space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>

        {/* Badge placeholders */}
        <div className="mb-3 flex flex-wrap gap-2">
          <Skeleton className="h-6 w-24 rounded-full" />
          <Skeleton className="h-6 w-20 rounded-full" />
          <Skeleton className="h-6 w-28 rounded-full" />
        </div>
      </CardContent>
    </Card>
  );
}
