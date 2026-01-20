# Design: Hierarchical Resources (Programs -> Providers)

## Status: Decided

**Decision**: Option B - Parent/child relationships via `program_id` foreign key

## Problem

Resources are currently flat, creating UX clutter when programs like SSVF have 235 local providers. Veterans see walls of similar-looking cards instead of understanding "SSVF is one program with multiple providers near me."

| Program | Provider Count | Current UX Issue |
|---------|---------------|------------------|
| SSVF | 235 | 235 separate cards |
| HUD-VASH | 400+ | 400+ separate cards |
| Legal Aid (LSC) | 129 | 129 separate cards |

## Options Considered

### Option A: UI-only Grouping
- Group cards by a `program` text field in the frontend
- No schema change required
- **Pros**: Quick to implement
- **Cons**: Loses provider detail when collapsed, no program-level metadata

### Option B: Parent/Child via program_id (CHOSEN)
- `Resource.program_id` links to `Program` model
- Program model stores program-level info (description, services, eligibility)
- UI shows folder cards for programs, expands to show child resources
- **Pros**: Clean data model, already partially implemented, program-level detail pages possible
- **Cons**: Requires UI grouping logic

### Option C: Separate Program Entity with Resource Children
- Full separation of Program and Resource as distinct concepts
- Programs have own CRUD, detail pages, search behavior
- **Pros**: Most flexible, cleanest separation of concerns
- **Cons**: Most complex, significant migration needed

## Why Option B

1. **Already implemented**: `Program` model exists with `ProgramType` enum (SSVF, HUD_VASH, etc.) and `Resource.program_id` foreign key is in place
2. **Minimal migration**: Existing SSVF connector already uses program_id
3. **Good UX balance**: Folder-style grouping with expand/collapse provides hierarchy without over-engineering
4. **Extensible**: Can evolve to Option C later if needed

## Data Model (Already Exists)

```python
# backend/app/models/program.py
class Program(SQLModel, table=True):
    id: UUID
    organization_id: UUID  # Parent org
    name: str
    program_type: ProgramType  # ssvf, hud_vash, gpd, etc.
    description: str | None
    services_offered: list[str]  # rapid re-housing, prevention, etc.
    states: list[str]  # States served
    status: ProgramStatus  # active, ended, pending
    # ... contact info, funding dates

# backend/app/models/resource.py
class Resource(SQLModel, table=True):
    id: UUID
    program_id: UUID | None  # Links to parent program
    # ... other fields
```

## UI Implementation

### ProgramCard Component
Visually distinct "folder" card for programs:
- Different color scheme (muted purple/indigo)
- Folder icon instead of category icon
- Badge showing "X providers"
- Expand/collapse chevron

### Search Results Grouping
1. API returns `program_id` with each resource
2. Frontend groups resources by `program_id`
3. For each group with program_id:
   - Show ProgramCard with expand toggle
   - Below: indented list of child ResourceCards (collapsed by default)
4. Standalone resources (no program_id) render normally

### Filtering Behavior
- State/category filters still work on individual resources
- When filtering, show only matching children under program
- Hide program card if no children match filters

## API Changes Required

1. **Add `program_id` to `ResourceRead` schema** (backend/app/schemas/resource.py)
2. **Add `program_id` to frontend `Resource` type** (frontend/src/lib/api.ts)
3. **Optionally add Program endpoint** for program detail pages (future)

## Future Considerations

1. **Program detail pages**: `/programs/{id}` showing all providers
2. **Program search**: Search programs directly, see providers
3. **Map view**: Show program coverage areas
4. **Provider filtering**: "Show SSVF providers in VA" within program context
