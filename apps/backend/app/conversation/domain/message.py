"""Message domain model for Nova AI.

Redirects imports to database models package to maintain consistency.
"""

from app.database.models.message import Message

__all__ = ["Message"]
