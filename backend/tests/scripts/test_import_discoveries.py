"""Tests for import_discoveries script."""

from scripts.import_discoveries import (
    map_eligibility_to_location_fields,
    parse_address,
)


class TestParseAddress:
    """Tests for parse_address function."""

    def test_full_address_with_zip(self):
        """Parse complete address with zip code."""
        result = parse_address("1201 Hull Street, Richmond, VA 23224")
        assert result["address"] == "1201 Hull Street"
        assert result["city"] == "Richmond"
        assert result["state"] == "VA"
        assert result["zip_code"] == "23224"

    def test_address_with_multiple_commas(self):
        """Parse address with floor/suite info."""
        result = parse_address("101 North 14th Street, 17th Floor, Richmond, VA 23219")
        assert result["address"] == "101 North 14th Street, 17th Floor"
        assert result["city"] == "Richmond"
        assert result["state"] == "VA"
        assert result["zip_code"] == "23219"

    def test_address_without_zip(self):
        """Parse address without zip code."""
        result = parse_address("Fort Gregg-Adams, Petersburg, VA")
        assert result["address"] == "Fort Gregg-Adams"
        assert result["city"] == "Petersburg"
        assert result["state"] == "VA"
        assert result["zip_code"] == ""

    def test_po_box_address(self):
        """Parse P.O. Box address."""
        result = parse_address("P.O. Box 5222, Richmond, VA 23220")
        assert result["address"] == "P.O. Box 5222"
        assert result["city"] == "Richmond"
        assert result["state"] == "VA"
        assert result["zip_code"] == "23220"

    def test_none_address(self):
        """Handle None input."""
        result = parse_address(None)
        assert result["address"] == ""
        assert result["city"] == ""
        assert result["state"] == ""
        assert result["zip_code"] == ""

    def test_empty_address(self):
        """Handle empty string input."""
        result = parse_address("")
        assert result["address"] == ""
        assert result["city"] == ""
        assert result["state"] == ""
        assert result["zip_code"] == ""

    def test_address_with_zip_plus_four(self):
        """Parse address with ZIP+4 code."""
        result = parse_address("123 Main St, Arlington, VA 22201-1234")
        assert result["address"] == "123 Main St"
        assert result["city"] == "Arlington"
        assert result["state"] == "VA"
        assert result["zip_code"] == "22201-1234"


class TestMapEligibilityToLocationFields:
    """Tests for map_eligibility_to_location_fields function."""

    def test_veteran_homeless(self):
        """Map veteran + homeless eligibility."""
        result = map_eligibility_to_location_fields(["veteran", "homeless"])
        assert result["veteran_status_required"] is True
        assert "homeless" in result["housing_status_required"]
        assert "DD-214 or VA letter" in result["docs_required"]
        assert "Photo ID" in result["docs_required"]

    def test_at_risk_homeless(self):
        """Map at-risk homeless eligibility."""
        result = map_eligibility_to_location_fields(["veteran", "at_risk_homeless"])
        assert "at_risk" in result["housing_status_required"]
        assert result["veteran_status_required"] is True

    def test_low_income(self):
        """Map low income eligibility to at_risk + stably_housed."""
        result = map_eligibility_to_location_fields(["low_income"])
        assert "at_risk" in result["housing_status_required"]
        assert "stably_housed" in result["housing_status_required"]

    def test_disabled_veteran(self):
        """Map disabled veteran adds VA disability docs."""
        result = map_eligibility_to_location_fields(["disabled_veteran"])
        assert result["veteran_status_required"] is True
        assert "VA disability rating documentation" in result["docs_required"]

    def test_active_duty(self):
        """Map active duty status."""
        result = map_eligibility_to_location_fields(["active_duty"])
        assert result["active_duty_required"] is True

    def test_military_family_no_veteran_required(self):
        """Military family doesn't require veteran status."""
        result = map_eligibility_to_location_fields(["military_spouse"])
        assert result["veteran_status_required"] is False

    def test_empty_list(self):
        """Handle empty eligibility list."""
        result = map_eligibility_to_location_fields([])
        assert result["veteran_status_required"] is False
        assert result["housing_status_required"] == []
        assert result["docs_required"] == []

    def test_combined_eligibility(self):
        """Test multiple eligibility criteria combined."""
        result = map_eligibility_to_location_fields(["veteran", "homeless", "disabled_veteran"])
        assert result["veteran_status_required"] is True
        assert "homeless" in result["housing_status_required"]
        assert "DD-214 or VA letter" in result["docs_required"]
        assert "VA disability rating documentation" in result["docs_required"]
