"""Abstract base interfaces and contracts for Autonomous Mission & Workflow Engine components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.mission_runtime.models import (
    ApprovalItem,
    CheckpointData,
    MissionHealth,
    MissionMetrics,
    MissionRecord,
    MissionState,
    NotificationMessage,
    ProgressReport,
    RecoveryRecord,
    TaskItem,
    WorkerStatus,
    WorkflowDefinition,
    WorkflowTemplate,
)


class IMissionManager(ABC):
    """Mission Manager contract controlling mission lifecycle."""

    @abstractmethod
    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> MissionRecord:
        """Creates and registers a new long-running mission."""
        pass

    @abstractmethod
    async def pause_mission(self, mission_id: str) -> MissionRecord:
        """Pauses active mission execution."""
        pass

    @abstractmethod
    async def resume_mission(self, mission_id: str) -> MissionRecord:
        """Resumes paused or recovered mission execution."""
        pass

    @abstractmethod
    async def cancel_mission(self, mission_id: str) -> MissionRecord:
        """Cancels running mission."""
        pass

    @abstractmethod
    async def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        """Retrieves mission record by ID."""
        pass


class IWorkflowEngine(ABC):
    """Workflow Engine contract executing complex control flows."""

    @abstractmethod
    async def execute_workflow(self, workflow: WorkflowDefinition, mission_id: str) -> Dict[str, Any]:
        """Executes sequential, parallel, conditional, and dynamic workflows."""
        pass


class ITaskScheduler(ABC):
    """Task Scheduler contract managing queues and cron jobs."""

    @abstractmethod
    async def schedule_task(self, task: TaskItem, delay_seconds: float = 0.0) -> None:
        """Schedules task for delayed or priority queue execution."""
        pass


class ICheckpointEngine(ABC):
    """Checkpoint Engine contract managing state persistence."""

    @abstractmethod
    async def save_checkpoint(self, mission_id: str, data: Dict[str, Any]) -> CheckpointData:
        """Saves a persistent state checkpoint."""
        pass

    @abstractmethod
    async def load_latest_checkpoint(self, mission_id: str) -> Optional[CheckpointData]:
        """Loads most recent checkpoint for crash/reboot recovery."""
        pass


class IRecoveryEngine(ABC):
    """Recovery Engine contract resolving crashes automatically."""

    @abstractmethod
    async def recover_mission(self, mission_id: str, crash_type: str) -> RecoveryRecord:
        """Recovers mission from crash, reboot, or timeout."""
        pass


class IApprovalQueue(ABC):
    """Approval Queue contract managing sensitive action approvals."""

    @abstractmethod
    async def request_approval(self, mission_id: str, action: str, details: str) -> ApprovalItem:
        """Submits sensitive action to approval queue."""
        pass

    @abstractmethod
    async def approve(self, approval_id: str) -> ApprovalItem:
        """Approves pending action."""
        pass


class IBackgroundWorkers(ABC):
    """Background Workers contract running concurrent worker threads."""

    @abstractmethod
    async def dispatch_worker(self, mission_id: str) -> WorkerStatus:
        """Dispatches background worker thread for mission."""
        pass


class IProgressEngine(ABC):
    """Progress Engine contract calculating % and ETA."""

    @abstractmethod
    async def get_progress(self, mission_id: str) -> ProgressReport:
        """Calculates percentage, ETA, completed/remaining tasks."""
        pass


class INotificationEngine(ABC):
    """Notification Engine contract dispatching multi-channel alerts."""

    @abstractmethod
    async def send_notification(self, title: str, body: str, channel: str = "voice") -> NotificationMessage:
        """Dispatches voice, desktop toast, email, or log alert."""
        pass


class IDashboardAPI(ABC):
    """Dashboard API contract serving UI telemetry."""

    @abstractmethod
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Provides mission list, timeline, metrics, and logs."""
        pass


class IWorkflowRecorder(ABC):
    """Workflow Recorder contract converting user actions to workflows."""

    @abstractmethod
    async def record_workflow(self, actions: List[Dict[str, Any]], name: str) -> WorkflowDefinition:
        """Compiles user action sequence into reusable WorkflowDefinition."""
        pass


class IMissionMemory(ABC):
    """Mission Memory contract storing historical execution logs."""

    @abstractmethod
    async def log_event(self, mission_id: str, event_type: str, details: Dict[str, Any]) -> None:
        """Logs mission event into audit trail."""
        pass


class IRuntimeManager(ABC):
    """Runtime Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts mission runtime engine."""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pauses runtime engine."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resumes runtime engine."""
        pass


class IMissionRuntimeEngine(ABC):
    """Central Mission Runtime Engine facade contract."""

    @abstractmethod
    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> MissionRecord:
        """Creates and runs an autonomous long-running mission."""
        pass

    @abstractmethod
    async def pause_mission(self, mission_id: str) -> MissionRecord:
        """Pauses running mission."""
        pass

    @abstractmethod
    async def resume_mission(self, mission_id: str) -> MissionRecord:
        """Resumes paused or recovered mission."""
        pass

    @abstractmethod
    async def cancel_mission(self, mission_id: str) -> MissionRecord:
        """Cancels running mission."""
        pass

    @abstractmethod
    async def clone_mission(self, mission_id: str) -> MissionRecord:
        """Clones existing mission."""
        pass

    @abstractmethod
    async def mission_progress(self, mission_id: str) -> ProgressReport:
        """Retrieves real-time progress report."""
        pass

    @abstractmethod
    async def mission_logs(self, mission_id: str) -> List[Dict[str, Any]]:
        """Retrieves execution logs."""
        pass

    @abstractmethod
    async def mission_history(self) -> List[MissionRecord]:
        """Retrieves mission history list."""
        pass

    @abstractmethod
    async def mission_dashboard(self) -> Dict[str, Any]:
        """Retrieves mission dashboard metrics and timeline."""
        pass
