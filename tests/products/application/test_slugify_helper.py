"""Tests for the slugify helper module."""

import pytest

from src.products.application.dtos.slugify_helper import slugify


@pytest.mark.parametrize(
    "input_text,expected_slug",
    [
        ("Test Product", "test-product"),
        ("Múltiple Wörds with Áccents", "multiple-words-with-accents"),
        ("Product  with   extra spaces", "product-with-extra-spaces"),
        ("Product @ with $pecial chars!", "product-with-pecial-chars"),
        ("", ""),
        ("123 456 789", "123-456-789"),
        ("UPPERCASE", "uppercase"),
        ("snake_case_text", "snake-case-text"),
        ("CamelCaseText", "camel-case-text"),
        (
            "Very-long-text-that-extends-beyond-normal-limits-and-might-cause-issues-in-some-systems",
            "very-long-text-that-extends-beyond-normal-limits-and-might-cause-issues-in-some-systems",
        ),
    ],
)
def test_slugify(input_text: str, expected_slug: str) -> None:
    """Test that the slugify function correctly converts text to URL-friendly slugs."""
    # Generate slug
    result = slugify(input_text)

    # Verify the result
    assert result == expected_slug

    # Check general slug properties
    if input_text:  # Skip empty string case
        assert "-" not in result[0]  # Should not start with a dash
        assert "-" not in result[-1]  # Should not end with a dash
        assert "--" not in result  # Should not have consecutive dashes

        # Only check lowercase if there are alphabetic characters
        if any(c.isalpha() for c in result):
            assert result.islower()  # Should be lowercase

        assert all(
            c.isalnum() or c == "-" for c in result
        )  # Only alphanumeric and dashes
