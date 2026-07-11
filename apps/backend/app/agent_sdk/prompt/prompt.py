"""Prompt data model representing standard prompt attributes.
"""

from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class Prompt(BaseModel):
    """Represents a validated prompt template structure."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique prompt identifier.")
    name: str = Field(..., description="The name of the prompt template.")
    category: str = Field(..., description="Category folder path (e.g., 'software', 'browser').")
    description: str = Field("", description="A description of the prompt's purpose.")
    system_prompt: str = Field("", description="System instructions prompt template.")
    user_prompt: str = Field("", description="User request prompt template.")
    variables: List[str] = Field(default_factory=list, description="List of template variables needed.")
    version: str = Field("v1", description="Version identifier string (e.g., 'v1').")
    language: str = Field("en", description="Target language identifier (e.g., 'en').")
    tags: List[str] = Field(default_factory=list, description="Categorization tags list.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata parameters.")
