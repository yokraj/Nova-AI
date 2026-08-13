"""Helper utilities for file copying, string manipulation and diff calculations.
"""

import difflib
import os
import shutil
from typing import List


def compute_unified_diff(original: str, modified: str, filename: str = "") -> str:
    """Generates standard unified diff lines between original and modified strings.

    Args:
        original: Original string content.
        modified: Modified string content.
        filename: Optional name of the file being compared.

    Returns:
        Unified diff string.
    """
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"a/{filename}" if filename else "original",
        tofile=f"b/{filename}" if filename else "modified",
    )
    return "".join(diff)


def backup_file(src_path: str, backup_dir: str, relative_path: str) -> str:
    """Copies file from src_path preserving subdirectories structure under backup_dir.

    Args:
        src_path: Source file absolute path.
        backup_dir: Absolute path of target backup directory.
        relative_path: Source file relative path.

    Returns:
        Absolute path of copied file inside backup_dir.
    """
    dest_path = os.path.join(backup_dir, relative_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)
    return dest_path


def restore_file(backup_path: str, orig_path: str) -> None:
    """Copies file back to its original location.

    Args:
        backup_path: Backed up file absolute path.
        orig_path: Original location absolute path.
    """
    os.makedirs(os.path.dirname(orig_path), exist_ok=True)
    shutil.copy2(backup_path, orig_path)
