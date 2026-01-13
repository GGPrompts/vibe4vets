"""Organization model using SQLModel."""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, String
from sqlmodel import Field, Relationship, SQLModel


class Organization(SQLModel, table=True):
    """Parent entity for resources - nonprofits, agencies, etc."""

    __tablename__ = "organizations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    ein: str | None = Field(default=None, max_length=20)  # Tax ID if known
    website: str | None = Field(default=None, max_length=500)
    phones: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    emails: list[str] = Field(default_factory=list, sa_type=ARRAY(String))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    locations: list["Location"] = Relationship(back_populates="organization")
    resources: list["Resource"] = Relationship(back_populates="organization")
