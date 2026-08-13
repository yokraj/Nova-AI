"""Utility formatting routines and stack trace string helpers.
"""

import ast
import re
from typing import Optional, Tuple


def safe_parse_ast(code: str, file_name: str = "temp_debug.py") -> Tuple[bool, Optional[str]]:
    """Tries parsing python code to look for syntax errors.

    Args:
        code: Python source code string.
        file_name: Dummy filename.

    Returns:
        Tuple (is_success, error_message).
    """
    try:
        ast.parse(code, filename=file_name)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
    except Exception as e:
        return False, str(e)


def clean_stack_trace_str(traceback_str: str) -> str:
    """Standardizes windows or linux newline breaks in stack traces.

    Args:
        traceback_str: Raw traceback message text.

    Returns:
        Cleaned traceback string.
    """
    if not traceback_str:
        return ""
    # Standardize carriage returns
    cleaned = traceback_str.replace("\r\n", "\n")
    # Truncate overly large stack messages
    if len(cleaned) > 25000:
        cleaned = cleaned[:10000] + "\n... [TRUNCATED] ...\n" + cleaned[-10000:]
    return cleaned
