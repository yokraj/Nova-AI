"""Utility helper functions for the memory package.
"""

import hashlib

def calculate_text_hash(text: str) -> str:
    """Computes SHA-256 hash value of a text block."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
