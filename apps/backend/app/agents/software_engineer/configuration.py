"""Configuration parameters for the Software Engineering Agent.
"""

from typing import Optional
from pydantic import Field

from app.agent_sdk.configuration import SDKConfiguration


class SoftwareEngineerConfiguration(SDKConfiguration):
    """Configuration class specific to the Software Engineering Agent."""

    default_model: str = Field("llama3", description="Default AI model name.")
    temperature: float = Field(0.2, description="Generation temperature.")
    max_tokens: int = Field(4096, description="Max generated tokens limit.")
    workspace_root: str = Field("", description="Root directory path of workspace.")
    allow_terminal: bool = Field(False)
    allow_browser: bool = Field(False)
    allow_filesystem: bool = Field(True)
    allow_git: bool = Field(False)
    allow_network: bool = Field(False)
    auto_save: bool = Field(True)
    context_window: int = Field(8192, description="Target model context window size.")
