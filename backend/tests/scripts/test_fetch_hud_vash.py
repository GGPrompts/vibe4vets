"""Tests for HUD-VASH award PDF fetcher script."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import script functions - handle case where pdfplumber is not installed
try:
    from scripts.fetch_hud_vash_awards import (
        _clean_text,
        _parse_table_row,
        create_awards_json,
        HUD_VASH_PDF_URL_TEMPLATE,
    )
    SCRIPT_AVAILABLE = True
except ImportError:
    SCRIPT_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not SCRIPT_AVAILABLE,
    reason="fetch_hud_vash_awards script not available"
)


class TestCleanText:
    """Tests for _clean_text function."""

    def test_clean_text_none(self):
        """Test cleaning None value."""
        assert _clean_text(None) == ""

    def test_clean_text_strips_whitespace(self):
        """Test cleaning strips leading/trailing whitespace."""
        assert _clean_text("  test  ") == "test"

    def test_clean_text_normalizes_whitespace(self):
        """Test cleaning normalizes internal whitespace."""
        assert _clean_text("test  multiple   spaces") == "test multiple spaces"

    def test_clean_text_handles_newlines(self):
        """Test cleaning handles newlines in text."""
        assert _clean_text("line1\nline2") == "line1 line2"


class TestParseTableRow:
    """Tests for _parse_table_row function."""

    def test_parse_valid_row(self):
        """Test parsing a valid table row."""
        row = ["CA004", "Housing Authority of Los Angeles", "V22/Greater LA HCS", "250", "$3,886,200"]
        result = _parse_table_row(row)

        assert result is not None
        assert result["pha_code"] == "CA004"
        assert result["pha_name"] == "Housing Authority of Los Angeles"
        assert result["vamc"] == "V22/Greater LA HCS"
        assert result["vouchers"] == 250
        assert result["budget"] == 3886200

    def test_parse_row_with_commas(self):
        """Test parsing row with comma-formatted numbers."""
        row = ["TX004", "Fort Worth Housing", "V17/Dallas", "1,250", "$12,345,678"]
        result = _parse_table_row(row)

        assert result is not None
        assert result["vouchers"] == 1250
        assert result["budget"] == 12345678

    def test_parse_row_short(self):
        """Test parsing too-short row returns None."""
        row = ["CA004", "Housing Authority"]
        result = _parse_table_row(row)
        assert result is None

    def test_parse_row_empty(self):
        """Test parsing empty row returns None."""
        result = _parse_table_row([])
        assert result is None

    def test_parse_row_none(self):
        """Test parsing None returns None."""
        result = _parse_table_row(None)
        assert result is None

    def test_parse_row_invalid_pha_code(self):
        """Test parsing row with invalid PHA code returns None."""
        row = ["invalid", "Some PHA", "V22/Phoenix", "10", "$50,000"]
        result = _parse_table_row(row)
        assert result is None

    def test_parse_row_invalid_vouchers(self):
        """Test parsing row with non-numeric vouchers returns None."""
        row = ["CA004", "Housing Authority", "V22/Phoenix", "N/A", "$50,000"]
        result = _parse_table_row(row)
        assert result is None

    def test_parse_row_invalid_budget(self):
        """Test parsing row with non-numeric budget returns None."""
        row = ["CA004", "Housing Authority", "V22/Phoenix", "10", "TBD"]
        result = _parse_table_row(row)
        assert result is None


class TestCreateAwardsJson:
    """Tests for create_awards_json function."""

    def test_creates_valid_json_structure(self):
        """Test creating JSON with proper structure."""
        awards = [
            {"pha_code": "CA004", "pha_name": "LA Housing", "vamc": "V22/LA", "vouchers": 100, "budget": 500000},
            {"pha_code": "TX004", "pha_name": "Dallas Housing", "vamc": "V17/Dallas", "vouchers": 50, "budget": 200000},
        ]

        result = create_awards_json(awards, 2024, "https://example.com/test.pdf")

        assert "metadata" in result
        assert "awards" in result
        assert result["awards"] == awards

    def test_calculates_totals(self):
        """Test that totals are calculated correctly."""
        awards = [
            {"pha_code": "CA004", "pha_name": "LA Housing", "vamc": "V22/LA", "vouchers": 100, "budget": 500000},
            {"pha_code": "TX004", "pha_name": "Dallas Housing", "vamc": "V17/Dallas", "vouchers": 50, "budget": 200000},
        ]

        result = create_awards_json(awards, 2024, "https://example.com/test.pdf")

        assert result["metadata"]["total_vouchers"] == 150
        assert result["metadata"]["total_budget"] == 700000

    def test_includes_source_url(self):
        """Test that source URL is included in metadata."""
        awards = [{"pha_code": "CA004", "pha_name": "Test", "vamc": "V22/Test", "vouchers": 10, "budget": 50000}]

        result = create_awards_json(awards, 2024, "https://hud.gov/test.pdf")

        assert result["metadata"]["source"] == "https://hud.gov/test.pdf"

    def test_includes_notice_number(self):
        """Test that notice number pattern is included."""
        awards = [{"pha_code": "CA004", "pha_name": "Test", "vamc": "V22/Test", "vouchers": 10, "budget": 50000}]

        result = create_awards_json(awards, 2024, "https://example.com/test.pdf")

        assert result["metadata"]["notice"] == "PIH 2024-18"

    def test_includes_extracted_date(self):
        """Test that extraction date is included."""
        awards = [{"pha_code": "CA004", "pha_name": "Test", "vamc": "V22/Test", "vouchers": 10, "budget": 50000}]

        result = create_awards_json(awards, 2024, "https://example.com/test.pdf")

        # Should be a date string in YYYY-MM-DD format
        assert "extracted_date" in result["metadata"]
        date_str = result["metadata"]["extracted_date"]
        assert len(date_str) == 10  # YYYY-MM-DD
        assert date_str[4] == "-" and date_str[7] == "-"


class TestURLTemplate:
    """Tests for PDF URL template."""

    def test_url_template_2024(self):
        """Test URL template for 2024."""
        url = HUD_VASH_PDF_URL_TEMPLATE.format(year=2024)
        assert url == "https://www.hud.gov/sites/dfiles/PIH/documents/2024-HUD-VASH-Awards_List-by-PHA.pdf"

    def test_url_template_2025(self):
        """Test URL template for 2025."""
        url = HUD_VASH_PDF_URL_TEMPLATE.format(year=2025)
        assert url == "https://www.hud.gov/sites/dfiles/PIH/documents/2025-HUD-VASH-Awards_List-by-PHA.pdf"
