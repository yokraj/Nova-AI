"""Metadata descriptors describing Software Engineering Agent profiles.
"""

from typing import List
from pydantic import Field

from app.agent_sdk.metadata import SDKMetadata


class SoftwareEngineerMetadata(SDKMetadata):
    """Metadata detailing identity and tech-stack capabilities of the Software Engineering Agent."""

    version: str = Field("1.0.0", description="Agent implementation version.")
    description: str = Field("Expert software engineer agent foundation.")
    author: str = Field("Nova AI Team")
    supported_languages: List[str] = Field(
        default_factory=lambda: ["python", "javascript", "typescript", "go", "rust", "html", "css"]
    )
    supported_frameworks: List[str] = Field(
        default_factory=lambda: ["fastapi", "nextjs", "react", "django", "express"]
    )
    supported_tools: List[str] = Field(default_factory=lambda: ["git", "pytest", "npm", "uv", "pip"])
    capabilities: List[str] = Field(default_factory=list)
