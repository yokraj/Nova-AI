"""Agent Runtime Foundation base specifications and models.

Establishes the generic contracts, context metrics, results schemas,
and permission enums for every agent inside Nova AI.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


# ====================================================
# Enums
# ====================================================
class AgentCapability(str, Enum):
    """Enumerate capabilities supported by AI agents."""

    CHAT = "chat"
    CODE = "code"
    VISION = "vision"
    VOICE = "voice"
    BROWSER = "browser"
    DESKTOP = "desktop"
    DATABASE = "database"
    MEMORY = "memory"
    SEARCH = "search"
    WORKFLOW = "workflow"


class AgentPermission(str, Enum):
    """Enumerate permissions allowed to AI agents."""

    FILESYSTEM = "filesystem"
    NETWORK = "network"
    MICROPHONE = "microphone"
    CAMERA = "camera"
    SCREEN = "screen"
    BROWSER = "browser"
    TERMINAL = "terminal"
    CLIPBOARD = "clipboard"


# ====================================================
# Models
# ====================================================
class AgentMetadata(BaseModel):
    """Metadata configurations describing an AI agent profile."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique agent identifier.")
    name: str = Field(..., description="Unique human-readable name.")
    version: str = Field("0.1.0", description="SemVer version description string.")
    description: str = Field(..., description="Purpose description details of the agent.")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Capabilities supported.")
    permissions: List[AgentPermission] = Field(default_factory=list, description="Permissions allowed.")


class AgentContext(BaseModel):
    """Execution context tracing an active agent session request."""

    user_id: uuid.UUID = Field(..., description="Unique user identifier.")
    conversation_id: uuid.UUID = Field(..., description="Active thread identifier.")
    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Action tracing identifier.")
    ai_provider: Optional[str] = Field("ollama", description="Configured AI provider name.")
    selected_model: str = Field("llama3", description="Model selected for execution.")
    locale: str = Field("en-US", description="Target locale region identifier.")
    timezone: str = Field("UTC", description="Active timezone string.")


class AgentResult(BaseModel):
    """Telemetries and output responses returned by an agent run."""

    success: bool = Field(..., description="True if execute finished without errors.")
    response: str = Field(..., description="Final text result of agent execution.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metric telemetries and execution data.")
    execution_time: float = Field(..., description="Execution duration in seconds.")


# ====================================================
# Base Agent Contract
# ====================================================
class BaseAgent(ABC):
    """Abstract Base Class establish foundation lifecycle for all AI agents."""

    def __init__(self, metadata: AgentMetadata) -> None:
        """Initializes the Agent.

        Args:
            metadata: AgentMetadata profile details.
        """
        self._metadata = metadata

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes dependencies, configurations, or resources.

        Raises:
            Exception: If boot/setup phase fails.
        """
        pass

    @abstractmethod
    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        """Processes request prompt inside the given context.

        Args:
            context: Tracing AgentContext payload parameters.
            prompt: Instructions prompt string.

        Returns:
            AgentResult outputs.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Performs cleanup on resources and stops threads."""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Runs availability health diagnostics.

        Returns:
            Dictionary containing health diagnostic metrics.
        """
        pass

    @property
    def metadata(self) -> AgentMetadata:
        """Returns metadata properties of the agent.

        Returns:
            AgentMetadata schema.
        """
        return self._metadata
