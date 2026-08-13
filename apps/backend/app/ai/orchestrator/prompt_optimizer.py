"""Prompt Optimization Engine with domain templates, versioning, profiles, and A/B testing support.
"""

from typing import Any, Dict, Optional
from app.ai.orchestrator.interfaces import IPromptOptimizer


class PromptOptimizer(IPromptOptimizer):
    """Enriches raw prompt with specialized domain template wrappers."""

    def __init__(self) -> None:
        self._templates: Dict[str, str] = {
            "conversation": "System: You are Nova AI OS, an empathetic, voice-first intelligent assistant.\nUser: {prompt}",
            "coding": "System: You are a Principal Software Engineer. Provide complete production-grade code.\nTask: {prompt}",
            "vision": "System: Analyze screenshot layout, UI controls, text, and visual elements.\nTarget: {prompt}",
            "planning": "System: Formulate a hierarchical goal DAG with dependencies and validation criteria.\nGoal: {prompt}",
            "reasoning": "System: Conduct step-by-step analytical reasoning and derive technical conclusion.\nQuery: {prompt}",
            "research": "System: Synthesize literature, academic findings, and technical evidence.\nTopic: {prompt}",
            "translation": "System: Translate input text accurately into target language preserving context.\nSource: {prompt}",
            "speech": "System: Process spoken audio turn for text conversion.\nTranscript: {prompt}",
        }

    def optimize_prompt(self, prompt: str, category: str, variables: Optional[Dict[str, Any]] = None) -> str:
        template = self._templates.get(category.lower(), self._templates["reasoning"])
        optimized = template.format(prompt=prompt)
        if variables:
            for key, val in variables.items():
                optimized += f"\nContext Variable [{key}]: {val}"
        return optimized
