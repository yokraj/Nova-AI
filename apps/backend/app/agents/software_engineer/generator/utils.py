"""Utility helpers including markdown code blocks extractors.
"""

import re
from typing import Optional


def extract_code_block(raw_text: str, language: str = "python") -> str:
    """Strips markdown code blocks wrapping LLM responses.

    Args:
        raw_text: Raw model generation content.
        language: Language format (e.g. 'python').

    Returns:
        Extracted raw code string.
    """
    if not raw_text:
        return ""

    # Look for ```python or ```LANG blocks first
    pattern = rf"```(?:{language})?\n(.*?)\n```"
    match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback to generic ``` block
    pattern_generic = r"```\n(.*?)\n```"
    match_generic = re.search(pattern_generic, raw_text, re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()

    # If no markdown blocks, return raw text cleaned
    return raw_text.strip()


def resolve_placeholders(template_content: str, variables: dict) -> str:
    """Helper replacing standard {{VariableName}} placeholders with mapping keys.

    Args:
        template_content: String containing templates placeholders.
        variables: Key-value substitutions dictionary.

    Returns:
        Rendered text.
    """
    rendered = template_content
    for key, val in variables.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(val))
    return rendered
