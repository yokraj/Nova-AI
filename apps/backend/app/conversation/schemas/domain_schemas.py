"""Validation schemas definitions for Conversation HTTP requests and responses DTOs.
"""

from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    """Payload representing file attachment metadata details."""

    id: uuid.UUID
    message_id: uuid.UUID
    name: str
    type: str
    url: str
    size: int
    created_at: datetime


class MessageRequest(BaseModel):
    """Payload to post/append a new chat message."""

    role: str = Field(..., description="Role actor: user, assistant, system.")
    content: str = Field(..., description="Content text.")


class MessageResponse(BaseModel):
    """Payload returned representing message details."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    token_count: int
    created_at: datetime
    attachments: List[AttachmentResponse] = []


class ConversationRequest(BaseModel):
    """Payload to create or update a conversation thread."""

    title: str = Field(..., min_length=1, max_length=255, description="Thread header title.")


class ConversationResponse(BaseModel):
    """Payload returned representing conversation thread metadata details."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    status: str
    created_at: datetime
    updated_at: datetime


class ConversationSummary(BaseModel):
    """Brief metadata summary representing a conversation entry item."""

    id: uuid.UUID
    title: str
    status: str
    last_message_at: Optional[datetime] = None
    created_at: datetime
