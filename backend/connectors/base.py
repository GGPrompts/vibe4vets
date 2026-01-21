"""Base connector interface for data sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, Self


@dataclass
class SourceMetadata:
    """Metadata about a data source."""

    name: str
    url: str
    tier: int  # 1=official, 2=established, 3=state, 4=community
    frequency: str  # daily, weekly, monthly
    terms_url: str | None = None
    requires_auth: bool = False


@dataclass
class ResourceCandidate:
    """Normalized resource from any source."""

    # Required
    title: str
    description: str
    source_url: str

    # Organization
    org_name: str
    org_website: str | None = None

    # Location (optional)
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    # Classification
    categories: list[str] | None = None
    tags: list[str] | None = None

    # Contact
    phone: str | None = None
    email: str | None = None
    hours: str | None = None

    # Content
    eligibility: str | None = None
    how_to_apply: str | None = None

    # Scope
    scope: str = "national"  # national, state, local
    states: list[str] | None = None

    # Metadata
    raw_data: dict | None = None
    fetched_at: datetime | None = None


class Connector(Protocol):
    """Protocol for data source connectors."""

    def run(self) -> list[ResourceCandidate]:
        """Fetch and return normalized resources."""
        ...

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        ...

    def close(self) -> None:
        """Close any open resources (HTTP clients, file handles, etc)."""
        ...

    def __enter__(self) -> Self:
        """Context manager entry."""
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        ...


class BaseConnector(ABC):
    """Base class for connectors with common functionality."""

    @abstractmethod
    def run(self) -> list[ResourceCandidate]:
        """Fetch and return normalized resources."""
        pass

    @property
    @abstractmethod
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        pass

    def close(self) -> None:
        """Close any open resources. Override in subclasses with resources to clean up."""
        pass

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit - ensures resources are cleaned up."""
        self.close()

    def _normalize_phone(self, phone: str | None) -> str | None:
        """Normalize phone number format."""
        if not phone:
            return None
        # Remove non-digits
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone

    def _normalize_state(self, state: str | None) -> str | None:
        """Normalize state to two-letter code."""
        if not state:
            return None
        state = state.strip().upper()
        if len(state) == 2:
            return state
        # TODO: Add state name to code mapping
        return state[:2] if len(state) > 2 else state
