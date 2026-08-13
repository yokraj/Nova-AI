"""Utility helper functions for the voice package.
"""

import hashlib

def calculate_audio_hash(audio_bytes: bytes) -> str:
    """Computes SHA-256 hash value of audio input."""
    return hashlib.sha256(audio_bytes).hexdigest()
