"""Abstract interface contracts for Multi-Agent Collaboration & Swarm Intelligence Engine."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.swarm.models import (
    BlackboardEntry,
    ConsensusDecision,
    SwarmAgentRecord,
    SwarmHealth,
    SwarmMessage,
    SwarmMetrics,
    SwarmMissionGraph,
    SwarmResult,
    SwarmTask,
    VoteRecord,
)


class IAgentRegistry(ABC):
    """Abstract contract for swarm agent discovery and capability registration."""

    @abstractmethod
    def register_agent(self, agent: SwarmAgentRecord) -> None:
        pass

    @abstractmethod
    def find_agents_by_role(self, role: str) -> List[SwarmAgentRecord]:
        pass

    @abstractmethod
    def list_all_agents(self) -> List[SwarmAgentRecord]:
        pass


class ITaskDecomposer(ABC):
    """Abstract contract for decomposing complex goals into task graphs."""

    @abstractmethod
    async def decompose_goal(self, goal: str) -> SwarmMissionGraph:
        pass


class IConsensusEngine(ABC):
    """Abstract contract for voting and reaching consensus across agents."""

    @abstractmethod
    async def reach_consensus(self, votes: List[VoteRecord], strategy: str = "majority") -> ConsensusDecision:
        pass


class ISharedBlackboard(ABC):
    """Abstract contract for inter-agent shared blackboard state."""

    @abstractmethod
    async def write(self, key: str, value: Any, author_agent_id: str) -> BlackboardEntry:
        pass

    @abstractmethod
    async def read(self, key: str) -> Optional[Any]:
        pass


class ILoadBalancer(ABC):
    """Abstract contract for agent work allocation and load balancing."""

    @abstractmethod
    async def allocate_task(self, task: SwarmTask) -> SwarmAgentRecord:
        pass


class ISwarmEngine(ABC):
    """Abstract contract for central Swarm Intelligence facade."""

    @abstractmethod
    async def create_swarm(self, goal: str) -> str:
        pass

    @abstractmethod
    async def execute_swarm(self, swarm_id: str) -> SwarmResult:
        pass

    @abstractmethod
    async def get_metrics(self) -> SwarmMetrics:
        pass

    @abstractmethod
    def check_health(self) -> SwarmHealth:
        pass
