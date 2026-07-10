"""Validation helper functions checking conversation ownership and states.
"""

import uuid

from app.database.models import Conversation
from app.database.models.enums import ConversationStatus
from app.conversation.domain.exceptions import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
    ConversationValidationError,
)


class ConversationValidator:
    """Enforces boundaries and rules constraints checking conversation state values."""

    @staticmethod
    def validate_exists(conversation: Conversation) -> None:
        """Verifies if conversation thread is present and not soft-deleted.

        Args:
            conversation: The conversation DB entity instance.
        """
        if not conversation or conversation.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

    @staticmethod
    def validate_ownership(conversation: Conversation, user_id: uuid.UUID) -> None:
        """Verifies if conversation is owned by the request user ID.

        Args:
            conversation: The conversation DB entity instance.
            user_id: The request user identifier claims.
        """
        if conversation.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

    @staticmethod
    def validate_active(conversation: Conversation) -> None:
        """Verifies that conversation is active and not archived.

        Args:
            conversation: The conversation DB entity instance.
        """
        if conversation.status == ConversationStatus.ARCHIVED.value:
            raise ConversationValidationError("Cannot modify an archived conversation.")
