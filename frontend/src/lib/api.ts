/**
 * API client for Vibe4Vets backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Organization {
  id: string;
  name: string;
  website: string | null;
}

export interface Location {
  id: string;
  city: string;
  state: string;
  address: string | null;
}

export interface TrustSignals {
  freshness_score: number;
  reliability_score: number;
  last_verified: string | null;
  source_tier: number | null;
  source_name: string | null;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  summary: string | null;
  eligibility: string | null;
  how_to_apply: string | null;
  categories: string[];
  subcategories: string[];
  tags: string[];
  scope: 'national' | 'state' | 'local';
  states: string[];
  website: string | null;
  phone: string | null;
  hours: string | null;
  languages: string[];
  cost: string | null;
  status: 'active' | 'needs_review' | 'inactive';
  created_at: string;
  updated_at: string;
  organization: Organization;
  location: Location | null;
  trust: TrustSignals;
}

export interface ResourceList {
  resources: Resource[];
  total: number;
  limit: number;
  offset: number;
}

export interface MatchExplanation {
  reason: string;
  field: string | null;
  highlight: string | null;
}

export interface SearchResult {
  resource: Resource;
  rank: number;
  explanations: MatchExplanation[];
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  limit: number;
  offset: number;
}

export interface ResourceCreate {
  title: string;
  description: string;
  organization_name: string;
  summary?: string;
  eligibility?: string;
  how_to_apply?: string;
  categories?: string[];
  subcategories?: string[];
  tags?: string[];
  scope?: 'national' | 'state' | 'local';
  states?: string[];
  website?: string;
  phone?: string;
  hours?: string;
  languages?: string[];
  cost?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
}

export interface ReviewQueueItem {
  id: string;
  resource_id: string;
  resource_title: string;
  organization_name: string;
  reason: string | null;
  status: string;
  created_at: string;
  changes_summary: string[];
}

export interface ReviewQueueResponse {
  items: ReviewQueueItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface DashboardStats {
  total_resources: number;
  pending_reviews: number;
  approved_today: number;
  sources_count: number;
  healthy_sources: number;
}

// Source Health types (from V4V-do6)
export interface ErrorRecord {
  id: string;
  source_id: string;
  source_name: string;
  error_type: string;
  message: string;
  occurred_at: string;
  job_run_id: string | null;
}

export interface SourceHealthDetail {
  source_id: string;
  name: string;
  url: string;
  tier: number;
  source_type: string;
  frequency: string;
  status: 'healthy' | 'degraded' | 'failing';
  resource_count: number;
  resources_by_status: Record<string, number>;
  average_freshness: number;
  last_run: string | null;
  last_success: string | null;
  error_count: number;
  success_rate: number;
  errors: ErrorRecord[];
}

export interface SourceHealthListResponse {
  sources: SourceHealthDetail[];
  total: number;
}

export interface ErrorListResponse {
  errors: ErrorRecord[];
  total: number;
}

// Job Management types (from V4V-lej)
export interface JobInfo {
  name: string;
  description: string;
  scheduled: boolean;
  next_run: string | null;
}

export interface JobsResponse {
  jobs: JobInfo[];
  scheduler_running: boolean;
}

export interface JobHistoryEntry {
  run_id: string;
  job_name: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  message: string;
  stats: Record<string, unknown>;
  error: string | null;
}

export interface JobHistoryResponse {
  history: JobHistoryEntry[];
  total: number;
}

export interface ConnectorInfo {
  name: string;
  source_name: string;
  tier: number;
  description: string;
}

export interface ConnectorsResponse {
  connectors: ConnectorInfo[];
  total: number;
}

export interface JobRunResult {
  run_id: string;
  job_name: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  message: string;
  stats: Record<string, unknown>;
  error: string | null;
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Resources API
export const api = {
  resources: {
    list: (params: {
      category?: string;
      state?: string;
      limit?: number;
      offset?: number;
    } = {}): Promise<ResourceList> => {
      const searchParams = new URLSearchParams();
      if (params.category) searchParams.set('category', params.category);
      if (params.state) searchParams.set('state', params.state);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      const query = searchParams.toString();
      return fetchAPI(`/api/v1/resources${query ? `?${query}` : ''}`);
    },

    get: (id: string): Promise<Resource> => {
      return fetchAPI(`/api/v1/resources/${id}`);
    },

    create: (data: ResourceCreate): Promise<Resource> => {
      return fetchAPI('/api/v1/resources', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    update: (id: string, data: Partial<ResourceCreate>): Promise<Resource> => {
      return fetchAPI(`/api/v1/resources/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },

    delete: (id: string): Promise<void> => {
      return fetchAPI(`/api/v1/resources/${id}`, {
        method: 'DELETE',
      });
    },
  },

  search: {
    query: (params: {
      q: string;
      category?: string;
      state?: string;
      limit?: number;
      offset?: number;
    }): Promise<SearchResponse> => {
      const searchParams = new URLSearchParams();
      searchParams.set('q', params.q);
      if (params.category) searchParams.set('category', params.category);
      if (params.state) searchParams.set('state', params.state);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      return fetchAPI(`/api/v1/search?${searchParams.toString()}`);
    },
  },

  admin: {
    getReviewQueue: (params: {
      status?: string;
      limit?: number;
      offset?: number;
    } = {}): Promise<ReviewQueueResponse> => {
      const searchParams = new URLSearchParams();
      if (params.status) searchParams.set('status', params.status);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      const query = searchParams.toString();
      return fetchAPI(`/api/v1/admin/review-queue${query ? `?${query}` : ''}`);
    },

    reviewResource: (
      reviewId: string,
      action: 'approve' | 'reject',
      reviewer: string,
      notes?: string
    ): Promise<{ success: boolean }> => {
      return fetchAPI(`/api/v1/admin/review/${reviewId}`, {
        method: 'POST',
        body: JSON.stringify({ action, reviewer, notes }),
      });
    },

    getDashboardStats: (): Promise<DashboardStats> => {
      return fetchAPI('/api/v1/admin/dashboard/stats');
    },

// Source Health API (from V4V-do6)
    getSourcesHealth: (): Promise<SourceHealthListResponse> => {
      return fetchAPI('/api/v1/admin/dashboard/sources');
    },

    getSourceHealth: (sourceId: string): Promise<SourceHealthDetail> => {
      return fetchAPI(`/api/v1/admin/dashboard/sources/${sourceId}`);
    },

    getRecentErrors: (limit: number = 20): Promise<ErrorListResponse> => {
      return fetchAPI(`/api/v1/admin/dashboard/errors?limit=${limit}`);
    },

    // Job Management API (from V4V-lej)
    getJobs: (): Promise<JobsResponse> => {
      return fetchAPI('/api/v1/admin/jobs');
    },

    runJob: (
      jobName: string,
      options?: { connector_name?: string; dry_run?: boolean }
    ): Promise<JobRunResult> => {
      return fetchAPI(`/api/v1/admin/jobs/${jobName}/run`, {
        method: 'POST',
        body: JSON.stringify(options || {}),
      });
    },

    getJobHistory: (limit: number = 20): Promise<JobHistoryResponse> => {
      return fetchAPI(`/api/v1/admin/jobs/history?limit=${limit}`);
    },

    getConnectors: (): Promise<ConnectorsResponse> => {
      return fetchAPI('/api/v1/admin/jobs/connectors');
    },
  },
};

export default api;
