"""Central Workflow Engine coordinating multi-step processes and rollbacks.
"""

import time
import uuid
import structlog
from typing import Dict, Any, List, Optional
from app.ai.workflow.configuration import WorkflowConfiguration
from app.ai.workflow.models import Workflow, WorkflowStep, WorkflowState, WorkflowCheckpoint, ApprovalRequest
from app.ai.workflow.state_persistence import StatePersistence
from app.ai.workflow.workflow_scheduler import WorkflowScheduler
from app.ai.workflow.workflow_builder import WorkflowBuilder
from app.ai.workflow.workflow_executor import WorkflowExecutor
from app.ai.workflow.workflow_state import WorkflowStateMachine
from app.ai.workflow.workflow_context import WorkflowContextContainer
from app.ai.workflow.checkpoint_manager import CheckpointManager
from app.ai.workflow.recovery_engine import RecoveryEngine
from app.ai.workflow.approval_manager import ApprovalManager
from app.ai.workflow.retry_engine import RetryEngine
from app.ai.workflow.rollback_engine import RollbackEngine
from app.ai.workflow.timeout_manager import TimeoutManager
from app.ai.workflow.branching_engine import BranchingEngine
from app.ai.workflow.event_bridge import WorkflowEventBridge
from app.ai.workflow.memory import WorkflowMemory
from app.ai.workflow.metrics import WorkflowMetricsTracker
from app.ai.workflow.health import WorkflowHealthMonitor
from app.ai.workflow.providers.mock_provider import MockWorkflowProvider
from app.ai.collaboration.collaboration_engine import CollaborationEngine

logger = structlog.get_logger("workflow_engine")

