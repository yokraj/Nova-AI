"""SDKContext schema defining agent execution request parameters.
"""

from typing import Optional
import uuid
from pydantic import BaseModel, Field


class SDKContext(BaseModel):
    """Execution context for an agent running via the Agent SDK."""

    user_id: str = Field(..., description="ID of the user initiating the task.")
    conversation_id: uuid.UUID = Field(..., description="Session/conversation identifier.")
    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the specific request.")
    ai_provider: str = Field(..., description="AI model provider name (e.g. 'ollama').")
    selected_model: str = Field(..., description="Name of the target AI model.")
    locale: str = Field("en-US", description="Target locale for translations.")
    timezone: str = Field("UTC", description="Target timezone context.")
