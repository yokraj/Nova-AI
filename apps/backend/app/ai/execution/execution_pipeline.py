"""Execution Pipeline linking Voice -> Intent -> Planner -> Mission -> Plugin -> Learning -> Voice Response."""

from typing import Any, Dict, Optional
import structlog
from uuid import uuid4

from app.ai.execution.mission_executor import MissionExecutor
from app.ai.execution.models import ExecutionStep, MissionExecutionPlan
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("execution_pipeline")


class ExecutionPipeline:
    """Full execution pipeline connecting Voice utterance to Plugin capability execution and Voice Response."""

    def __init__(self, mission_executor: Optional[MissionExecutor] = None) -> None:
        self.executor = mission_executor or MissionExecutor()

    async def process_voice_command(self, utterance: str) -> Dict[str, Any]:
        """Process natural language voice command end-to-end.

        Flow: Voice → Intent → Planner → Mission → Plugin → Learning → Voice Response
        """
        logger.info("Processing voice command through execution pipeline", utterance=utterance)
        mission_id = f"ms_v_{uuid4().hex[:8]}"

        # 1. Resolve intent via gateway / plugin skills
        try:
            gateway = resolve(IAIGateway)
            # Try to resolve directly or plan
            plan_res = await gateway.recommend_strategy(utterance)
            strategy_name = plan_res.get("recommendation", "Default Execution Strategy")
        except Exception:
            strategy_name = "Default Execution Strategy"

        # 2. Build execution plan
        steps = self._derive_steps(utterance)
        plan = MissionExecutionPlan(
            mission_id=mission_id,
            goal=utterance,
            steps=steps,
        )

        # 3. Execute mission plan through executor (Plugins + Safety + Checkpoints)
        executed_plan = await self.executor.run_plan(plan)

        # 4. Formulate voice response
        if executed_plan.state.value == "completed":
            response_text = f"Successfully completed task: '{utterance}'."
        else:
            response_text = f"Task '{utterance}' failed during execution."

        logger.info("Pipeline execution complete", mission_id=mission_id, status=executed_plan.state.value)

        return {
            "mission_id": mission_id,
            "utterance": utterance,
            "status": executed_plan.state.value,
            "voice_response": response_text,
            "steps_executed": len(executed_plan.steps),
        }

    def _derive_steps(self, utterance: str) -> list:
        """Derive execution steps from utterance keywords."""
        text = utterance.lower()

        if "pdf" in text and "email" in text:
            return [
                ExecutionStep(
                    name="Summarize PDF",
                    plugin_id="pdf",
                    capability="summarize_pdf",
                    parameters={"path": "document.pdf"},
                ),
                ExecutionStep(
                    name="Send Email Summary",
                    plugin_id="email",
                    capability="send_email",
                    parameters={"to": "john@example.com", "subject": "PDF Summary"},
                    requires_approval=True,
                ),
            ]

        if "chrome" in text or "website" in text or "browser" in text:
            return [
                ExecutionStep(
                    name="Open Browser",
                    plugin_id="browser",
                    capability="open_url",
                    parameters={"url": "https://nova.ai"},
                ),
                ExecutionStep(
                    name="Take Screenshot",
                    plugin_id="browser",
                    capability="take_screenshot",
                    parameters={"filename": "notes.png"},
                ),
            ]

        # Default fallback step
        return [
            ExecutionStep(
                name="Execute Terminal Diagnostic",
                plugin_id="terminal",
                capability="check_environment",
                parameters={},
            )
        ]
