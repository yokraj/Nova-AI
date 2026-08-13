"""Helper utilities for test execution, file parsing, and subprocess workers management.
"""

import ast
import os
import subprocess
from typing import Optional, Tuple


def safe_compile_code(code: str, file_name: str = "temp_test.py") -> Tuple[bool, Optional[str]]:
    """Compiles source code to check for syntax errors before running or saving.

    Args:
        code: Source code content.
        file_name: Name of target file.

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


def run_subprocess_command(
    args: list[str], cwd: str, timeout: float = 30.0
) -> Tuple[int, str, str]:
    """Runs a subprocess command capturing output.

    Args:
        args: Command line argument array.
        cwd: Target working directory path.
        timeout: Timeout duration in seconds.

    Returns:
        Tuple (exit_code, stdout, stderr).
    """
    try:
        res = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired as e:
        return -1, e.stdout or "", e.stderr or f"Timeout expired after {timeout} seconds."
    except Exception as e:
        return -2, "", str(e)
