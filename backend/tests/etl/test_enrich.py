"""Tests for ETL enricher."""

from etl.enrich import Enricher, StubGeocoder
from etl.models import NormalizedResource


class MockGeocoder:
    """Mock geocoder that returns preset coordinates."""

    def __init__(self, lat: float = 38.9072, lng: float = -77.0369):
        self.lat = lat
        self.lng = lng
        self.calls: list[tuple[str, str, str, str]] = []

    def geocode(
        self, address: str, city: str, state: str, zip_code: str
    ) -> tuple[float | None, float | None]:
        self.calls.append((address, city, state, zip_code))
        return self.lat, self.lng


class TestEnricher:
    """Tests for the Enricher class."""

    def test_enrich_basic(self):
        """Test basic enrichment."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            source_tier=2,
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        # Should have reliability score from tier
        assert result.reliability_score == 0.8  # Tier 2

    def test_enrich_geocoding(self):
        """Test that geocoding is called for addresses."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            address="123 Main St",
            city="Washington",
            state="DC",
            zip_code="20001",
        )

        geocoder = MockGeocoder(lat=38.9, lng=-77.0)
        enricher = Enricher(geocoder=geocoder)
        result = enricher.enrich(resource)

        assert len(geocoder.calls) == 1
        assert result.latitude == 38.9
        assert result.longitude == -77.0

    def test_enrich_no_geocoding_without_address(self):
        """Test that geocoding is skipped without full address."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            city="Washington",  # No full address
            state="DC",
        )

        geocoder = MockGeocoder()
        enricher = Enricher(geocoder=geocoder)
        enricher.enrich(resource)

        assert len(geocoder.calls) == 0

    def test_enrich_infers_employment_category(self):
        """Test category inference for employment keywords."""
        resource = NormalizedResource(
            title="Job Placement Program",
            description="Career counseling and employment services for veterans",
            source_url="https://example.com",
            org_name="Test Org",
            categories=[],  # Empty - should be inferred
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "employment" in result.categories

    def test_enrich_infers_training_category(self):
        """Test category inference for training keywords."""
        resource = NormalizedResource(
            title="GI Bill Education Benefits",
            description="Vocational training and certification programs",
            source_url="https://example.com",
            org_name="Test Org",
            categories=[],
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "training" in result.categories

    def test_enrich_infers_housing_category(self):
        """Test category inference for housing keywords."""
        resource = NormalizedResource(
            title="HUD-VASH Program",
            description="Emergency shelter and transitional housing for homeless veterans",
            source_url="https://example.com",
            org_name="Test Org",
            categories=[],
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "housing" in result.categories

    def test_enrich_infers_legal_category(self):
        """Test category inference for legal keywords."""
        resource = NormalizedResource(
            title="Veterans Legal Aid",
            description="Free legal assistance for VA appeals and discharge upgrades",
            source_url="https://example.com",
            org_name="Test Org",
            categories=[],
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "legal" in result.categories

    def test_enrich_preserves_existing_categories(self):
        """Test that existing categories are not overwritten."""
        resource = NormalizedResource(
            title="Job Services",
            description="Employment services",
            source_url="https://example.com",
            org_name="Test Org",
            categories=["housing"],  # Pre-existing
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        # Should keep housing, not infer employment
        assert result.categories == ["housing"]

    def test_enrich_extracts_tags(self):
        """Test tag extraction from content."""
        resource = NormalizedResource(
            title="PTSD Support Program",
            description="Mental health services for disabled veterans and their family members",
            source_url="https://example.com",
            org_name="Test Org",
            categories=["employment"],
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "ptsd" in result.tags
        assert "mental-health" in result.tags
        assert "disabled" in result.tags or "disability" in result.tags
        # "family" keyword matches "family members" in description
        assert "family" in result.tags
        assert "employment" in result.tags  # From category

    def test_enrich_scope_local_with_address(self):
        """Test scope determination for resources with full address."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            address="123 Main St",
            city="Austin",
            state="TX",
            zip_code="78701",
            scope="local",
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert result.scope == "local"
        assert "TX" in result.states

    def test_enrich_scope_state_without_full_address(self):
        """Test scope determination for state-level resources."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            state="CA",
            scope="state",
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert result.scope == "state"
        assert "CA" in result.states

    def test_enrich_scope_national_no_location(self):
        """Test scope determination for national resources."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            scope="national",
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert result.scope == "national"

    def test_enrich_batch(self):
        """Test batch enrichment."""
        resources = [
            NormalizedResource(
                title="Resource 1",
                description="Employment services",
                source_url="https://example.com/1",
                org_name="Org 1",
                source_tier=1,
            ),
            NormalizedResource(
                title="Resource 2",
                description="Housing assistance",
                source_url="https://example.com/2",
                org_name="Org 2",
                source_tier=3,
            ),
        ]

        enricher = Enricher()
        results = enricher.enrich_batch(resources)

        assert len(results) == 2
        assert results[0].reliability_score == 1.0  # Tier 1
        assert results[1].reliability_score == 0.6  # Tier 3

    def test_enrich_reliability_scores(self):
        """Test reliability score assignment for each tier."""
        enricher = Enricher()

        for tier, expected_score in [(1, 1.0), (2, 0.8), (3, 0.6), (4, 0.4)]:
            resource = NormalizedResource(
                title="Test",
                description="Test",
                source_url="https://example.com",
                org_name="Org",
                source_tier=tier,
            )
            result = enricher.enrich(resource)
            assert result.reliability_score == expected_score

    def test_enrich_adds_nationwide_tag(self):
        """Test that national scope adds nationwide tag."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            scope="national",
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "nationwide" in result.tags

    def test_enrich_adds_state_tags(self):
        """Test that state scope adds state tags."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
            scope="state",
            states=["TX", "CA"],
        )

        enricher = Enricher()
        result = enricher.enrich(resource)

        assert "state-tx" in result.tags
        assert "state-ca" in result.tags


class TestStubGeocoder:
    """Tests for the StubGeocoder class."""

    def test_stub_returns_none(self):
        """Test that stub geocoder returns None."""
        geocoder = StubGeocoder()
        lat, lng = geocoder.geocode("123 Main St", "City", "ST", "12345")

        assert lat is None
        assert lng is None
