"""Conversation domain model for Nova AI.

Redirects imports to database models package to maintain consistency.
"""

from app.database.models.conversation import Conversation

__all__ = ["Conversation"]
