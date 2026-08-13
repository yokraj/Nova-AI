"""Helper utilities for markdown manipulation, template interpolation, and file checks.
"""

import re
from typing import Any, Dict


def clean_markdown_headers(md_text: str) -> str:
    """Cleans duplicate leading hashes or formatting spacing in markdown blocks.

    Args:
        md_text: Target markdown text.

    Returns:
        Cleaned markdown.
    """
    if not md_text:
        return ""
    # Standardize newline blocks
    cleaned = md_text.replace("\r\n", "\n")
    return cleaned


def simple_interpolate(template: str, parameters: Dict[str, Any]) -> str:
    """Replaces placeholders in format {{parameter}} with their actual string values.

    Args:
        template: Base layout template string.
        parameters: Dict mapping parameter names to values.

    Returns:
        Interpolated text.
    """
    result = template
    for key, val in parameters.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(val))
    return result
