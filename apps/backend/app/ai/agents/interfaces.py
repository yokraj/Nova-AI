"""Abstract base interfaces and contracts for Universal Agent Workforce & Autonomous AI Company.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.ai.agents.models import (
    AgentBlueprint,
    AgentLearningRecord,
    AgentMessage,
    MissionPlanDAG,
    PeerReviewRequest,
    PeerReviewResult,
    SharedMemoryItem,
    TaskNode,
    WorkforceHealth,
)


class IAgentMessageBus(ABC):
    """Contract for inter-agent communication bus."""

    @abstractmethod
    async def publish_message(self, message: AgentMessage) -> None:
        """Publishes message to inter-agent bus."""
        pass

    @abstractmethod
    def list_active_listeners(self) -> List[str]:
        """Lists active agent message listeners."""
        pass


class ITaskDelegationEngine(ABC):
    """Contract for task delegation and mission DAG planning."""

    @abstractmethod
    async def decompose_goal(self, goal: str) -> MissionPlanDAG:
        """Decomposes complex goal into hierarchical task DAG."""
        pass

    @abstractmethod
    async def execute_mission_dag(self, plan: MissionPlanDAG) -> Dict[str, Any]:
        """Executes mission DAG with parallel execution and dependency resolution."""
        pass


class IPeerReviewEngine(ABC):
    """Contract for multi-agent peer review quality gates."""

    @abstractmethod
    async def evaluate_deliverable(self, request: PeerReviewRequest) -> PeerReviewResult:
        """Enforces peer review flow across Code Review, Security, QA, and Performance agents."""
        pass


class ISharedAgentMemory(ABC):
    """Contract for cross-agent shared memory."""

    @abstractmethod
    def store(self, key: str, value: Any, author: str, category: str = "general") -> None:
        """Stores item in shared agent memory."""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieves item from shared agent memory."""
        pass


class IAgentLearningEngine(ABC):
    """Contract for autonomous pattern learning engine."""

    @abstractmethod
    def record_learning(self, pattern_name: str, steps: List[str]) -> AgentLearningRecord:
        """Persists successful workflow pattern."""
        pass


class IUniversalAgentWorkforceEngine(ABC):
    """Central facade contract for Nova Autonomous AI Company."""

    @abstractmethod
    async def execute_voice_mission(self, voice_prompt: str) -> Dict[str, Any]:
        """Executes complete voice-driven mission through Executive -> Divisions -> Review -> Delivery."""
        pass

    @abstractmethod
    def list_all_agents(self) -> List[AgentBlueprint]:
        """Lists all 68 specialized agents across 9 divisions."""
        pass

    @abstractmethod
    def get_workforce_health(self) -> WorkforceHealth:
        """Snapshot overall workforce health diagnostics."""
        pass
