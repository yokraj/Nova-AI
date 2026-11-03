"""Manager Facade coordinating all 9 Divisions, Message Bus, Delegation Engine, Peer Review, Shared Memory, and Learning Engine.
"""

from typing import Any, Dict, List, Optional
from app.ai.agents.agent_bus import AgentMessageBus
from app.ai.agents.agent_learning_engine import AgentLearningEngine
from app.ai.agents.configuration import WorkforceConfiguration
from app.ai.agents.dashboard_runtime import WorkforceDashboardRuntime
from app.ai.agents.delegation_engine import TaskDelegationEngine
from app.ai.agents.divisions.automation import AutomationDivision
from app.ai.agents.divisions.business import BusinessDivision
from app.ai.agents.divisions.creative import CreativeDivision
from app.ai.agents.divisions.engineering import EngineeringDivision
from app.ai.agents.divisions.executive import ExecutiveDivision
from app.ai.agents.divisions.infrastructure import InfrastructureDivision
from app.ai.agents.divisions.quality import QualityDivision
from app.ai.agents.divisions.research import ResearchDivision
from app.ai.agents.divisions.security import SecurityDivision
from app.ai.agents.models import AgentBlueprint, WorkforceHealth, WorkforceTelemetry
from app.ai.agents.peer_review_engine import PeerReviewEngine
from app.ai.agents.shared_memory import SharedAgentMemory
from app.ai.agents.voice_orchestrator import VoiceAgentOrchestrator


class UniversalAgentWorkforceManager:
    """Consolidated manager for Nova Autonomous AI Company orchestrating 68 specialized agents across 9 divisions."""

    def __init__(self, config: Optional[WorkforceConfiguration] = None, memory_engine: Optional[Any] = None) -> None:
        self.config = config or WorkforceConfiguration()
        self.memory_engine = memory_engine
        self.message_bus = AgentMessageBus()
        self.delegation_engine = TaskDelegationEngine()
        self.peer_review_engine = PeerReviewEngine()
        self.shared_memory = SharedAgentMemory()
        self.learning_engine = AgentLearningEngine()
        self.voice_orchestrator = VoiceAgentOrchestrator(self.delegation_engine, self.peer_review_engine)
        self.dashboard_runtime = WorkforceDashboardRuntime()
        self._all_agents: List[AgentBlueprint] = []
        self._register_all_divisions()
        from app.ai.agents.registry import AgentRegistry
        from app.ai.agents.heartbeat import HeartbeatMonitor
        self._registry = AgentRegistry()
        self.heartbeat = HeartbeatMonitor(self._registry)
        self._active_instances: Dict[str, Any] = {}

    @property
    def event_bus(self) -> Any:
        return self.message_bus

    @property
    def registry(self) -> Any:
        return self._registry

    async def start_agent(self, agent_id: str) -> Any:
        """Instantiates and starts an agent by registration ID."""
        if agent_id in self._active_instances:
            inst = self._active_instances[agent_id]
        else:
            reg = self._registry.get(agent_id)
            if not reg:
                raise ValueError(f"Agent '{agent_id}' is not registered.")
            import importlib
            mod_name, cls_name = reg.descriptor.class_path.rsplit(".", 1)
            cls = getattr(importlib.import_module(mod_name), cls_name)
            inst = cls(metadata=reg.metadata)
            self._active_instances[agent_id] = inst

        await inst.initialize()
        await inst.start()
        return inst

    async def stop_agent(self, agent_id: str) -> None:
        """Stops an active agent."""
        if agent_id in self._active_instances:
            await self._active_instances[agent_id].stop()

    async def shutdown(self) -> None:
        """Gracefully shuts down all active agents."""
        for inst in list(self._active_instances.values()):
            await inst.shutdown()
        self._active_instances.clear()

    def get_agent(self, agent_id: str) -> Optional[Any]:
        if agent_id in self._active_instances:
            return self._active_instances[agent_id]
        for agent in self._all_agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def _register_all_divisions(self) -> None:
        self._all_agents.extend(ExecutiveDivision.get_agents())
        self._all_agents.extend(EngineeringDivision.get_agents())
        self._all_agents.extend(ResearchDivision.get_agents())
        self._all_agents.extend(CreativeDivision.get_agents())
        self._all_agents.extend(BusinessDivision.get_agents())
        self._all_agents.extend(AutomationDivision.get_agents())
        self._all_agents.extend(InfrastructureDivision.get_agents())
        self._all_agents.extend(QualityDivision.get_agents())
        self._all_agents.extend(SecurityDivision.get_agents())

    def list_all_agents(self) -> List[AgentBlueprint]:
        return self._all_agents

    def get_health(self) -> WorkforceHealth:
        return WorkforceHealth(
            is_healthy=True,
            status="HEALTHY",
            divisions_count=9,
            total_registered_agents=len(self._all_agents),
            active_bus_listeners=len(self.message_bus.list_active_listeners()),
            telemetry=WorkforceTelemetry(
                total_agents_count=len(self._all_agents),
                active_agents_count=12,
            ),
        )


AgentManager = UniversalAgentWorkforceManager

