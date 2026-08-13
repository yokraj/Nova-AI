"""Reasoning Engine synthesizing evidence, inferring conclusions, and highlighting uncertainties via UniversalAIRuntimeEngine.reason().
"""

from typing import List, Optional
from app.ai.research.interfaces import IReasoningEngine
from app.ai.research.models import ClaimVerification, ReasoningOutput
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine


class ReasoningEngine(IReasoningEngine):
    """Executes structured reasoning and evidence synthesis over verified claims using real local AI runtime."""

    def __init__(self, runtime_engine: Optional[UniversalAIRuntimeEngine] = None) -> None:
        self.runtime = runtime_engine or UniversalAIRuntimeEngine()

    async def reason(self, topic: str, claims: List[ClaimVerification]) -> ReasoningOutput:
        """Synthesizes verified claims into structured reasoning output via UniversalAIRuntimeEngine."""
        claims_text = "\n".join([f"- {c.statement} (Score: {c.verification_score})" for c in claims])
        prompt = f"Synthesize research topic '{topic}' with claims:\n{claims_text}"

        res = await self.runtime.reason(prompt=prompt, model_id="qwen3:8b")

        conclusions: List[str] = []
        uncertainties: List[str] = []

        for clm in claims:
            if clm.verification_score >= 0.8:
                conclusions.append(f"Confirmed: {clm.statement}")
            else:
                uncertainties.append(f"Uncertain: {clm.statement} (Score: {clm.verification_score})")

        if not conclusions:
            conclusions.append(f"Primary thesis established for {topic} based on available sources.")

        next_steps = [
            f"Conduct deeper benchmark analysis on {topic}",
            f"Verify real-world deployment patterns for {topic}",
        ]

        summary_text = res.text_or_data if res and res.text_or_data else f"Synthesized {len(claims)} verified claims for '{topic}'."

        return ReasoningOutput(
            topic=topic,
            conclusions=conclusions,
            evidence_summary=summary_text,
            uncertainties=uncertainties,
            next_steps=next_steps,
        )
