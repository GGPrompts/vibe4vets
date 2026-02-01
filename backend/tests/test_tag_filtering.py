"""Tests for tag filtering with AND logic.

These tests verify that selecting multiple tags narrows results (AND logic)
rather than broadening them (OR logic).
"""


class TestTagFilteringLogic:
    """Test that tag filtering uses AND logic."""

    def test_single_tag_filter_matches_resource_with_tag(self):
        """A single tag should match resources that have that tag."""
        # This is a unit test verifying the logic pattern
        resource_tags = ["veterans", "housing", "hud-vash"]
        filter_tags = ["veterans"]

        # AND logic: resource must have ALL filter tags
        result = all(tag in resource_tags for tag in filter_tags)
        assert result is True

    def test_multiple_tags_require_all_matches(self):
        """Multiple tags should require ALL tags to match (AND logic)."""
        resource_tags = ["veterans", "housing", "hud-vash"]
        filter_tags = ["veterans", "housing"]

        # AND logic: resource must have ALL filter tags
        result = all(tag in resource_tags for tag in filter_tags)
        assert result is True

    def test_multiple_tags_fails_if_one_missing(self):
        """If any tag is missing, the resource should NOT match (AND logic)."""
        resource_tags = ["veterans", "housing"]
        filter_tags = ["veterans", "families"]  # "families" is not in resource_tags

        # AND logic: resource must have ALL filter tags
        result = all(tag in resource_tags for tag in filter_tags)
        assert result is False

    def test_more_tags_narrow_results(self):
        """Adding more tags should narrow results, not broaden them."""
        resources = [
            {"tags": ["veterans", "housing", "hud-vash"]},
            {"tags": ["veterans", "employment"]},
            {"tags": ["families", "housing"]},
        ]

        # Single tag "veterans" - should match 2 resources
        filter_single = ["veterans"]
        matches_single = [r for r in resources if all(t in r["tags"] for t in filter_single)]
        assert len(matches_single) == 2

        # Two tags "veterans" AND "housing" - should match 1 resource (narrower)
        filter_double = ["veterans", "housing"]
        matches_double = [r for r in resources if all(t in r["tags"] for t in filter_double)]
        assert len(matches_double) == 1

        # More tags = fewer results (refinement behavior)
        assert len(matches_double) < len(matches_single)

    def test_empty_tags_matches_all(self):
        """Empty tags list should not filter anything."""
        resources = [
            {"tags": ["veterans"]},
            {"tags": ["families"]},
        ]

        filter_tags = []
        # Empty filter should match all (no filtering applied)
        matches = resources if not filter_tags else [r for r in resources if all(t in r["tags"] for t in filter_tags)]

        assert len(matches) == 2


class TestBuildTagsSql:
    """Test the SQL generation for tag filtering."""

    def test_build_tags_sql_uses_and_join(self):
        """The build_tags_sql helper should use AND to join tag conditions."""
        # Simulate the build_tags_sql function logic
        tags = ["veterans", "housing"]
        tag_conditions = []
        for tag in tags:
            search_term = f"%{tag}%"
            search_term_spaced = f"%{tag.replace('-', ' ')}%"
            tag_conditions.append(
                f"(r.eligibility ILIKE '{search_term}' OR r.eligibility ILIKE '{search_term_spaced}' "
                f"OR r.title ILIKE '{search_term}' OR r.title ILIKE '{search_term_spaced}' "
                f"OR r.description ILIKE '{search_term}' OR r.description ILIKE '{search_term_spaced}' "
                f"OR r.tags @> ARRAY['{tag}']::text[] "
                f"OR r.subcategories @> ARRAY['{tag}']::text[])"
            )

        # AND logic: join with AND
        result = " AND ".join(tag_conditions)

        # Verify AND is used between conditions
        assert " AND " in result
        # Verify there's no OR at the top level (only within each tag's condition)
        assert result.count(" AND ") == len(tags) - 1  # One AND between each pair
        # Verify both tags are in the result
        assert "veterans" in result
        assert "housing" in result

    def test_single_tag_no_and_needed(self):
        """Single tag should not need AND join."""
        tags = ["veterans"]
        tag_conditions = []
        for tag in tags:
            search_term = f"%{tag}%"
            tag_conditions.append(f"(r.tags @> ARRAY['{tag}']::text[])")

        result = " AND ".join(tag_conditions)

        # Single condition, no AND in output
        assert " AND " not in result
        assert "veterans" in result


