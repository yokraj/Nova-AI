"""Abstract interfaces for the Autonomous Skill Execution Runtime."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.execution.models import (
    CheckpointData,
    ExecutionHealth,
    ExecutionMetrics,
    ExecutionStep,
    MissionExecutionPlan,
)


class IExecutionRuntime(ABC):
    """Abstract interface contract for central Execution Runtime facade."""

    @abstractmethod
    async def execute_mission(self, plan: MissionExecutionPlan) -> MissionExecutionPlan:
        pass

    @abstractmethod
    async def get_mission_status(self, mission_id: str) -> Optional[MissionExecutionPlan]:
        pass

    @abstractmethod
    async def cancel_mission(self, mission_id: str) -> bool:
        pass

    @abstractmethod
    async def resume_mission(self, mission_id: str) -> MissionExecutionPlan:
        pass

    @abstractmethod
    async def list_active_missions(self) -> List[MissionExecutionPlan]:
        pass

    @abstractmethod
    async def get_metrics(self) -> ExecutionMetrics:
        pass

    @abstractmethod
    def check_health(self) -> ExecutionHealth:
        pass


class IMissionExecutor(ABC):
    """Abstract interface for multi-step mission orchestrator."""

    @abstractmethod
    async def run_plan(self, plan: MissionExecutionPlan) -> MissionExecutionPlan:
        pass


class IPluginExecutor(ABC):
    """Abstract interface for step-level plugin capability execution."""

    @abstractmethod
    async def execute_step(self, step: ExecutionStep, context_data: Dict[str, Any]) -> Any:
        pass


class ITransactionManager(ABC):
    """Abstract interface for step-level transaction commit and rollback."""

    @abstractmethod
    async def begin(self, mission_id: str) -> str:
        pass

    @abstractmethod
    async def commit(self, tx_id: str) -> None:
        pass

    @abstractmethod
    async def rollback(self, tx_id: str) -> None:
        pass


class ICheckpointManager(ABC):
    """Abstract interface for checkpoint persistence and recovery."""

    @abstractmethod
    async def create_checkpoint(self, plan: MissionExecutionPlan, context_data: Dict[str, Any]) -> CheckpointData:
        pass

    @abstractmethod
    async def load_checkpoint(self, mission_id: str) -> Optional[CheckpointData]:
        pass
