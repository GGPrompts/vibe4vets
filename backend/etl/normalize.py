"""Data normalization for ETL pipeline.

Converts ResourceCandidate objects from connectors into validated
NormalizedResource objects ready for database insertion.
"""

import hashlib
import re
from urllib.parse import urlparse

from connectors.base import ResourceCandidate
from etl.models import ETLError, NormalizedResource

# Valid US state codes
US_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
    "PR",
    "VI",
    "GU",
    "AS",
    "MP",  # Territories
}

# State name to code mapping
STATE_NAME_TO_CODE = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
    "puerto rico": "PR",
    "virgin islands": "VI",
    "guam": "GU",
    "american samoa": "AS",
    "northern mariana islands": "MP",
}

# Valid resource categories from taxonomy
VALID_CATEGORIES = {"employment", "training", "housing", "legal"}


class Normalizer:
    """Normalizes and validates ResourceCandidate objects."""

    def normalize(
        self, candidate: ResourceCandidate, source_name: str | None = None, source_tier: int = 4
    ) -> tuple[NormalizedResource | None, ETLError | None]:
        """Normalize a single ResourceCandidate.

        Args:
            candidate: Raw resource from connector
            source_name: Name of the source for tracking
            source_tier: Tier of the source (1-4)

        Returns:
            Tuple of (NormalizedResource, None) on success, or (None, ETLError) on failure.
        """
        # Validate required fields
        validation_error = self._validate_required_fields(candidate)
        if validation_error:
            return None, validation_error

        try:
            normalized = NormalizedResource(
                # Required
                title=self._clean_text(candidate.title),
                description=self._clean_text(candidate.description),
                source_url=self._normalize_url(candidate.source_url),
                org_name=self._clean_text(candidate.org_name),
                # Organization
                org_website=(
                    self._normalize_url(candidate.org_website) if candidate.org_website else None
                ),
                # Location
                address=self._clean_text(candidate.address) if candidate.address else None,
                city=self._clean_text(candidate.city) if candidate.city else None,
                state=self._normalize_state(candidate.state),
                zip_code=self._normalize_zip(candidate.zip_code),
                # Classification
                categories=self._normalize_categories(candidate.categories),
                tags=self._normalize_tags(candidate.tags),
                # Contact
                phone=self._normalize_phone(candidate.phone),
                email=self._normalize_email(candidate.email),
                hours=self._clean_text(candidate.hours) if candidate.hours else None,
                # Content
                eligibility=(
                    self._clean_text(candidate.eligibility) if candidate.eligibility else None
                ),
                how_to_apply=(
                    self._clean_text(candidate.how_to_apply) if candidate.how_to_apply else None
                ),
                # Scope
                scope=self._normalize_scope(candidate.scope),
                states=self._normalize_states_list(candidate.states),
                # Trust (initial values, enricher will update)
                source_tier=source_tier,
                reliability_score=self._tier_to_reliability(source_tier),
                # Metadata
                raw_data=candidate.raw_data,
                fetched_at=candidate.fetched_at,
                source_name=source_name,
            )

            # Generate content hash for deduplication
            normalized.content_hash = self._generate_hash(normalized)

            return normalized, None

        except Exception as e:
            return None, ETLError(
                stage="normalize",
                message=f"Unexpected error during normalization: {str(e)}",
                resource_title=candidate.title,
                source_url=candidate.source_url,
                exception=type(e).__name__,
            )

    def normalize_batch(
        self,
        candidates: list[ResourceCandidate],
        source_name: str | None = None,
        source_tier: int = 4,
    ) -> tuple[list[NormalizedResource], list[ETLError]]:
        """Normalize a batch of candidates.

        Args:
            candidates: List of raw resources
            source_name: Name of the source
            source_tier: Tier of the source

        Returns:
            Tuple of (successful normalizations, errors).
        """
        normalized: list[NormalizedResource] = []
        errors: list[ETLError] = []

        for candidate in candidates:
            result, error = self.normalize(candidate, source_name, source_tier)
            if result:
                normalized.append(result)
            if error:
                errors.append(error)

        return normalized, errors

    def _validate_required_fields(self, candidate: ResourceCandidate) -> ETLError | None:
        """Validate that required fields are present and non-empty."""
        missing = []

        if not candidate.title or not candidate.title.strip():
            missing.append("title")
        if not candidate.description or not candidate.description.strip():
            missing.append("description")
        if not candidate.org_name or not candidate.org_name.strip():
            missing.append("org_name")
        if not candidate.source_url or not candidate.source_url.strip():
            missing.append("source_url")

        if missing:
            return ETLError(
                stage="normalize",
                message=f"Missing required fields: {', '.join(missing)}",
                resource_title=candidate.title if candidate.title else "Unknown",
                source_url=candidate.source_url,
            )
        return None

    def _clean_text(self, text: str | None) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove null characters and other control chars (except newlines/tabs)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        return text

    def _normalize_phone(self, phone: str | None) -> str | None:
        """Normalize phone number to (XXX) XXX-XXXX format."""
        if not phone:
            return None

        # Remove non-digits
        digits = "".join(c for c in phone if c.isdigit())

        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        # Return original if can't normalize
        return phone.strip() if phone.strip() else None

    def _normalize_state(self, state: str | None) -> str | None:
        """Normalize state to 2-letter uppercase code."""
        if not state:
            return None

        state = state.strip()

        # Already a 2-letter code?
        if len(state) == 2:
            code = state.upper()
            return code if code in US_STATES else None

        # Try full name lookup
        code = STATE_NAME_TO_CODE.get(state.lower())
        return code

    def _normalize_zip(self, zip_code: str | None) -> str | None:
        """Normalize ZIP code."""
        if not zip_code:
            return None

        zip_code = zip_code.strip()

        # Extract digits
        digits = "".join(c for c in zip_code if c.isdigit())

        if len(digits) == 5:
            return digits
        elif len(digits) == 9:
            return f"{digits[:5]}-{digits[5:]}"
        elif len(digits) > 5:
            return digits[:5]  # Take first 5

        return None

    def _normalize_url(self, url: str | None) -> str:
        """Normalize and validate URL."""
        if not url:
            return ""

        url = url.strip()

        # Add scheme if missing
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        # Basic validation
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return url
        except Exception:
            pass

        return url  # Return as-is if can't validate

    def _normalize_email(self, email: str | None) -> str | None:
        """Normalize and validate email."""
        if not email:
            return None

        email = email.strip().lower()

        # Basic email validation
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return email

        return None

    def _normalize_categories(self, categories: list[str] | None) -> list[str]:
        """Normalize and validate categories against taxonomy."""
        if not categories:
            return []

        valid = []
        for cat in categories:
            cat_lower = cat.lower().strip()
            if cat_lower in VALID_CATEGORIES:
                valid.append(cat_lower)

        return list(set(valid))  # Deduplicate

    def _normalize_tags(self, tags: list[str] | None) -> list[str]:
        """Normalize tags to lowercase with hyphens."""
        if not tags:
            return []

        normalized = []
        for tag in tags:
            # Clean and normalize
            tag = tag.strip().lower()
            tag = re.sub(r"[^a-z0-9\-]", "-", tag)
            tag = re.sub(r"-+", "-", tag).strip("-")

            if tag and len(tag) >= 2:
                normalized.append(tag)

        return list(set(normalized))  # Deduplicate

    def _normalize_scope(self, scope: str | None) -> str:
        """Normalize scope value."""
        if not scope:
            return "national"

        scope = scope.lower().strip()
        if scope in ("national", "state", "local"):
            return scope

        return "national"

    def _normalize_states_list(self, states: list[str] | None) -> list[str]:
        """Normalize list of states to 2-letter codes."""
        if not states:
            return []

        normalized = []
        for state in states:
            code = self._normalize_state(state)
            if code:
                normalized.append(code)

        return list(set(normalized))

    def _tier_to_reliability(self, tier: int) -> float:
        """Convert source tier to initial reliability score."""
        tier_scores = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}
        return tier_scores.get(tier, 0.4)

    def _generate_hash(self, resource: NormalizedResource) -> str:
        """Generate content hash for deduplication and change detection."""
        # Use key fields that identify the resource
        content = "|".join(
            [
                resource.title.lower(),
                resource.org_name.lower(),
                resource.description[:500].lower() if resource.description else "",
                resource.source_url.lower(),
                resource.address.lower() if resource.address else "",
                resource.city.lower() if resource.city else "",
                resource.state or "",
                resource.zip_code or "",
            ]
        )

        return hashlib.sha256(content.encode()).hexdigest()
