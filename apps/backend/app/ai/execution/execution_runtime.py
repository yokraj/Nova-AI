"""Central Autonomous Skill Execution Runtime facade."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.execution.checkpoint_manager import CheckpointManager
from app.ai.execution.configuration import ExecutionConfiguration
from app.ai.execution.event_publisher import ExecutionEventPublisher
from app.ai.execution.execution_pipeline import ExecutionPipeline
from app.ai.execution.execution_queue import ExecutionQueue
from app.ai.execution.health import ExecutionHealthMonitor
from app.ai.execution.interfaces import IExecutionRuntime
from app.ai.execution.metrics import ExecutionMetricsTracker
from app.ai.execution.mission_executor import MissionExecutor
from app.ai.execution.mock_provider import MockExecutionProvider
from app.ai.execution.models import CheckpointData, ExecutionHealth, ExecutionMetrics, ExecutionState, MissionExecutionPlan
from app.ai.execution.plugin_executor import PluginExecutor
from app.ai.execution.progress_tracker import ProgressTracker
from app.ai.execution.resource_manager import ResourceManager
from app.ai.execution.rollback_manager import RollbackManager
from app.ai.execution.state_manager import StateManager
from app.ai.execution.status_manager import StatusManager
from app.ai.execution.transaction_manager import TransactionManager
from app.ai.plugins.plugin_engine import PluginEngine

logger = structlog.get_logger("execution_runtime")


class ExecutionRuntime(IExecutionRuntime):
    """Central orchestrator facade for autonomous skill execution runtime."""

    def __init__(
        self,
        plugin_engine: Optional[PluginEngine] = None,
        memory_engine: Optional[Any] = None,
        config: Optional[ExecutionConfiguration] = None,
    ) -> None:
        self.config = config or ExecutionConfiguration()
        self.plugin_engine = plugin_engine or PluginEngine(memory_engine=memory_engine)

        self.queue = ExecutionQueue(max_concurrent=self.config.max_concurrent_missions)
        self.checkpoint_mgr = CheckpointManager(config=self.config)
        self.rollback_mgr = RollbackManager()
        self.tx_mgr = TransactionManager(rollback_manager=self.rollback_mgr)
        self.plugin_executor = PluginExecutor(plugin_engine=self.plugin_engine)
        self.mission_executor = MissionExecutor(
            plugin_executor=self.plugin_executor,
            checkpoint_manager=self.checkpoint_mgr,
            transaction_manager=self.tx_mgr,
        )
        self.pipeline = ExecutionPipeline(mission_executor=self.mission_executor)
        self.resource_mgr = ResourceManager(config=self.config)
        self.state_mgr = StateManager()
        self.progress_tracker = ProgressTracker()
        self.status_mgr = StatusManager()
        self.events = ExecutionEventPublisher()
        self.metrics = ExecutionMetricsTracker()
        self.health = ExecutionHealthMonitor(
            queue=self.queue,
            checkpoint_manager=self.checkpoint_mgr,
            resource_manager=self.resource_mgr,
        )
        self.mock = MockExecutionProvider()

        logger.info("ExecutionRuntime initialized", max_concurrent=self.config.max_concurrent_missions)

    # ------------------------------------------------------------------
    # Public Core API Methods
    # ------------------------------------------------------------------

    async def execute_mission(self, plan: MissionExecutionPlan) -> MissionExecutionPlan:
        """Execute a mission plan."""
        # 1. Resource check
        self.resource_mgr.check_capacity()

        # 2. Enqueue plan
        self.queue.enqueue(plan)
        self.status_mgr.store_plan(plan)

        # 3. Dequeue and run via mission_executor
        active_plan = self.queue.dequeue()
        if not active_plan:
            return plan

        try:
            res_plan = await self.mission_executor.run_plan(active_plan)
            self.status_mgr.store_plan(res_plan)
            self.metrics.record_mission_completion(
                success=res_plan.state == ExecutionState.COMPLETED,
                duration=sum(s.duration_seconds for s in res_plan.steps),
                steps_count=len(res_plan.steps),
            )
            return res_plan
        finally:
            self.queue.mark_completed(active_plan.mission_id)

    async def process_voice_command(self, utterance: str) -> Dict[str, Any]:
        """Process a natural language voice command end-to-end through pipeline."""
        return await self.pipeline.process_voice_command(utterance)

    async def get_mission_status(self, mission_id: str) -> Optional[MissionExecutionPlan]:
        """Query mission status."""
        plan = self.status_mgr.get_status(mission_id)
        if not plan:
            chk = await self.checkpoint_mgr.load_checkpoint(mission_id)
            if chk:
                plan = MissionExecutionPlan(
                    mission_id=chk.mission_id,
                    goal=chk.goal,
                    state=chk.state,
                )
        return plan

    async def cancel_mission(self, mission_id: str) -> bool:
        """Cancel a queued or active mission."""
        success = self.queue.cancel(mission_id)
        plan = self.status_mgr.get_status(mission_id)
        if plan:
            plan.state = ExecutionState.CANCELLED
            self.status_mgr.store_plan(plan)
        return success

    async def resume_mission(self, mission_id: str) -> MissionExecutionPlan:
        """Resume an interrupted mission from its checkpoint."""
        checkpoint = await self.checkpoint_mgr.load_checkpoint(mission_id)
        if not checkpoint:
            raise Exception(f"No checkpoint found to resume mission '{mission_id}'.")

        plan = self.status_mgr.get_status(mission_id)
        if not plan:
            plan = MissionExecutionPlan(
                mission_id=mission_id,
                goal=checkpoint.goal,
                state=ExecutionState.PENDING,
            )

        # Re-run plan starting from remaining incomplete steps
        for step in plan.steps:
            if step.step_id in checkpoint.completed_step_ids:
                step.status = step.status.COMPLETED
                step.output = checkpoint.step_outputs.get(step.step_id)

        return await self.execute_mission(plan)

    async def list_active_missions(self) -> List[MissionExecutionPlan]:
        """List all active running or queued missions."""
        return self.status_mgr.list_active()

    async def get_mission_history() -> List[MissionExecutionPlan]:
        """List all historical missions."""
        return self.status_mgr.list_history()

    async def get_metrics(self) -> ExecutionMetrics:
        """Return execution metrics snapshot."""
        return self.metrics.snapshot()

    def check_health(self) -> ExecutionHealth:
        """Return composite health status."""
        return self.health.check_health()
