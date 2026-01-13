"""Organization model using SQLModel."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.resource import Resource


class Organization(SQLModel, table=True):
    """Parent entity for resources - nonprofits, agencies, etc."""

    __tablename__ = "organizations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    ein: str | None = Field(default=None, max_length=20)  # Tax ID if known
    website: str | None = Field(default=None, max_length=500)
    phones: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )
    emails: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    locations: list["Location"] = Relationship(back_populates="organization")
    resources: list["Resource"] = Relationship(back_populates="organization")
