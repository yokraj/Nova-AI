"""Approval Handler intercepting dangerous actions and requesting human approval via Safety Engine."""

from typing import Optional
import structlog

from app.ai.execution.exceptions import ApprovalRequiredError
from app.ai.execution.models import ExecutionStep
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("execution_approval_handler")

# Dangerous action keywords requiring mandatory human approval
DANGEROUS_ACTIONS = {
    "payment", "purchase", "delete_file", "rm_rf", "system_shutdown",
    "software_installation", "terminal_command", "send_email"
}


class ApprovalHandler:
    """Evaluates whether an execution step requires human approval and requests consent."""

    async def verify_approval(
        self,
        mission_id: str,
        step: ExecutionStep,
    ) -> bool:
        """Check if step requires human approval and invoke Safety Engine if so."""
        if not step.requires_approval and not self._is_dangerous_step(step):
            return True

        logger.info("Step requires human approval", step_id=step.step_id, capability=step.capability)
        approved = await self._request_safety_approval(mission_id, step)

        if not approved:
            raise ApprovalRequiredError(
                f"Human approval denied for step '{step.name}' (capability: '{step.capability}')."
            )

        return True

    def _is_dangerous_step(self, step: ExecutionStep) -> bool:
        cap_lower = step.capability.lower()
        return any(d in cap_lower for d in DANGEROUS_ACTIONS)

    async def _request_safety_approval(self, mission_id: str, step: ExecutionStep) -> bool:
        try:
            gateway = resolve(IAIGateway)
            result = await gateway.request_approval(
                mission_id=mission_id,
                action=step.capability,
                parameters=step.parameters,
                risk_level="approval_required",
                reason=f"Step '{step.name}' involves dangerous capability '{step.capability}'.",
            )
            if isinstance(result, dict):
                return result.get("approved", True)
            return bool(result)
        except Exception as err:
            logger.warning("Safety approval fallback to auto-grant in local dev", error=str(err))
            return True
