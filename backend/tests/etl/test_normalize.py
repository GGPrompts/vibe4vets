"""Tests for ETL normalizer."""

from connectors.base import ResourceCandidate
from etl.normalize import Normalizer


class TestNormalizer:
    """Tests for the Normalizer class."""

    def test_normalize_valid_candidate(self, sample_candidate):
        """Test normalizing a valid ResourceCandidate."""
        normalizer = Normalizer()
        result, error = normalizer.normalize(sample_candidate, source_name="VA.gov", source_tier=1)

        assert error is None
        assert result is not None
        assert result.title == "VA Employment Services"
        assert result.org_name == "U.S. Department of Veterans Affairs"
        assert result.source_name == "VA.gov"
        assert result.source_tier == 1
        assert result.reliability_score == 1.0  # Tier 1

    def test_normalize_minimal_candidate(self, minimal_candidate):
        """Test normalizing a minimal ResourceCandidate."""
        normalizer = Normalizer()
        result, error = normalizer.normalize(minimal_candidate)

        assert error is None
        assert result is not None
        assert result.title == "Basic Resource"
        assert result.org_name == "Example Organization"
        assert result.categories == []
        assert result.tags == []

    def test_normalize_missing_required_fields(self, candidate_missing_fields):
        """Test that missing required fields generate an error."""
        normalizer = Normalizer()
        result, error = normalizer.normalize(candidate_missing_fields)

        assert result is None
        assert error is not None
        assert error.stage == "normalize"
        assert "title" in error.message
        assert "org_name" in error.message

    def test_normalize_phone_10_digits(self):
        """Test phone normalization for 10-digit numbers."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            phone="5551234567",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.phone == "(555) 123-4567"

    def test_normalize_phone_11_digits_with_country_code(self):
        """Test phone normalization for 11-digit numbers with country code."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            phone="1-800-827-1000",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.phone == "(800) 827-1000"

    def test_normalize_phone_preserves_invalid(self):
        """Test that invalid phone numbers are preserved as-is."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            phone="555-1234",  # Too short
        )

        result, _ = normalizer.normalize(candidate)
        assert result.phone == "555-1234"

    def test_normalize_state_two_letter(self):
        """Test state normalization for 2-letter codes."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            state="tx",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.state == "TX"

    def test_normalize_state_full_name(self):
        """Test state normalization for full state names."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            state="California",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.state == "CA"

    def test_normalize_state_invalid(self):
        """Test that invalid state codes return None."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            state="ZZ",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.state is None

    def test_normalize_zip_5_digit(self):
        """Test ZIP code normalization for 5-digit codes."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            zip_code="12345",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.zip_code == "12345"

    def test_normalize_zip_9_digit(self):
        """Test ZIP code normalization for 9-digit codes."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            zip_code="123456789",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.zip_code == "12345-6789"

    def test_normalize_url_adds_scheme(self):
        """Test URL normalization adds https scheme."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="example.com/resource",
            org_name="Test Org",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.source_url == "https://example.com/resource"

    def test_normalize_categories_valid(self):
        """Test category normalization filters to valid categories."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            categories=["Employment", "INVALID", "housing"],
        )

        result, _ = normalizer.normalize(candidate)
        assert set(result.categories) == {"employment", "housing"}

    def test_normalize_email_valid(self):
        """Test email normalization for valid emails."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            email="Test@Example.COM",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.email == "test@example.com"

    def test_normalize_email_invalid(self):
        """Test email normalization returns None for invalid emails."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            email="not-an-email",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.email is None

    def test_normalize_tags_cleaned(self):
        """Test tag normalization cleans and formats tags."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            tags=["VA Benefits", "job placement", "CAREER!", "a"],
        )

        result, _ = normalizer.normalize(candidate)
        # "a" should be filtered out (too short)
        assert "va-benefits" in result.tags
        assert "job-placement" in result.tags
        assert "career" in result.tags
        assert "a" not in result.tags

    def test_normalize_batch(self, sample_candidate, minimal_candidate, candidate_missing_fields):
        """Test batch normalization."""
        normalizer = Normalizer()
        candidates = [sample_candidate, minimal_candidate, candidate_missing_fields]

        normalized, errors = normalizer.normalize_batch(candidates, source_name="Test")

        assert len(normalized) == 2  # Two valid
        assert len(errors) == 1  # One invalid
        assert errors[0].stage == "normalize"

    def test_normalize_generates_hash(self, sample_candidate):
        """Test that normalization generates a content hash."""
        normalizer = Normalizer()
        result, _ = normalizer.normalize(sample_candidate)

        assert result.content_hash is not None
        assert len(result.content_hash) == 64  # SHA-256 hex

    def test_normalize_same_content_same_hash(self):
        """Test that same content generates same hash."""
        normalizer = Normalizer()
        candidate1 = ResourceCandidate(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
        )
        candidate2 = ResourceCandidate(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result1, _ = normalizer.normalize(candidate1)
        result2, _ = normalizer.normalize(candidate2)

        assert result1.content_hash == result2.content_hash

    def test_normalize_scope_values(self):
        """Test scope normalization."""
        normalizer = Normalizer()

        for scope in ["national", "state", "local"]:
            candidate = ResourceCandidate(
                title="Test",
                description="Test desc",
                source_url="https://example.com",
                org_name="Test Org",
                scope=scope,
            )
            result, _ = normalizer.normalize(candidate)
            assert result.scope == scope

        # Invalid scope defaults to national
        candidate = ResourceCandidate(
            title="Test",
            description="Test desc",
            source_url="https://example.com",
            org_name="Test Org",
            scope="invalid",
        )
        result, _ = normalizer.normalize(candidate)
        assert result.scope == "national"

    def test_normalize_cleans_whitespace(self):
        """Test that excessive whitespace is cleaned."""
        normalizer = Normalizer()
        candidate = ResourceCandidate(
            title="  Test   Resource  ",
            description="Multiple   spaces\t\tand\n\nnewlines",
            source_url="https://example.com",
            org_name="  Org  Name  ",
        )

        result, _ = normalizer.normalize(candidate)
        assert result.title == "Test Resource"
        assert "  " not in result.description
        assert result.org_name == "Org Name"
