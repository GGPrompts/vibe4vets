"""Location model using SQLModel."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.resource import Resource


class Location(SQLModel, table=True):
    """Physical location with geocoding."""

    __tablename__ = "locations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")

    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=2)  # Two-letter code
    zip_code: str = Field(max_length=10)

    latitude: float | None = None
    longitude: float | None = None

    service_area: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # Counties/regions served

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Organization = Relationship(back_populates="locations")
    resources: list[Resource] = Relationship(back_populates="location")
