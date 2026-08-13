"""Central Mission Runtime Engine orchestrating autonomous long-running missions and workflows.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.mission_runtime.approval_queue import ApprovalQueue
from app.ai.mission_runtime.background_workers import BackgroundWorkers
from app.ai.mission_runtime.checkpoint_engine import CheckpointEngine
from app.ai.mission_runtime.configuration import MissionRuntimeConfiguration
from app.ai.mission_runtime.dashboard_api import DashboardAPI
from app.ai.mission_runtime.health import MissionHealthMonitor
from app.ai.mission_runtime.interfaces import IMissionRuntimeEngine
from app.ai.mission_runtime.metrics import MissionMetricsTracker
from app.ai.mission_runtime.mission_manager import MissionManager
from app.ai.mission_runtime.mission_memory import MissionMemory
from app.ai.mission_runtime.models import (
    ApprovalItem,
    CheckpointData,
    MissionHealth,
    MissionMetrics,
    MissionRecord,
    MissionState,
    ProgressReport,
    RecoveryRecord,
    WorkerStatus,
    WorkflowDefinition,
)
from app.ai.mission_runtime.notification_engine import NotificationEngine
from app.ai.mission_runtime.progress_engine import ProgressEngine
from app.ai.mission_runtime.recovery_engine import RecoveryEngine
from app.ai.mission_runtime.runtime_manager import MissionRuntimeManager
from app.ai.mission_runtime.task_scheduler import TaskScheduler
from app.ai.mission_runtime.workflow_engine import WorkflowEngine
from app.ai.mission_runtime.workflow_recorder import WorkflowRecorder


class MissionRuntimeEngine(IMissionRuntimeEngine):
    """The central Autonomous Mission Runtime Engine facade for Nova AI."""

    def __init__(self, config: Optional[MissionRuntimeConfiguration] = None) -> None:
        self.config = config or MissionRuntimeConfiguration()
        self.manager = MissionRuntimeManager(self.config)
        self.mission_manager = MissionManager()
        self.workflow_engine = WorkflowEngine()
        self.task_scheduler = TaskScheduler()
        self.checkpoint_engine = CheckpointEngine()
        self.recovery_engine = RecoveryEngine(self.checkpoint_engine)
        self.approval_queue = ApprovalQueue()
        self.background_workers = BackgroundWorkers(max_workers=self.config.max_background_workers)
        self.progress_engine = ProgressEngine()
        self.notification_engine = NotificationEngine()
        self.dashboard_api = DashboardAPI()
        self.workflow_recorder = WorkflowRecorder()
        self.mission_memory = MissionMemory()
        self.metrics_tracker = MissionMetricsTracker()
        self.health_monitor = MissionHealthMonitor()

        self.health_monitor.set_state(MissionState.RUNNING)

    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> MissionRecord:
        """Creates and launches an autonomous long-running mission.

        Args:
            name: Human-readable mission title.
            goal: Goal description prompt.
            **kwargs: Extra settings (priority, initial tasks).

        Returns:
            MissionRecord model.
        """
        mission = await self.mission_manager.create_mission(name, goal, **kwargs)
        mission.state = MissionState.RUNNING

        # Save initial checkpoint
        await self.checkpoint_engine.save_checkpoint(mission.mission_id, {
            "task_id": mission.workflow.tasks[0].task_id if mission.workflow.tasks else None,
            "state": MissionState.RUNNING,
            "variables": {"goal": goal},
        })
        mission.checkpoints_count += 1

        # Dispatch background worker
        await self.background_workers.dispatch_worker(mission.mission_id)

        # Log event & notify
        await self.mission_memory.log_event(mission.mission_id, "mission_created", {"name": name, "goal": goal})
        if self.config.enable_voice_notifications:
            await self.notification_engine.send_notification(
                title="Mission Started",
                body=f"Started long-running autonomous mission '{name}'.",
                channel="voice",
            )

        self.metrics_tracker.record_mission_created()
        return mission

    async def pause_mission(self, mission_id: str) -> MissionRecord:
        """Pauses running mission state."""
        mission = await self.mission_manager.pause_mission(mission_id)
        await self.background_workers.stop_worker(mission_id)
        await self.notification_engine.send_notification("Mission Paused", f"Mission '{mission.name}' has been paused.", channel="desktop")
        return mission

    async def resume_mission(self, mission_id: str) -> MissionRecord:
        """Resumes paused or recovered mission."""
        mission = await self.mission_manager.resume_mission(mission_id)
        await self.background_workers.dispatch_worker(mission_id)
        await self.notification_engine.send_notification("Mission Resumed", f"Resumed mission '{mission.name}'.", channel="voice")
        return mission

    async def cancel_mission(self, mission_id: str) -> MissionRecord:
        """Cancels running mission."""
        mission = await self.mission_manager.cancel_mission(mission_id)
        await self.background_workers.stop_worker(mission_id)
        self.metrics_tracker.record_mission_failed()
        return mission

    async def clone_mission(self, mission_id: str) -> MissionRecord:
        """Clones existing mission definition."""
        return await self.mission_manager.clone_mission(mission_id)

    async def mission_progress(self, mission_id: str) -> ProgressReport:
        """Retrieves progress report telemetry."""
        return await self.progress_engine.get_progress(mission_id)

    async def mission_logs(self, mission_id: str) -> List[Dict[str, Any]]:
        """Retrieves audit execution logs."""
        return await self.mission_memory.get_logs(mission_id)

    async def mission_history(self) -> List[MissionRecord]:
        """Retrieves mission history list."""
        return await self.mission_manager.list_missions()

    async def mission_dashboard(self) -> Dict[str, Any]:
        """Provides dashboard summary telemetry."""
        return await self.dashboard_api.get_dashboard_data()

    async def check_health(self) -> MissionHealth:
        """Retrieves mission runtime health monitor diagnostics."""
        return self.health_monitor.check_health()

    async def get_metrics(self) -> MissionMetrics:
        """Retrieves mission runtime telemetry metrics."""
        return self.metrics_tracker.get_metrics()
