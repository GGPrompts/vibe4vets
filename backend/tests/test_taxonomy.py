"""Taxonomy tests."""

from app.core.taxonomy import (
    CATEGORIES,
    SUBCATEGORIES,
    get_category,
    get_reliability_score,
    get_subcategories,
    is_valid_category,
    is_valid_subcategory,
)


def test_categories_defined():
    """Test that all required categories are defined."""
    assert "employment" in CATEGORIES
    assert "training" in CATEGORIES
    assert "housing" in CATEGORIES
    assert "legal" in CATEGORIES
    assert "benefits" in CATEGORIES
    assert "food" in CATEGORIES
    assert "mentalHealth" in CATEGORIES
    assert "supportServices" in CATEGORIES
    assert "healthcare" in CATEGORIES
    assert "education" in CATEGORIES
    assert "financial" in CATEGORIES
    assert len(CATEGORIES) == 11


def test_subcategories_have_valid_parents():
    """Test that all subcategories reference valid categories."""
    for subcategory in SUBCATEGORIES.values():
        assert subcategory.category_id in CATEGORIES


def test_get_category():
    """Test get_category function."""
    category = get_category("employment")
    assert category is not None
    assert category.id == "employment"
    assert category.name == "Employment"

    assert get_category("nonexistent") is None


def test_get_subcategories():
    """Test get_subcategories function."""
    employment_subs = get_subcategories("employment")
    assert len(employment_subs) > 0
    for sub in employment_subs:
        assert sub.category_id == "employment"

    housing_subs = get_subcategories("housing")
    assert len(housing_subs) > 0
    assert "hud-vash" in [s.id for s in housing_subs]


def test_is_valid_category():
    """Test is_valid_category function."""
    assert is_valid_category("employment") is True
    assert is_valid_category("training") is True
    assert is_valid_category("invalid") is False


def test_is_valid_subcategory():
    """Test is_valid_subcategory function."""
    assert is_valid_subcategory("hud-vash") is True
    assert is_valid_subcategory("hud-vash", "housing") is True
    assert is_valid_subcategory("hud-vash", "employment") is False
    assert is_valid_subcategory("invalid") is False


def test_get_reliability_score():
    """Test get_reliability_score function."""
    assert get_reliability_score(1) == 1.0
    assert get_reliability_score(2) == 0.8
    assert get_reliability_score(3) == 0.6
    assert get_reliability_score(4) == 0.4
    assert get_reliability_score(99) == 0.0
