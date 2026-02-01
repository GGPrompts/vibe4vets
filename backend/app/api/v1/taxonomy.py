"""Taxonomy endpoints for categories, subcategories, and eligibility tags.

Provides the tag taxonomy for frontend consumption to power filter UIs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_
from sqlmodel import Session, select

from app.core.taxonomy import (
    CATEGORIES,
    ELIGIBILITY_TAGS,
    SUBCATEGORIES,
    get_category,
    get_eligibility_tags,
    get_flat_tags_for_category,
    get_subcategories,
    get_tag_display_name,
)
from app.database import get_session
from app.models import Resource
from app.models.resource import ResourceScope

router = APIRouter()


class TagInfo(BaseModel):
    """Tag information for display."""

    id: str = Field(..., description="Tag identifier (e.g., 'hud-vash')")
    name: str = Field(..., description="Display name (e.g., 'HUD-VASH')")


class TagGroup(BaseModel):
    """Group of related tags within a category."""

    group: str = Field(..., description="Group name (e.g., 'voucher', 'type')")
    tags: list[TagInfo] = Field(..., description="Tags in this group")


class CategoryTags(BaseModel):
    """Tags organized by category."""

    category_id: str = Field(..., description="Category identifier")
    category_name: str = Field(..., description="Category display name")
    groups: list[TagGroup] = Field(..., description="Tag groups for this category")


class TaxonomyResponse(BaseModel):
    """Full tag taxonomy response."""

    categories: list[CategoryTags] = Field(..., description="All categories with their tags")

    model_config = {
        "json_schema_extra": {
            "example": {
                "categories": [
                    {
                        "category_id": "housing",
                        "category_name": "Housing",
                        "groups": [
                            {
                                "group": "voucher",
                                "tags": [
                                    {"id": "hud-vash", "name": "HUD-VASH"},
                                    {"id": "ssvf", "name": "SSVF"},
                                ],
                            }
                        ],
                    }
                ]
            }
        }
    }


class CategoryTagsResponse(BaseModel):
    """Tags for a single category."""

    category_id: str
    category_name: str
    groups: list[TagGroup]
    flat_tags: list[TagInfo] = Field(..., description="All tags for this category as a flat list")


@router.get(
    "/tags",
    response_model=TaxonomyResponse,
    summary="Get full tag taxonomy",
    response_description="Complete tag taxonomy organized by category and group",
)
def get_tag_taxonomy() -> TaxonomyResponse:
    """Get the complete eligibility tag taxonomy.

    Returns all categories with their tag groups, enabling the frontend
    to build tree-style filter UIs for case managers.

    **Use cases:**
    - Populating filter dropdowns/checkboxes
    - Building sidebar tag filters
    - Category card expansion on landing page
    """
    categories_list = []

    for cat_id, cat_tags in ELIGIBILITY_TAGS.items():
        category = get_category(cat_id)
        if not category:
            continue

        groups = []
        for group_name, tag_ids in cat_tags.items():
            tags = [TagInfo(id=tag_id, name=get_tag_display_name(tag_id)) for tag_id in tag_ids]
            groups.append(TagGroup(group=group_name, tags=tags))

        categories_list.append(
            CategoryTags(
                category_id=cat_id,
                category_name=category.name,
                groups=groups,
            )
        )

    return TaxonomyResponse(categories=categories_list)


@router.get(
    "/tags/{category_id}",
    response_model=CategoryTagsResponse,
    summary="Get tags for a category",
    response_description="Tags for the specified category",
    responses={
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail": "Category not found"}}},
        }
    },
)
def get_category_tags(
    category_id: str,
    states: str | None = Query(None, description="Filter by states (comma-separated)"),
    zip: str | None = Query(None, description="Filter by ZIP code"),
    radius: int = Query(100, description="Radius in miles for ZIP search"),
    scope: str | None = Query(None, description="Filter by scope (national/state/local)"),
    filter_empty: bool = Query(False, description="If true, only return tags with results"),
    db: Session = Depends(get_session),
) -> CategoryTagsResponse:
    """Get eligibility tags for a specific category.

    Returns both grouped and flat tag lists for flexible frontend usage.

    When filter_empty=true and filters are provided, only returns tags that have
    at least 1 resource matching the current filters.
    """
    category = get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    cat_tags = get_eligibility_tags(category_id)
    all_tag_ids = get_flat_tags_for_category(category_id)

    # If filter_empty is requested and we have filters, check which tags have results
    tags_with_results = set(all_tag_ids)  # Default: all tags
    if filter_empty and (states or zip or scope):
        tags_with_results = set()

        # Build base query with current filters
        base_conditions = [Resource.categories.contains([category_id])]

        if states:
            state_list = [s.strip().upper() for s in states.split(",") if s.strip()]
            if state_list:
                # Truly nationwide (empty states) or matching states
                state_conditions = [and_(Resource.scope == ResourceScope.NATIONAL, Resource.states == [])]
                for s in state_list:
                    state_conditions.append(Resource.states.contains([s]))
                base_conditions.append(or_(*state_conditions))

        if scope and scope != "all":
            if scope == "state":
                # "state" in UI means non-national (state + local)
                base_conditions.append(Resource.scope != ResourceScope.NATIONAL)
            elif scope == "national":
                base_conditions.append(Resource.scope == ResourceScope.NATIONAL)
            elif scope == "local":
                base_conditions.append(Resource.scope == ResourceScope.LOCAL)

        # For each tag, check if there are any matching resources
        for tag_id in all_tag_ids:
            tag_condition = or_(
                Resource.tags.contains([tag_id]),
                Resource.subcategories.contains([tag_id]),
                func.lower(Resource.eligibility).contains(tag_id.lower()),
                func.lower(Resource.title).contains(tag_id.replace("-", " ").lower()),
            )

            query = select(func.count()).select_from(Resource).where(*base_conditions, tag_condition)
            count = db.execute(query).scalar() or 0
            if count > 0:
                tags_with_results.add(tag_id)

    # Build response with only tags that have results
    groups = []
    for group_name, tag_ids in cat_tags.items():
        filtered_tag_ids = [tid for tid in tag_ids if tid in tags_with_results]
        if filtered_tag_ids:  # Only include group if it has tags
            tags = [TagInfo(id=tag_id, name=get_tag_display_name(tag_id)) for tag_id in filtered_tag_ids]
            groups.append(TagGroup(group=group_name, tags=tags))

    flat_tags = [
        TagInfo(id=tag_id, name=get_tag_display_name(tag_id)) for tag_id in all_tag_ids if tag_id in tags_with_results
    ]

    return CategoryTagsResponse(
        category_id=category_id,
        category_name=category.name,
        groups=groups,
        flat_tags=flat_tags,
    )


class CategoryInfo(BaseModel):
    """Category information."""

    id: str
    name: str
    description: str


class CategoriesResponse(BaseModel):
    """List of all categories."""

    categories: list[CategoryInfo]


@router.get(
    "/categories",
    response_model=CategoriesResponse,
    summary="Get all categories",
    response_description="List of all resource categories",
)
def get_categories() -> CategoriesResponse:
    """Get all resource categories.

    Returns the list of categories available for filtering resources.
    """
    categories_list = [
        CategoryInfo(id=cat.id, name=cat.name, description=cat.description) for cat in CATEGORIES.values()
    ]
    return CategoriesResponse(categories=categories_list)


class SubcategoryInfo(BaseModel):
    """Subcategory information."""

    id: str
    name: str
    category_id: str
    description: str


class SubcategoriesResponse(BaseModel):
    """List of subcategories."""

    subcategories: list[SubcategoryInfo]


@router.get(
    "/subcategories",
    response_model=SubcategoriesResponse,
    summary="Get all subcategories",
    response_description="List of all subcategories, optionally filtered by category",
)
def get_all_subcategories(category_id: str | None = None) -> SubcategoriesResponse:
    """Get subcategories, optionally filtered by category."""
    subs = get_subcategories(category_id) if category_id else list(SUBCATEGORIES.values())

    subcategories_list = [
        SubcategoryInfo(
            id=sub.id,
            name=sub.name,
            category_id=sub.category_id,
            description=sub.description,
        )
        for sub in subs
    ]
    return SubcategoriesResponse(subcategories=subcategories_list)
