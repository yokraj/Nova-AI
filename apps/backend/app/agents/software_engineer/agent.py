"""SoftwareEngineerAgent class inheriting from BaseAgent and BaseAgentSDK.
"""

import time
from typing import Any, Dict, Optional

from app.agent_sdk.base_sdk import BaseAgentSDK
from app.agents.base import AgentContext, AgentMetadata, AgentResult, BaseAgent
from app.agents.software_engineer.configuration import SoftwareEngineerConfiguration
from app.agents.software_engineer.health import HealthProvider
from app.agents.software_engineer.metadata import SoftwareEngineerMetadata
from app.agents.software_engineer.session import SoftwareEngineerSession
from app.agents.software_engineer.state import SoftwareEngineerState
from app.agents.software_engineer.workspace import WorkspaceManager


class HybridMetadata:
    """Combines SDKMetadata and AgentMetadata into a single attribute-accessible object."""

    def __init__(self, sdk_meta: SoftwareEngineerMetadata, agent_meta: AgentMetadata) -> None:
        """Initializes HybridMetadata.

        Args:
            sdk_meta: The SoftwareEngineerMetadata descriptor.
            agent_meta: The AgentMetadata profile details.
        """
        self._sdk_meta = sdk_meta
        self._agent_meta = agent_meta

    def __getattr__(self, name: str) -> Any:
        """Proxies attribute lookups to either metadata instance."""
        if name in ("id", "name", "capabilities", "permissions"):
            return getattr(self._agent_meta, name)
        return getattr(self._sdk_meta, name)


class SoftwareEngineerAgent(BaseAgent, BaseAgentSDK):
    """The enterprise Software Engineering Agent."""

    def __init__(
        self,
        metadata: SoftwareEngineerMetadata,
        configuration: Optional[SoftwareEngineerConfiguration] = None,
    ) -> None:
        """Initializes SoftwareEngineerAgent.

        Args:
            metadata: Identity metadata model.
            configuration: Initial configuration schema model.
        """
        self._sdk_metadata: Optional[SoftwareEngineerMetadata] = None

        # Initialize BaseAgentSDK
        BaseAgentSDK.__init__(self, metadata, configuration)

        from app.agents.base import AgentCapability, AgentPermission

        agent_meta = AgentMetadata(
            name=metadata.agent_name,
            version=metadata.version,
            description=metadata.description,
            capabilities=[AgentCapability.CODE],
            permissions=[AgentPermission.FILESYSTEM],
        )
        # Initialize BaseAgent
        BaseAgent.__init__(self, agent_meta)

        self.state = SoftwareEngineerState.IDLE
        self.workspace_manager = WorkspaceManager()
        self.session = SoftwareEngineerSession()
        self.health_provider = HealthProvider(self)

        # Open workspace if workspace_root is configured
        if self.configuration.settings.get("workspace_root"):
            self.workspace_manager.open_workspace(self.configuration.settings["workspace_root"])
            self.session.workspace = self.configuration.settings["workspace_root"]
        elif hasattr(self.configuration, "workspace_root") and self.configuration.workspace_root:
            self.workspace_manager.open_workspace(self.configuration.workspace_root)
            self.session.workspace = self.configuration.workspace_root

    @property
    def metadata(self) -> Any:
        """Hybrid metadata property combining BaseAgent and SDK attributes."""
        # If BaseAgent hasn't set self._metadata yet, fallback to sdk metadata dict proxies
        agent_meta = getattr(self, "_metadata", None)
        if not agent_meta:
            return self._sdk_metadata
        return HybridMetadata(self._sdk_metadata, agent_meta)

    @metadata.setter
    def metadata(self, value: Any) -> None:
        """Sets the SDK metadata instance."""
        self._sdk_metadata = value

    def update_state(self, new_state: SoftwareEngineerState) -> None:
        """Updates agent tracking status.

        Args:
            new_state: Target state Enum.
        """
        self.state = new_state

    async def initialize(self) -> None:
        """Initializes dependencies and starts lifecycle setup processes."""
        await BaseAgentSDK.initialize(self)

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        """Processes request prompt inside the given context.

        Args:
            context: Tracing AgentContext payload parameters.
            prompt: Instructions prompt string.

        Returns:
            AgentResult outcome telemetry.
        """
        start = time.perf_counter()
        duration = time.perf_counter() - start
        return AgentResult(
            success=True,
            response="Software Engineering Agent Foundation active.",
            metadata={"execution_time": duration},
            execution_time=duration,
        )

    async def shutdown(self) -> None:
        """Performs cleanup on resources and stops threads."""
        await BaseAgentSDK.shutdown(self)

    async def health(self) -> Dict[str, Any]:
        """Runs availability health diagnostics.

        Returns:
            Dictionary containing health diagnostic metrics.
        """
        sdk_health = BaseAgentSDK.health(self)
        return {
            "healthy": sdk_health.healthy,
            "uptime": sdk_health.uptime,
            "error_count": sdk_health.error_count,
            "workspace_loaded": bool(self.workspace_manager.current_workspace()),
            "active_tasks": len(self.session.active_tasks),
            "memory_usage_placeholder": 0.0,
            "status": self.state.value,
        }

    async def _on_startup(self) -> None:
        """Override callback called on initialization."""
        self.update_state(SoftwareEngineerState.THINKING)
        self._start_time = time.perf_counter()

    async def _on_shutdown(self) -> None:
        """Override callback called on shutdown."""
        self.update_state(SoftwareEngineerState.IDLE)
