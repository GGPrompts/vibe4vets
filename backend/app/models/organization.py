"""Organization model."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Organization(Base):
    """Parent entity for resources - nonprofits, agencies, etc."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ein: Mapped[str | None] = mapped_column(String(20))  # Tax ID if known
    website: Mapped[str | None] = mapped_column(String(500))
    phones: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    emails: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    locations = relationship("Location", back_populates="organization")
    resources = relationship("Resource", back_populates="organization")
