"""User domain model mapping for Nova AI.

Redirects definition imports to the core database models package to maintain compatibility.
"""

from app.database.models.user import User  # noqa: F401
