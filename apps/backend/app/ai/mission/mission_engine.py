"""Central Mission Engine coordinating autonomous objective goals and queues.
"""

import time
import uuid
import structlog
from typing import Dict, Any, List, Optional
from app.ai.mission.configuration import MissionConfiguration
from app.ai.mission.models import Mission, MissionState, MissionCheckpoint
from app.ai.mission.mission_manager import MissionManager
from app.ai.mission.mission_queue import MissionQueue
from app.ai.mission.mission_scheduler import MissionScheduler
from app.ai.mission.mission_executor import MissionExecutor
from app.ai.mission.mission_state import MissionStateMachine
from app.ai.mission.mission_context import MissionContextContainer
from app.ai.mission.checkpoint_manager import CheckpointManager
from app.ai.mission.recovery_manager import RecoveryManager
from app.ai.mission.autonomous_decision_engine import AutonomousDecisionEngine
from app.ai.mission.mission_monitor import MissionMonitor
from app.ai.mission.progress_tracker import ProgressTracker
from app.ai.mission.notification_manager import NotificationManager
from app.ai.mission.event_bridge import MissionEventBridge
from app.ai.mission.memory import MissionMemory
from app.ai.mission.metrics import MissionMetricsTracker
from app.ai.mission.health import MissionHealthMonitor
from app.ai.mission.providers.mock_provider import MockMissionProvider
from app.ai.workflow.workflow_engine import WorkflowEngine

logger = structlog.get_logger("mission_engine")

