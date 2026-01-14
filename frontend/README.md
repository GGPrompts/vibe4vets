# Vibe4Vets Frontend

Next.js 15 + React 18 + TypeScript + Tailwind + shadcn/ui frontend for the veteran resource directory.

## Setup

```bash
npm install
```

Create `.env.local` for local development:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

Runs on http://localhost:3000 with Turbopack. Requires the backend running at `NEXT_PUBLIC_API_URL`.

## Build

```bash
npm run build
npm run start
```

For production, set `NEXT_PUBLIC_API_URL` to your deployed backend URL.

## Project Structure

```
src/
├── app/                    # App Router pages
│   ├── page.tsx            # Landing page with search
│   ├── search/page.tsx     # Search results
│   ├── resources/[id]/     # Resource detail
│   └── admin/page.tsx      # Admin review queue
├── components/
│   ├── ui/                 # shadcn/ui primitives
│   ├── search-bar.tsx      # Search with filters
│   ├── resource-card.tsx   # Resource display card
│   └── category-buttons.tsx
└── lib/
    └── api.ts              # Typed API client
```

## API Client

The API client in `src/lib/api.ts` provides typed access to all backend endpoints:

```typescript
import { api } from '@/lib/api';

// List resources
const { resources, total } = await api.resources.list({
  category: 'employment',
  state: 'TX',
  limit: 20,
});

// Search with full-text
const { results } = await api.search.query({
  q: 'job training',
  category: 'training',
});

// Get single resource
const resource = await api.resources.get(id);

// Admin: review queue
const { items } = await api.admin.getReviewQueue({ status: 'pending' });
await api.admin.reviewResource(reviewId, 'approve', 'admin@example.com');
```

### Key Types

- `Resource` - Full resource with organization, location, trust signals
- `SearchResult` - Resource with rank and match explanations
- `ReviewQueueItem` - Pending review with changes summary

## Components

### shadcn/ui Components

Located in `src/components/ui/`. Installed via shadcn CLI:

- `Button`, `Input`, `Card` - Basic form elements
- `Select` - Dropdowns with Radix UI
- `Dialog` - Modal dialogs
- `Tabs`, `Table` - Data display
- `Badge`, `Separator`, `Skeleton` - UI helpers

### Custom Components

| Component | Purpose |
|-----------|---------|
| `SearchBar` | Full-text search with category/state filters |
| `ResourceCard` | Displays resource with trust signals |
| `CategoryButtons` | Quick category navigation |

## State & Territory Filters

State filters use 2-letter codes. In addition to the 50 states, the UI supports:

- `DC` (District of Columbia)
- `PR` (Puerto Rico)
- `GU` (Guam)
- `VI` (U.S. Virgin Islands)
- `AS` (American Samoa)
- `MP` (Northern Mariana Islands)

When a state/territory filter is selected, national resources still appear alongside local matches.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server with Turbopack |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | ESLint check |
