"""Utility helper functions for AST traversal and file loading.
"""

import os


def load_file_safely(file_path: str) -> str:
    """Reads file text content with automatic Latin-1 fallback for encoding issues.

    Args:
        file_path: Absolute or relative file path on disk.

    Returns:
        Full file content string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        return ""


def clean_docstring(docstring: Optional[str]) -> Optional[str]:
    """Trims whitespace and cleans documentation string.

    Args:
        docstring: Raw docstring text.

    Returns:
        Cleaned docstring string, or None.
    """
    if not docstring:
        return None
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation of non-blank lines (except first line)
    margin = 999999
    for line in lines[1:]:
        content = len(line) - len(line.lstrip())
        if line.strip() and content < margin:
            margin = content

    trimmed = [lines[0].strip()]
    if margin < 999999:
        for line in lines[1:]:
            trimmed.append(line[margin:].rstrip())

    # Strip empty lines from both ends
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    while trimmed and not trimmed[-1]:
        trimmed.pop()

    return "\n".join(trimmed) if trimmed else None


def get_source_snippet(source_code: str, start_line: int, end_line: Optional[int]) -> Optional[str]:
    """Extracts a slice of source code representing a symbol definition.

    Args:
        source_code: Complete file source code.
        start_line: 1-indexed start line number.
        end_line: 1-indexed end line number.

    Returns:
        Snippet string or None.
    """
    if not source_code:
        return None
    lines = source_code.splitlines()
    end = end_line if end_line is not None else start_line
    # Bounds safety
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end)
    if start_idx < len(lines):
        return "\n".join(lines[start_idx:end_idx])
    return None
