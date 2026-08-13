"""Mission Executor orchestrating multi-step execution plans with full resiliency and learning integration."""

from typing import Any, Dict, Optional
import structlog

from app.ai.execution.approval_handler import ApprovalHandler
from app.ai.execution.checkpoint_manager import CheckpointManager
from app.ai.execution.execution_context import ExecutionContext
from app.ai.execution.execution_scheduler import ExecutionScheduler
from app.ai.execution.interfaces import IMissionExecutor
from app.ai.execution.models import ExecutionState, ExecutionStep, MissionExecutionPlan, StepStatus
from app.ai.execution.plugin_executor import PluginExecutor
from app.ai.execution.recovery_manager import RecoveryManager
from app.ai.execution.state_manager import StateManager
from app.ai.execution.transaction_manager import TransactionManager
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("execution_mission_executor")


class MissionExecutor(IMissionExecutor):
    """Executes a multi-step MissionExecutionPlan through plugins, checkpoints, and transactions."""

    def __init__(
        self,
        plugin_executor: Optional[PluginExecutor] = None,
        checkpoint_manager: Optional[CheckpointManager] = None,
        transaction_manager: Optional[TransactionManager] = None,
    ) -> None:
        self.plugin_executor = plugin_executor or PluginExecutor()
        self.checkpoint_mgr = checkpoint_manager or CheckpointManager()
        self.tx_mgr = transaction_manager or TransactionManager()
        self.scheduler = ExecutionScheduler()
        self.state_mgr = StateManager()
        self.approval_handler = ApprovalHandler()
        self.recovery_mgr = RecoveryManager()

    async def run_plan(self, plan: MissionExecutionPlan) -> MissionExecutionPlan:
        """Run all steps in a mission plan sequentially with context sharing and checkpoints."""
        logger.info("Starting mission plan execution", mission_id=plan.mission_id, goal=plan.goal)
        plan.state = self.state_mgr.transition_mission(plan.state, ExecutionState.RUNNING)

        context = ExecutionContext(mission_id=plan.mission_id)
        tx_id: Optional[str] = None

        if any(s.is_transactional for s in plan.steps):
            tx_id = await self.tx_mgr.begin(plan.mission_id)

        try:
            total_steps = len(plan.steps)

            for idx, step in enumerate(plan.steps, start=1):
                if plan.state == ExecutionState.CANCELLED:
                    logger.info("Mission cancelled before step", mission_id=plan.mission_id, step_id=step.step_id)
                    break

                # 1. Approval check
                if step.requires_approval or self.approval_handler._is_dangerous_step(step):
                    plan.state = ExecutionState.WAITING_APPROVAL
                    await self.approval_handler.verify_approval(plan.mission_id, step)
                    plan.state = ExecutionState.RUNNING

                # 2. Step execution via scheduler
                async def _exec_fn():
                    return await self.plugin_executor.execute_step(step, context.dump_data()["shared"])

                try:
                    output = await self.scheduler.schedule_step(step, _exec_fn)
                    step.output = output
                    context.record_step_output(step.step_id, output)
                    if step.output and isinstance(step.output, dict):
                        for k, v in step.output.items():
                            context.set(k, v)
                except Exception as step_err:
                    # Attempt automated recovery
                    try:
                        output = await self.recovery_mgr.recover(step, step_err, _exec_fn)
                        step.output = output
                        context.record_step_output(step.step_id, output)
                    except Exception as final_err:
                        step.status = StepStatus.FAILED
                        step.error = str(final_err)
                        raise step_err

                if tx_id and step.is_transactional:
                    self.tx_mgr.record_step(tx_id, step)

                # 3. Update progress & checkpoint
                plan.progress_percentage = round((idx / total_steps) * 100.0, 1)
                await self.checkpoint_mgr.create_checkpoint(plan, context.dump_data())

            if tx_id:
                await self.tx_mgr.commit(tx_id)

            plan.state = self.state_mgr.transition_mission(plan.state, ExecutionState.COMPLETED)
            logger.info("Mission plan completed successfully", mission_id=plan.mission_id)

            # Inform Learning Engine
            await self._feed_learning(plan)

        except Exception as err:
            logger.error("Mission plan execution failed", mission_id=plan.mission_id, error=str(err))
            if tx_id:
                await self.tx_mgr.rollback(tx_id)
            plan.state = ExecutionState.FAILED

        return plan

    async def _feed_learning(self, plan: MissionExecutionPlan) -> None:
        """Feed execution metadata to LearningEngine."""
        try:
            gateway = resolve(IAIGateway)
            await gateway.learn_from_mission(
                mission_id=plan.mission_id,
                mission_result={
                    "goal": plan.goal,
                    "status": "success" if plan.state == ExecutionState.COMPLETED else "failed",
                    "duration_seconds": sum(s.duration_seconds for s in plan.steps),
                    "agents_used": plan.agents_involved or ["execution_runtime"],
                },
            )
        except Exception:
            pass
