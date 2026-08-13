"""Repair Generator invoking local coding models to design code fixes recommendations.
"""

import time
from typing import Any, Optional

from app.agents.software_engineer.debugging.interfaces import RepairGenerator
from app.agents.software_engineer.debugging.models import (
    DebugContext,
    DebugRequest,
    RepairPlan,
    RepairSuggestion,
    RootCause,
)
from app.agents.software_engineer.debugging.prompt_builder import DebuggingPromptBuilder
from app.agents.software_engineer.generator.utils import extract_code_block
from app.ai.models import ChatRequest


class LocalRepairGenerator(RepairGenerator):
    """Interfaces with LLM gateway registry to synthesize patches."""

    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway
        self.prompt_builder = DebuggingPromptBuilder()

    def _resolve_model(self, request: DebugRequest) -> str:
        model_name = request.model_override
        if not model_name and self.gateway and hasattr(self.gateway, "model_registry"):
            model_name = self.gateway.model_registry.default_model()
        return model_name or "llama3"

    async def generate_repair(
        self, request: DebugRequest, context: DebugContext, root_cause: RootCause
    ) -> RepairPlan:
        """Invokes LLM via dynamic model lookup.

        Args:
            request: Active debugging request.
            context: Session context parameters.
            root_cause: Detected root cause report.

        Returns:
            RepairPlan.
        """
        model_name = self._resolve_model(request)

        # Fallback helper suggestion if offline/gateway is None
        if not self.gateway:
            sug = RepairSuggestion(
                file_path=root_cause.origin_file,
                original_code="# original statement",
                replacement_code="# replacement patch coding",
                explanation="Offline fallback suggestion: verify variable allocations.",
            )
            return RepairPlan(
                plan_id=f"plan-{int(time.time())}",
                summary="Fallback repair patch recommendation.",
                suggestions=[sug],
                estimated_risk="low",
                confidence_score=0.5,
            )

        prompt_pkg = self.prompt_builder.build_prompt(request, context, root_cause)
        chat_req = ChatRequest(
            messages=prompt_pkg.messages,
            model=model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        try:
            chat_res = await self.gateway.chat(chat_req)
            raw_out = chat_res.message.content
        except Exception as e:
            raw_out = f"Error during model generation: {str(e)}"

        code_patch = extract_code_block(raw_out, "python") or "# Fix code could not be extracted"

        sug = RepairSuggestion(
            file_path=root_cause.origin_file,
            original_code="# target error line",
            replacement_code=code_patch,
            explanation=raw_out[:300],
        )

        return RepairPlan(
            plan_id=f"plan-{int(time.time())}",
            summary="LLM synthesized code fix patch.",
            suggestions=[sug],
            estimated_risk="low",
            confidence_score=0.8,
        )