class WorkflowEngine:
    """The central orchestrator for multi-agent workflows with pauses, retries, and checkpoints."""

    def __init__(self, event_bus: Any = None, memory_engine: Any = None) -> None:
        self.config = WorkflowConfiguration()
        self.persistence = StatePersistence()
        self.scheduler = WorkflowScheduler()
        self.builder = WorkflowBuilder()
        
        # Instantiate dependencies
        self.collab = CollaborationEngine(event_bus, memory_engine)
        self.executor = WorkflowExecutor(self.collab)
        self.state_machine = WorkflowStateMachine()
        self.branching_engine = BranchingEngine()
        self.checkpoint_mgr = CheckpointManager()
        self.recovery = RecoveryEngine(self.persistence, self.checkpoint_mgr)
        self.approvals = ApprovalManager()
        self.retries = RetryEngine()
        self.rollback_engine = RollbackEngine()
        self.timeout_mgr = TimeoutManager()
        self.event_bridge = WorkflowEventBridge(event_bus)
        self.memory = WorkflowMemory(memory_engine)
        self.metrics = WorkflowMetricsTracker()
        self.health = WorkflowHealthMonitor(self.scheduler, self.persistence, self.approvals)
        self.mock = MockWorkflowProvider()

        # Keep active contexts
        self.contexts: Dict[str, WorkflowContextContainer] = {}

    async def execute_workflow(self, goal: str) -> Dict[str, Any]:
        """Compiles planning graph tasks and executes steps topologically."""
        start_time = time.time()
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        logger.info("Initializing workflow execution run", workflow_id=workflow_id, goal=goal)

        # 1. Build and persist workflow structure
        workflow = self.builder.build_workflow(workflow_id, goal)
        self.contexts[workflow_id] = WorkflowContextContainer(workflow_id)
        
        # Enqueue and start
        self.scheduler.enqueue(workflow)
        workflow.state = WorkflowState.RUNNING
        self.persistence.save_workflow(workflow)
        await self.event_bridge.publish_workflow_transition(workflow)

        # Save pre-execution checkpoint
        self.save_checkpoint(workflow_id)

        # 2. Main Step Loop
        try:
            await self._run_loop(workflow_id)
            workflow = self.persistence.get_workflow(workflow_id) or workflow
            workflow.state = WorkflowState.COMPLETED
            self.metrics.record_outcome(True)
        except Exception as err:
            logger.error("Workflow run encountered a fatal exception", error=str(err))
            workflow.state = WorkflowState.FAILED
            self.metrics.record_outcome(False)
            # Rollback
            try:
                latest_ckpt = self.persistence.get_checkpoints(workflow_id)[-1]
                self.rollback_engine.rollback(workflow, self.contexts[workflow_id], latest_ckpt.workflow_snapshot)
                self.metrics.record_rollback()
            except Exception as rollback_err:
                logger.error("Failed to execute automatic rollback sequence", error=str(rollback_err))

        duration = (time.time() - start_time) * 1000.0
        self.metrics.record_duration(duration)
        self.persistence.save_workflow(workflow)
        await self.event_bridge.publish_workflow_transition(workflow)

        spoken_update = self.generate_voice_progress(workflow_id)
        await self.memory.persist_workflow(workflow_id, spoken_update)

        return {
            "status": "success" if workflow.state == WorkflowState.COMPLETED else "failed",
            "workflow_id": workflow_id,
            "state": workflow.state.value,
            "progress": workflow.progress,
            "voice_summary": spoken_update,
            "metrics": self.metrics.dump_summary()
        }

    async def _run_loop(self, workflow_id: str) -> None:
        """Runs the queue scheduler execution loop checking blockers and approvals."""
        wf = self.persistence.get_workflow(workflow_id)
        ctx = self.contexts[workflow_id]
        if not wf:
            return

        while True:
            next_steps = self.scheduler.get_next_steps(workflow_id)
            if not next_steps:
                break

            for step in next_steps:
                # Check for approval gate
                if "approval" in step.action or "destructive" in step.parameters:
                    wf.state = WorkflowState.PAUSED
                    self.persistence.save_workflow(wf)
                    await self.event_bridge.publish_workflow_transition(wf)
                    
                    app_id = f"app_{uuid.uuid4().hex[:8]}"
                    req = ApprovalRequest(
                        approval_id=app_id,
                        workflow_id=workflow_id,
                        step_id=step.step_id,
                        action=step.action,
                        reason="Approval gate protection for destructive or deployment tasks."
                    )
                    self.approvals.request_approval(req)
                    self.metrics.record_approval()
                    return  # Pauses execution until resolved

                # Execute step with retry limits and timeouts
                try:
                    await self._execute_step_with_retries(step, ctx)
                except Exception as step_err:
                    step.state = WorkflowState.FAILED
                    raise step_err

                # Update progress percentage
                completed = sum(1 for s in wf.steps.values() if s.state == WorkflowState.COMPLETED)
                wf.progress = (completed / len(wf.steps)) * 100.0
                
                # Checkpoint completing steps
                self.persistence.save_workflow(wf)
                self.save_checkpoint(workflow_id)

    async def _execute_step_with_retries(self, step: WorkflowStep, ctx: WorkflowContextContainer) -> None:
        """Executes a single step enforcing timeout bounds and retry backoffs."""
        max_retries = self.config.max_step_retries
        while True:
            try:
                # Wrap execution in timeout check
                await self.timeout_mgr.execute_with_timeout(
                    self.executor.execute_step(step, ctx.dump()),
                    self.config.step_timeout_seconds
                )
                break
            except Exception as err:
                self.metrics.record_retry()
                if self.retries.should_retry(step, max_retries):
                    step.retry_count += 1
                    delay = self.retries.get_backoff_delay(step.retry_count, self.config.backoff_factor)
                    logger.warn("Step task failed. Backing off for retry attempt", 
                                step_id=step.step_id, retry=step.retry_count, delay_seconds=delay)
                    time.sleep(delay)
                else:
                    raise err

    def save_checkpoint(self, workflow_id: str) -> None:
        """Creates progress checkpoint snapshot."""
        wf = self.persistence.get_workflow(workflow_id)
        ctx = self.contexts.get(workflow_id)
        if wf and ctx:
            ckpt = self.checkpoint_mgr.create_checkpoint(wf, ctx)
            self.persistence.save_checkpoint(ckpt)
            self.metrics.record_checkpoint()

    async def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Recovers state context and resumes pending execution blocks queue."""
        logger.info("Resuming workflow execution", workflow_id=workflow_id)
        recovery_data = self.recovery.recover_workflow(workflow_id)
        if not recovery_data:
            return {"status": "failed", "message": "No valid checkpoint found to recover workflow"}

        workflow, context_vars = recovery_data
        
        # Restore local context mapping
        self.contexts[workflow_id] = WorkflowContextContainer(workflow_id)
        self.contexts[workflow_id].load(context_vars)
        
        # Enqueue back to scheduler and mark running
        workflow.state = WorkflowState.RUNNING
        self.scheduler.enqueue(workflow)
        self.persistence.save_workflow(workflow)
        await self.event_bridge.publish_workflow_transition(workflow)

        try:
            await self._run_loop(workflow_id)
            workflow = self.persistence.get_workflow(workflow_id) or workflow
            workflow.state = WorkflowState.COMPLETED
            self.metrics.record_outcome(True)
        except Exception as err:
            logger.error("Failed executing resumed workflow task", error=str(err))
            workflow.state = WorkflowState.FAILED
            self.metrics.record_outcome(False)

        self.persistence.save_workflow(workflow)
        spoken_update = self.generate_voice_progress(workflow_id)
        await self.memory.persist_workflow(workflow_id, spoken_update)

        return {
            "status": "success" if workflow.state == WorkflowState.COMPLETED else "failed",
            "workflow_id": workflow_id,
            "state": workflow.state.value,
            "progress": workflow.progress,
            "voice_summary": spoken_update
        }

    def generate_voice_progress(self, workflow_id: str) -> str:
        """Compiles human-friendly notification sentences spoken by Voice Intelligence Layer."""
        wf = self.persistence.get_workflow(workflow_id)
        if not wf:
            return "Workflow not found."

        if wf.state == WorkflowState.COMPLETED:
            return "Workflow completed successfully."
        elif wf.state == WorkflowState.FAILED:
            return "Workflow execution failed."
        elif wf.state == WorkflowState.PAUSED:
            return "Deployment requires your approval."
        
        completed = sum(1 for s in wf.steps.values() if s.state == WorkflowState.COMPLETED)
        total = len(wf.steps)
        progress_pct = int(wf.progress)
        
        # Resolve active running step
        running_step = next((s.title for s in wf.steps.values() if s.state == WorkflowState.RUNNING), "next steps")
        return f"Workflow in progress. {completed} of {total} steps completed. Current active task is: {running_step}."
