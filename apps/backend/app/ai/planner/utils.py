"""Utility helper functions for the Planner subsystem.
"""

import uuid

def generate_uuid() -> str:
    """Returns a unique string representation identifier."""
    return str(uuid.uuid4())
