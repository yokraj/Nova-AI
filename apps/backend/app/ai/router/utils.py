"""Utility helpers for the model router.
"""

import hashlib

def calculate_prompt_hash(prompt: str) -> str:
    """Computes SHA-256 hash of a prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()
