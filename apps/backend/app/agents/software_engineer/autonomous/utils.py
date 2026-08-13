"""Utility helpers for the Autonomous Engine.
"""

import hashlib
import time

def calculate_checksum(content: str) -> str:
    """Calculates the SHA-256 checksum of a string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def get_current_timestamp() -> float:
    """Returns current epoch timestamp."""
    return time.time()