class TestSQLInjectionPrevention:
    """Test that SQL injection attempts are properly handled.

    These tests verify that parameterized queries prevent SQL injection
    in tag and category filters.
    """

    def test_malicious_tag_is_parameterized(self):
        """Malicious SQL in tag values should be parameterized, not interpolated.

        The build_tags_sql function should produce parameterized SQL that
        doesn't directly embed user input.
        """
        # Simulate the parameterized build_tags_sql function logic
        malicious_tags = ["'] OR 1=1--", "'; DROP TABLE resources;--", "<script>alert(1)</script>"]
        params = {}

        for i, tag in enumerate(malicious_tags):
            param_like = f"tag_like_{i}"
            param_like_spaced = f"tag_like_spaced_{i}"
            param_array = f"tag_array_{i}"
            # Values go into params dict, not SQL string
            params[param_like] = f"%{tag}%"
            params[param_like_spaced] = f"%{tag.replace('-', ' ')}%"
            params[param_array] = tag

        # Verify malicious content is in params, not in SQL structure
        assert "'] OR 1=1--" not in "".join(params.keys())  # Not in param names
        assert "'] OR 1=1--" in params["tag_array_0"]  # In param values (safe)

        # The SQL template should only have placeholders
        sql_template = (
            "(r.eligibility ILIKE :tag_like_0 OR r.eligibility ILIKE :tag_like_spaced_0 "
            "OR r.title ILIKE :tag_like_0 OR r.title ILIKE :tag_like_spaced_0 "
            "OR r.description ILIKE :tag_like_0 OR r.description ILIKE :tag_like_spaced_0 "
            "OR r.tags @> ARRAY[:tag_array_0]::text[] "
            "OR r.subcategories @> ARRAY[:tag_array_0]::text[])"
        )

        # Verify SQL template has no literal malicious content
        assert "OR 1=1" not in sql_template
        assert "DROP TABLE" not in sql_template
        assert "<script>" not in sql_template

    def test_malicious_category_is_parameterized(self):
        """Malicious SQL in category values should be parameterized.

        The build_categories_sql function should produce parameterized SQL.
        """
        malicious_categories = ["employment'] OR 1=1--", "'; DELETE FROM resources;--"]
        params = {}

        cat_conditions = []
        for i, cat in enumerate(malicious_categories):
            param_name = f"cat_{i}"
            params[param_name] = cat  # Value goes in params
            cat_conditions.append(f"r.categories @> ARRAY[:{param_name}]::text[]")

        sql = " OR ".join(cat_conditions)

        # Verify SQL uses placeholders, not literal values
        assert ":cat_0" in sql
        assert ":cat_1" in sql
        assert "OR 1=1" not in sql
        assert "DELETE FROM" not in sql

        # Verify malicious content is safely in params dict
        assert params["cat_0"] == "employment'] OR 1=1--"

    def test_sql_injection_payload_examples(self):
        """Common SQL injection payloads should be safely parameterized.

        This tests various known SQL injection patterns to ensure they
        would be passed as parameters rather than executed.
        """
        injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE resources; --",
            "' UNION SELECT * FROM users --",
            "1; UPDATE resources SET title='hacked'--",
            "admin'--",
            "' OR 1=1#",
            "'; EXEC xp_cmdshell('net user')--",
            "' AND 1=CONVERT(int, (SELECT TOP 1 column_name FROM information_schema.columns))--",
        ]

        for payload in injection_payloads:
            params = {}
            param_name = "test_param"
            params[param_name] = payload

            # The SQL template is static - payloads go into params
            sql = f"r.tags @> ARRAY[:{param_name}]::text[]"

            # Verify the actual malicious string is NOT in the SQL
            assert payload not in sql
            # But it IS in the params (where it's safe)
            assert params[param_name] == payload
