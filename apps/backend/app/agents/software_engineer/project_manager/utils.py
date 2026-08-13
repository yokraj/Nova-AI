"""Utility helpers for the Project Manager Engine.
"""

import hashlib
import json
from typing import Any, Dict

def calculate_hash(content: str) -> str:
    """Calculates the SHA-256 hash of a string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def format_json(data: Dict[str, Any]) -> str:
    """Formats a dictionary to a pretty JSON string."""
    return json.dumps(data, indent=2)
