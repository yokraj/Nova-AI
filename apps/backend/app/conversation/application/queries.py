"""Application CQRS queries for the Conversation bounded context.

Defines parameters structures for reading conversation states and listings.
"""

import uuid
from pydantic import BaseModel, Field


class GetConversationQuery(BaseModel):
    """Query parameters to fetch conversation metadata details."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")


class ListConversationsQuery(BaseModel):
    """Query parameters to list conversation summaries for a specific User."""

    user_id: uuid.UUID = Field(..., description="Target User UUID.")


class GetMessagesQuery(BaseModel):
    """Query parameters to retrieve messages list for a conversation."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")
