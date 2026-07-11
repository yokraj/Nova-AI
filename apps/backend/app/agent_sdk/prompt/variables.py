"""PromptVariables container defining active session variables context.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PromptVariables(BaseModel):
    """Container for runtime variables used during prompt rendering."""

    user: str = Field("user", description="Active user ID.")
    user_name: str = Field("User", description="Active user name.")
    conversation: str = Field("", description="Conversation ID reference.")
    conversation_summary: str = Field("", description="Summarized history content.")
    selected_text: str = Field("", description="User selected text fragment.")
    clipboard: str = Field("", description="Clipboard buffer text.")
    active_application: str = Field("", description="Name of focused window process.")
    operating_system: str = Field("Windows", description="OS details.")
    language: str = Field("en", description="Active language.")
    timezone: str = Field("UTC", description="Active timezone.")
    voice_mode: str = Field("text", description="Voice interface mode.")
    current_model: str = Field("llama3", description="Currently active AI model.")
    provider: str = Field("ollama", description="Active provider adapter.")
    workspace: str = Field("", description="Focused workspace directory path.")
    project: str = Field("", description="Focused project name.")
    file: str = Field("", description="Focused file path.")
    code: str = Field("", description="Source code text.")
    custom: Dict[str, Any] = Field(default_factory=dict, description="Custom runtime mappings.")

    def to_dict(self) -> Dict[str, Any]:
        """Converts values to a flat dictionary for renderer substitution."""
        base = self.model_dump(exclude={"custom"})
        base.update(self.custom)
        return base
