/**
 * API client for Vibe4Vets backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Organization {
  id: string;
  name: string;
  website: string | null;
}

export interface EligibilityInfo {
  age_min: number | null;
  age_max: number | null;
  household_size_min: number | null;
  household_size_max: number | null;
  income_limit_type: string | null;
  income_limit_value: number | null;
  income_limit_ami_percent: number | null;
  housing_status_required: string[];
  active_duty_required: boolean | null;
  discharge_required: string | null;
  veteran_status_required: boolean;
  docs_required: string[];
  waitlist_status: string | null;
}

export interface IntakeInfo {
  phone: string | null;
  url: string | null;
  hours: string | null;
  notes: string | null;
}

export interface VerificationInfo {
  last_verified_at: string | null;
  verified_by: string | null;
  notes: string | null;
}

export interface Location {
  id: string;
  city: string;
  state: string;
  address: string | null;
  service_area?: string[];
  eligibility?: EligibilityInfo | null;
  intake?: IntakeInfo | null;
  verification?: VerificationInfo | null;
}

export interface TrustSignals {
  freshness_score: number;
  reliability_score: number;
  last_verified: string | null;
  source_tier: number | null;
  source_name: string | null;
}

export interface Program {
  id: string;
  name: string;
  program_type: string;
  description: string | null;
  services_offered: string[];
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  summary: string | null;
  eligibility: string | null;
  how_to_apply: string | null;
  program_id: string | null;
  program: Program | null;
  categories: string[];
  subcategories: string[];
  tags: string[];
  scope: 'national' | 'state' | 'local';
  states: string[];
  website: string | null;
  logo_url: string | null;
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

// Nearby search types
export interface ResourceNearbyResult {
  resource: Resource;
  distance_miles: number;
}

export interface ResourceNearbyList {
  resources: ResourceNearbyResult[];
  total: number;
  zip_code: string;
  radius_miles: number;
  center_lat: number;
  center_lng: number;
}

export interface MatchExplanation {
  reason: string;
  field: string | null;
  highlight: string | null;
}

export interface MatchReason {
  type: string;
  label: string;
}

export interface SearchResult {
  resource: Resource;
  rank: number;
  explanations: MatchExplanation[];
  match_reasons?: MatchReason[];
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  limit: number;
  offset: number;
}

export interface EligibilitySearchParams {
  q?: string;
  category?: string;
  states?: string;
  counties?: string;
  age_bracket?: 'under_55' | '55_61' | '62_plus' | '65_plus';
  household_size?: number;
  income_bracket?: 'low' | 'moderate' | 'any';
  housing_status?: 'homeless' | 'at_risk' | 'stably_housed';
  veteran_status?: boolean;
  discharge?: 'honorable' | 'other_than_dis' | 'unknown';
  has_disability?: boolean;
  tags?: string;
  limit?: number;
  offset?: number;
}

// Taxonomy types for tag filtering
export interface TagInfo {
  id: string;
  name: string;
}

export interface TagGroup {
  group: string;
  tags: TagInfo[];
}

export interface CategoryTags {
  category_id: string;
  category_name: string;
  groups: TagGroup[];
}

export interface TaxonomyResponse {
  categories: CategoryTags[];
}

export interface CategoryTagsResponse {
  category_id: string;
  category_name: string;
  groups: TagGroup[];
  flat_tags: TagInfo[];
}

export interface CategoryInfo {
  id: string;
  name: string;
  description: string;
}

export interface CategoriesResponse {
  categories: CategoryInfo[];
}

export interface EligibilitySearchResponse {
  query: string | null;
  results: SearchResult[];
  total: number;
  limit: number;
  offset: number;
  filters_applied: string[];
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
  display_name: string;
  url: string;
  tier: number;
  frequency: string;
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

// Feedback types (from V4V-1ca)
export type FeedbackIssueType =
  | 'phone'
  | 'address'
  | 'hours'
  | 'website'
  | 'closed'
  | 'eligibility'
  | 'other';

export type FeedbackStatus = 'pending' | 'reviewed' | 'applied' | 'dismissed';

export interface FeedbackCreate {
  resource_id: string;
  issue_type: FeedbackIssueType;
  description: string;
  suggested_correction?: string;
  source_of_correction?: string;
}

export interface FeedbackResponse {
  id: string;
  resource_id: string;
  issue_type: FeedbackIssueType;
  description: string;
  suggested_correction: string | null;
  source_of_correction: string | null;
  status: FeedbackStatus;
  created_at: string;
}

export interface FeedbackAdminResponse {
  id: string;
  resource_id: string;
  resource_title: string;
  organization_name: string;
  issue_type: FeedbackIssueType;
  description: string;
  suggested_correction: string | null;
  source_of_correction: string | null;
  status: FeedbackStatus;
  reviewer: string | null;
  reviewed_at: string | null;
  reviewer_notes: string | null;
  created_at: string;
}

export interface FeedbackListResponse {
  items: FeedbackAdminResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface FeedbackStats {
  pending: number;
  reviewed: number;
  applied: number;
  dismissed: number;
  total: number;
}

// Analytics types (from V4V-u87)
export type AnalyticsEventType =
  | 'search'
  | 'search_filter'
  | 'resource_view'
  | 'wizard_start'
  | 'wizard_step'
  | 'wizard_complete'
  | 'chat_start'
  | 'chat_message'
  | 'page_view';

export interface AnalyticsEventCreate {
  event_type: AnalyticsEventType;
  event_name: string;
  category?: string;
  state?: string;
  resource_id?: string;
  search_query?: string;
  wizard_step?: number;
  page_path?: string;
}

export interface AnalyticsEventResponse {
  id: string;
  event_type: AnalyticsEventType;
  event_name: string;
  created_at: string;
}

export interface AnalyticsSummaryStats {
  period_days: number;
  total_searches: number;
  total_resource_views: number;
  wizard_starts: number;
  wizard_completions: number;
  chat_sessions: number;
  chat_messages: number;
  filter_usage: number;
}

export interface PopularSearchItem {
  query: string;
  count: number;
}

export interface PopularCategoryItem {
  category: string;
  count: number;
}

export interface PopularStateItem {
  state: string;
  count: number;
}

export interface PopularResourceItem {
  resource_id: string;
  resource_title: string | null;
  count: number;
}

export interface WizardFunnelStats {
  starts: number;
  completions: number;
  completion_rate: number;
}

export interface DailyTrendItem {
  date: string;
  search?: number;
  resource_view?: number;
  wizard_start?: number;
  wizard_complete?: number;
  chat_start?: number;
  chat_message?: number;
}

export interface AnalyticsDashboardResponse {
  summary: AnalyticsSummaryStats;
  popular_searches: PopularSearchItem[];
  popular_categories: PopularCategoryItem[];
  popular_states: PopularStateItem[];
  popular_resources: PopularResourceItem[];
  wizard_funnel: WizardFunnelStats;
  daily_trends: DailyTrendItem[];
}

// AI Stats types (for About page transparency section)
// Note: ConnectorInfo is defined above, reusing it here

export interface AIStats {
  total_resources: number;
  resources_verified: number;
  resources_by_category: Record<string, number>;
  total_sources: number;
  connectors_active: ConnectorInfo[];
  last_refresh: string | null;
  average_trust_score: number;
  scheduler_status: string;
  jobs_completed_today: number;
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  let response: Response;

  // Add admin key header for admin endpoints
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (endpoint.includes('/admin')) {
    const adminKey = process.env.NEXT_PUBLIC_ADMIN_API_KEY;
    if (adminKey) {
      headers['X-Admin-Key'] = adminKey;
    }
  }

  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });
  } catch (err) {
    // Network error or CORS - provide helpful message
    const message = err instanceof Error ? err.message : 'Network error';
    throw new Error(`Unable to connect to server: ${message}. Is the backend running?`);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Resource count type
export interface ResourceCount {
  count: number;
}

// Resources API
export const api = {
  resources: {
    list: (params: {
      category?: string;
      state?: string;
      // Multi-value filters (comma-separated strings)
      categories?: string;
      states?: string;
      scope?: string;
      limit?: number;
      offset?: number;
    } = {}): Promise<ResourceList> => {
      const searchParams = new URLSearchParams();
      // Prefer multi-value params over deprecated single-value
      if (params.categories) searchParams.set('categories', params.categories);
      else if (params.category) searchParams.set('category', params.category);
      if (params.states) searchParams.set('states', params.states);
      else if (params.state) searchParams.set('state', params.state);
      if (params.scope) searchParams.set('scope', params.scope);
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

    count: (params: {
      categories?: string;
      states?: string;
      scope?: string;
    } = {}): Promise<ResourceCount> => {
      const searchParams = new URLSearchParams();
      if (params.categories) searchParams.set('categories', params.categories);
      if (params.states) searchParams.set('states', params.states);
      if (params.scope) searchParams.set('scope', params.scope);

      const query = searchParams.toString();
      return fetchAPI(`/api/v1/resources/count${query ? `?${query}` : ''}`);
    },

    nearby: (params: {
      zip: string;
      radius?: number;
      categories?: string;
      scope?: string;
      tags?: string;
      limit?: number;
      offset?: number;
    }): Promise<ResourceNearbyList> => {
      const searchParams = new URLSearchParams();
      searchParams.set('zip', params.zip);
      if (params.radius) searchParams.set('radius', String(params.radius));
      if (params.categories) searchParams.set('categories', params.categories);
      if (params.scope && params.scope !== 'all') searchParams.set('scope', params.scope);
      if (params.tags) searchParams.set('tags', params.tags);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      return fetchAPI(`/api/v1/resources/nearby?${searchParams.toString()}`);
    },
  },

  search: {
    query: (params: {
      q: string;
      category?: string;
      state?: string;
      // Multi-value filters (comma-separated strings)
      categories?: string;
      states?: string;
      scope?: string;
      tags?: string;
      limit?: number;
      offset?: number;
    }): Promise<SearchResponse> => {
      const searchParams = new URLSearchParams();
      searchParams.set('q', params.q);
      // Prefer multi-value params over deprecated single-value
      if (params.categories) searchParams.set('categories', params.categories);
      else if (params.category) searchParams.set('category', params.category);
      if (params.states) searchParams.set('states', params.states);
      else if (params.state) searchParams.set('state', params.state);
      if (params.scope && params.scope !== 'all') searchParams.set('scope', params.scope);
      if (params.tags) searchParams.set('tags', params.tags);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      return fetchAPI(`/api/v1/search?${searchParams.toString()}`);
    },

    eligibility: (params: EligibilitySearchParams): Promise<EligibilitySearchResponse> => {
      const searchParams = new URLSearchParams();
      if (params.q) searchParams.set('q', params.q);
      if (params.category) searchParams.set('category', params.category);
      if (params.states) searchParams.set('states', params.states);
      if (params.counties) searchParams.set('counties', params.counties);
      if (params.age_bracket) searchParams.set('age_bracket', params.age_bracket);
      if (params.household_size) searchParams.set('household_size', String(params.household_size));
      if (params.income_bracket) searchParams.set('income_bracket', params.income_bracket);
      if (params.housing_status) searchParams.set('housing_status', params.housing_status);
      if (params.veteran_status !== undefined) searchParams.set('veteran_status', String(params.veteran_status));
      if (params.discharge) searchParams.set('discharge', params.discharge);
      if (params.has_disability !== undefined) searchParams.set('has_disability', String(params.has_disability));
      if (params.tags) searchParams.set('tags', params.tags);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      return fetchAPI(`/api/v1/search/eligibility?${searchParams.toString()}`);
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

    // Feedback Admin API (from V4V-1ca)
    getFeedback: (params: {
      status?: FeedbackStatus;
      limit?: number;
      offset?: number;
    } = {}): Promise<FeedbackListResponse> => {
      const searchParams = new URLSearchParams();
      if (params.status) searchParams.set('status', params.status);
      if (params.limit) searchParams.set('limit', String(params.limit));
      if (params.offset) searchParams.set('offset', String(params.offset));

      const query = searchParams.toString();
      return fetchAPI(`/api/v1/feedback/admin${query ? `?${query}` : ''}`);
    },

    reviewFeedback: (
      feedbackId: string,
      status: FeedbackStatus,
      reviewer: string,
      reviewer_notes?: string
    ): Promise<FeedbackAdminResponse> => {
      return fetchAPI(`/api/v1/feedback/admin/${feedbackId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status, reviewer, reviewer_notes }),
      });
    },

    getFeedbackStats: (): Promise<FeedbackStats> => {
      return fetchAPI('/api/v1/feedback/admin/stats/summary');
    },
  },

  // Public Feedback API (no auth required)
  feedback: {
    submit: (data: FeedbackCreate): Promise<FeedbackResponse> => {
      return fetchAPI('/api/v1/feedback', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  },

  // Analytics API (from V4V-u87)
  analytics: {
    // Public endpoint - record anonymous event
    trackEvent: (data: AnalyticsEventCreate): Promise<AnalyticsEventResponse> => {
      return fetchAPI('/api/v1/analytics/events', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    // Admin endpoints
    getDashboard: (days: number = 30): Promise<AnalyticsDashboardResponse> => {
      return fetchAPI(`/api/v1/analytics/admin/dashboard?days=${days}`);
    },

    getSummary: (days: number = 30): Promise<AnalyticsSummaryStats> => {
      return fetchAPI(`/api/v1/analytics/admin/summary?days=${days}`);
    },

    getPopularSearches: (
      days: number = 30,
      limit: number = 10
    ): Promise<PopularSearchItem[]> => {
      return fetchAPI(
        `/api/v1/analytics/admin/popular-searches?days=${days}&limit=${limit}`
      );
    },

    getPopularCategories: (
      days: number = 30,
      limit: number = 10
    ): Promise<PopularCategoryItem[]> => {
      return fetchAPI(
        `/api/v1/analytics/admin/popular-categories?days=${days}&limit=${limit}`
      );
    },

    getPopularStates: (
      days: number = 30,
      limit: number = 10
    ): Promise<PopularStateItem[]> => {
      return fetchAPI(
        `/api/v1/analytics/admin/popular-states?days=${days}&limit=${limit}`
      );
    },

    getPopularResources: (
      days: number = 30,
      limit: number = 10
    ): Promise<PopularResourceItem[]> => {
      return fetchAPI(
        `/api/v1/analytics/admin/popular-resources?days=${days}&limit=${limit}`
      );
    },

    getWizardFunnel: (days: number = 30): Promise<WizardFunnelStats> => {
      return fetchAPI(`/api/v1/analytics/admin/wizard-funnel?days=${days}`);
    },

    getDailyTrends: (days: number = 30): Promise<DailyTrendItem[]> => {
      return fetchAPI(`/api/v1/analytics/admin/daily-trends?days=${days}`);
    },
  },

  // Taxonomy API (for filter UIs)
  taxonomy: {
    getTags: (): Promise<TaxonomyResponse> => {
      return fetchAPI('/api/v1/taxonomy/tags');
    },

    getCategoryTags: (categoryId: string): Promise<CategoryTagsResponse> => {
      return fetchAPI(`/api/v1/taxonomy/tags/${categoryId}`);
    },

    getCategories: (): Promise<CategoriesResponse> => {
      return fetchAPI('/api/v1/taxonomy/categories');
    },
  },

  // AI Stats API (for About page transparency)
  stats: {
    getAIStats: (): Promise<AIStats> => {
      return fetchAPI('/api/v1/stats/ai');
    },
  },
};

export default api;
