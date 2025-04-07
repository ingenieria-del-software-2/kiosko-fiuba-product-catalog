"""Helper module for generating URL-friendly slugs."""

import re

from slugify import slugify as base_slugify


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug.

    Args:
        text: The text to convert

    Returns:
        A URL-friendly slug
    """
    # Handle camel case by adding spaces before capital letters
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)

    # Use the base slugify function with specific options
    result: str = base_slugify(text, separator="-", lowercase=True)
    return result
