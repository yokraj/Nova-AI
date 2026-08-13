"""Utility helpers for the Deployment Engine.
"""

import hashlib
import os
from typing import Any, Dict

def calculate_checksum(file_path: str) -> str:
    """Calculates the SHA-256 checksum of a file."""
    if not os.path.exists(file_path):
        return ""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def calculate_content_checksum(content: str) -> str:
    """Calculates the SHA-256 checksum of raw text content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def write_deployment_file(path: str, content: str) -> str:
    """Writes content to target path, ensuring directories exist. Returns path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
