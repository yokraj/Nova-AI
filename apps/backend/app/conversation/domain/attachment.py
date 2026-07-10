"""Attachment domain model for Nova AI.

Redirects imports to database models package to maintain consistency.
"""

from app.database.models.attachment import Attachment

__all__ = ["Attachment"]
