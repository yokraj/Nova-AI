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
from app.agents.software_engineer.repository.analyzer import RepositoryAnalyzer
from app.agents.software_engineer.intelligence.analyzer import CodeIntelligenceAnalyzer
from app.agents.software_engineer.generator.generator import LocalCodeGenerator
from app.agents.software_engineer.refactoring.engine import LocalRefactoringEngine
from app.agents.software_engineer.testing.engine import LocalTestingEngine
from app.agents.software_engineer.debugging.engine import LocalDebuggingEngine
from app.agents.software_engineer.documentation.engine import LocalDocumentationEngine


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
        workspace_root = None
        if self.configuration.settings.get("workspace_root"):
            workspace_root = self.configuration.settings["workspace_root"]
        elif hasattr(self.configuration, "workspace_root") and self.configuration.workspace_root:
            workspace_root = self.configuration.workspace_root

        self.repository_analyzer = RepositoryAnalyzer(workspace_root=workspace_root)
        self.code_intelligence = CodeIntelligenceAnalyzer(workspace_root=workspace_root)

        try:
            from app.ai.gateway import AIGateway
            from app.core.dependency_container import resolve
            gateway = resolve(AIGateway)
        except Exception:
            gateway = None

        self.code_generator = LocalCodeGenerator(gateway=gateway, workspace_root=workspace_root)
        self.refactoring = LocalRefactoringEngine(gateway=gateway, workspace_root=workspace_root)
        self.testing = LocalTestingEngine(gateway=gateway, workspace_root=workspace_root)
        self.debugger = LocalDebuggingEngine(gateway=gateway, workspace_root=workspace_root)
        self.documentation = LocalDocumentationEngine(gateway=gateway, workspace_root=workspace_root)

        from app.agents.software_engineer.deployment.engine import LocalDeploymentEngine
        self._deployment = LocalDeploymentEngine(gateway=gateway, workspace_root=workspace_root)

        from app.agents.software_engineer.project_manager.engine import LocalProjectManagerEngine
        self._project_manager = LocalProjectManagerEngine(gateway=gateway, workspace_root=workspace_root)

        from app.agents.software_engineer.autonomous.engine import LocalAutonomousEngine
        self._autonomous = LocalAutonomousEngine(agent=self, gateway=gateway, workspace_root=workspace_root)

        from app.ai.memory.engine import LocalMemoryEngine
        self.memory = LocalMemoryEngine()

        from app.ai.voice.engine import LocalVoiceEngine
        self.voice = LocalVoiceEngine()

        from app.ai.vision.engine import LocalVisionEngine
        self._vision = LocalVisionEngine(gateway=gateway, memory_engine=self.memory)

        from app.ai.automation.engine import LocalAutomationEngine
        self._automation = LocalAutomationEngine(gateway=gateway, memory_engine=self.memory)

        if workspace_root:
            self.workspace_manager.open_workspace(workspace_root)
            self.session.workspace = workspace_root

        # Auto-register to multi-agent foundation registry
        if gateway and hasattr(gateway, "agents"):
            try:
                from app.ai.agents.models import AgentDescriptor, AgentMetadata as FndAgentMetadata, AgentCapability as FndAgentCapability
                new_meta = FndAgentMetadata(
                    id="software_engineer",
                    name="Software Engineer",
                    type="software_engineer",
                    capabilities=[
                        FndAgentCapability(name="code_generation", description="Generate high quality code"),
                        FndAgentCapability(name="debugging", description="Debug application issues"),
                        FndAgentCapability(name="testing", description="Write and execute tests"),
                        FndAgentCapability(name="documentation", description="Generate documentation")
                    ],
                    permissions=["Filesystem", "Developer"]
                )
                desc = AgentDescriptor(
                    class_path="app.agents.software_engineer.agent.SoftwareEngineerAgent",
                    dependencies=[]
                )
                if not gateway.agents.registry.exists(new_meta.id):
                    gateway.agents.registry.register(desc, new_meta)
            except Exception:
                pass

    @property
    def automation(self) -> Any:
        """Exposes the desktop automation engine for computer controls actions."""
        return self._automation

    @property
    def vision(self) -> Any:
        """Exposes the vision engine for autonomous screen/image visual understanding."""
        return self._vision

    @property
    def deployment(self) -> Any:
        """Exposes the deployment engine for autonomous deployment preparations."""
        return self._deployment

    @property
    def project_manager(self) -> Any:
        """Exposes the project manager engine for autonomous software project management."""
        return self._project_manager

    @property
    def autonomous(self) -> Any:
        """Exposes the autonomous integration engine workflow."""
        return self._autonomous

    @property
    def conversation_memory(self) -> Any:
        """Exposes the conversation memory."""
        return self.memory.conversation

    @property
    def project_memory(self) -> Any:
        """Exposes the project memory."""
        return self.memory.project

    @property
    def code_memory(self) -> Any:
        """Exposes the code memory."""
        return self.memory.code

    @property
    def voice_engine(self) -> Any:
        """Exposes the voice engine."""
        return self.voice

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
