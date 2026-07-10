"""Application CQRS commands for the Conversation bounded context.

Defines input parameter schemas driving state modification workflows.
"""

from typing import List, Optional
import uuid
from pydantic import BaseModel, Field


class AttachmentPayload(BaseModel):
    """Payload representing a file attachment to be uploaded/saved."""

    name: str = Field(..., description="Name of the file.")
    type: str = Field(..., description="AttachmentType: file, image, code, pdf.")
    url: str = Field(..., description="Public download path of attachment.")
    size: int = Field(..., description="Size in bytes.")


class CreateConversationCommand(BaseModel):
    """Command parameters to initialize a new conversation thread."""

    user_id: uuid.UUID = Field(..., description="Unique User UUID.")
    title: str = Field(..., min_length=1, max_length=255, description="Initial title.")


class SendMessageCommand(BaseModel):
    """Command parameters to append a message inside a conversation thread."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")
    role: str = Field(..., description="Actor role: user, assistant, system.")
    content: str = Field(..., description="Text content body.")
    attachments: Optional[List[AttachmentPayload]] = Field(
        None, description="Optional uploaded file attachments."
    )


class RenameConversationCommand(BaseModel):
    """Command parameters to rename conversation title description."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")
    title: str = Field(..., min_length=1, max_length=255, description="New title.")


class ArchiveConversationCommand(BaseModel):
    """Command parameters to archive a conversation thread."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")


class DeleteConversationCommand(BaseModel):
    """Command parameters to soft/hard delete a conversation thread."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")


class RestoreConversationCommand(BaseModel):
    """Command parameters to restore an archived or deleted conversation thread."""

    conversation_id: uuid.UUID = Field(..., description="Target Conversation UUID.")