class MissionEngine:
    """The Mission Control Engine orchestrating long-running multi-agent autonomous runs."""

    def __init__(self, event_bus: Any = None, memory_engine: Any = None) -> None:
        self.config = MissionConfiguration()
        self.manager = MissionManager()
        self.queue = MissionQueue()
        self.scheduler = MissionScheduler(self.queue, self.config.max_concurrent_missions)
        
        # Core engines
        self.workflow_engine = WorkflowEngine(event_bus, memory_engine)
        self.executor = MissionExecutor(workflow_engine=self.workflow_engine)
        self.state_machine = MissionStateMachine()
        self.checkpoint_mgr = CheckpointManager()
        self.recovery = RecoveryManager(self.manager, self.checkpoint_mgr)
        self.decision_engine = AutonomousDecisionEngine()
        self.monitor = MissionMonitor()
        self.notification = NotificationManager(event_bus)
        self.event_bridge = MissionEventBridge(event_bus)
        self.memory = MissionMemory(memory_engine)
        self.metrics = MissionMetricsTracker()
        self.health = MissionHealthMonitor(self.scheduler, self.queue, self.manager)
        self.mock = MockMissionProvider()

        # Track active contexts and trackers
        self.contexts: Dict[str, MissionContextContainer] = {}
        self.trackers: Dict[str, ProgressTracker] = {}

    async def start_mission(self, goal: str) -> Dict[str, Any]:
        """Registers a new goal and enqueues it for resource scheduling."""
        start_time = time.time()
        mission_id = f"ms_{uuid.uuid4().hex[:8]}"
        logger.info("Starting new autonomous mission", mission_id=mission_id, goal=goal)

        # 1. Initialize models
        mission = Mission(mission_id=mission_id, goal=goal)
        self.contexts[mission_id] = MissionContextContainer(mission_id)
        self.trackers[mission_id] = ProgressTracker(mission_id)

        # 2. Queue and schedule
        self.queue.push(mission)
        self.manager.save_mission(mission)
        await self.event_bridge.publish_mission_transition(mission)
        await self.notification.notify_event("Mission Started", {"mission_id": mission_id, "goal": goal})

        # Try scheduling immediately
        scheduled = self.scheduler.schedule_next()
        if scheduled and scheduled.mission_id == mission_id:
            # Transition pipeline
            mission.state = MissionState.EXECUTING
            self.manager.save_mission(mission)
            await self.event_bridge.publish_mission_transition(mission)

            # Save pre-execution checkpoint
            self.save_checkpoint(mission_id)

            # 3. Execution Pipeline
            try:
                # Decide autonomously using decision policies
                telemetry = self.monitor.collect_telemetry()
                decision = self.decision_engine.decide(telemetry)
                self.metrics.record_decision()

                if decision == "pause":
                    mission.state = MissionState.PAUSED
                    await self.notification.notify_event("Mission Paused", {"mission_id": mission_id})
                else:
                    # Run executors linking planners/workflows
                    wf_res = await self.executor.execute_mission(mission, self.contexts[mission_id].dump())
                    
                    # Update progress
                    tracker = self.trackers[mission_id]
                    tracker.update_progress(
                        percentage=wf_res.get("progress", 100.0),
                        completed=["step_arch", "step_db", "step_api", "step_ui", "step_test"],
                        remaining=[],
                        stage="execution"
                    )
                    
                    mission.progress = tracker.percentage
                    mission.state = MissionState.COMPLETED
                    self.metrics.record_outcome(True)
                    await self.notification.notify_event("Mission Completed", {"mission_id": mission_id})

            except Exception as err:
                logger.error("Autonomous mission execution failed", error=str(err))
                mission.state = MissionState.FAILED
                self.metrics.record_outcome(False)
                await self.notification.notify_event("Mission Failed", {"mission_id": mission_id, "error": str(err)})

        # Persist and index history summary details
        duration = (time.time() - start_time) * 1000.0
        self.metrics.record_duration(duration)
        
        self.scheduler.complete_mission(mission_id)
        self.manager.save_mission(mission)
        await self.event_bridge.publish_mission_transition(mission)

        voice_summary = self.generate_voice_progress(mission_id)
        await self.memory.persist_mission(mission_id, voice_summary)

        return {
            "status": "success" if mission.state == MissionState.COMPLETED else "failed",
            "mission_id": mission_id,
            "state": mission.state.value,
            "progress": mission.progress,
            "voice_summary": voice_summary,
            "metrics": self.metrics.dump_summary()
        }

    async def pause_mission(self, mission_id: str) -> Dict[str, Any]:
        """Pauses executing mission threads."""
        logger.info("Pausing mission thread", mission_id=mission_id)
        mission = self.manager.get_mission(mission_id)
        if not mission:
            return {"status": "failed", "message": "Mission not registered"}

        mission.state = MissionState.PAUSED
        self.manager.save_mission(mission)
        await self.event_bridge.publish_mission_transition(mission)
        await self.notification.notify_event("Mission Paused", {"mission_id": mission_id})

        return {"status": "success", "mission_id": mission_id, "state": mission.state.value}

    async def resume_mission(self, mission_id: str) -> Dict[str, Any]:
        """Resumes paused mission schedules from checkpoint snap."""
        logger.info("Resuming mission thread", mission_id=mission_id)
        recovery_data = self.recovery.recover_mission(mission_id)
        if not recovery_data:
            return {"status": "failed", "message": "No checkpoints found to recover mission"}

        mission, context_vars = recovery_data
        self.contexts[mission_id] = MissionContextContainer(mission_id)
        self.contexts[mission_id].load(context_vars)

        mission.state = MissionState.RESUMED
        self.manager.save_mission(mission)
        await self.event_bridge.publish_mission_transition(mission)
        await self.notification.notify_event("Mission Resumed", {"mission_id": mission_id})

        # Run loop trigger
        mission.state = MissionState.EXECUTING
        wf_res = await self.executor.execute_mission(mission, self.contexts[mission_id].dump())
        
        mission.progress = wf_res.get("progress", 100.0)
        mission.state = MissionState.COMPLETED
        self.manager.save_mission(mission)
        await self.event_bridge.publish_mission_transition(mission)

        return {"status": "success", "mission_id": mission_id, "state": mission.state.value}

    async def cancel_mission(self, mission_id: str) -> Dict[str, Any]:
        """Cancels mission in scheduling queues."""
        logger.info("Canceling mission thread", mission_id=mission_id)
        self.queue.cancel(mission_id)
        self.scheduler.complete_mission(mission_id)
        
        mission = self.manager.get_mission(mission_id)
        if mission:
            mission.state = MissionState.ARCHIVED
            self.manager.save_mission(mission)

        return {"status": "success", "mission_id": mission_id}

    async def mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Returns metadata status information of target mission."""
        mission = self.manager.get_mission(mission_id)
        if not mission:
            return {"status": "failed", "message": "Mission not registered"}
        return mission.model_dump()

    async def list_missions(self) -> List[Dict[str, Any]]:
        """Lists metadata of all registered missions."""
        return [m.model_dump() for m in self.manager.list_missions()]

    def save_checkpoint(self, mission_id: str) -> None:
        """Saves current state checkpoints."""
        mission = self.manager.get_mission(mission_id)
        ctx = self.contexts.get(mission_id)
        if mission and ctx:
            ckpt = self.checkpoint_mgr.create_checkpoint(mission, ctx)
            self.manager.save_checkpoint(ckpt)
            self.metrics.record_recovery()

    def generate_voice_progress(self, mission_id: str) -> str:
        """Generates conversational progress indicators."""
        mission = self.manager.get_mission(mission_id)
        if not mission:
            return "Mission not found."

        if mission.state == MissionState.COMPLETED:
            return "Mission completed successfully."
        elif mission.state == MissionState.FAILED:
            return "Mission execution failed."
        elif mission.state == MissionState.PAUSED:
            return "Deployment requires your approval."

        tracker = self.trackers.get(mission_id)
        if tracker:
            return tracker.generate_voice_summary()
        return "Mission is running."
