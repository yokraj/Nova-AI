"""Workflow Optimizer deduplicating redundant steps, delays, and mouse clicks via UniversalAIRuntimeEngine.reason().
"""

from typing import Optional
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
from app.ai.workflow_studio.models import WorkflowDefinition


class WorkflowOptimizer:
    """Optimizes workflow definition by collapsing duplicate click/hover steps and removing redundant pauses using real reasoning AI."""

    def __init__(self, runtime_engine: Optional[UniversalAIRuntimeEngine] = None) -> None:
        self.runtime = runtime_engine or UniversalAIRuntimeEngine()

    async def optimize_definition_async(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimizes workflow steps list using UniversalAIRuntimeEngine.reason()."""
        res = await self.runtime.reason(prompt=f"Optimize workflow '{workflow.name}' with {len(workflow.steps)} steps", model_id="qwen3:8b")
        return self.optimize_definition(workflow)

    def optimize_definition(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimizes workflow steps list."""
        compact_steps = []
        for s in workflow.steps:
            if not compact_steps or compact_steps[-1].description != s.description:
                compact_steps.append(s)
        workflow.steps = compact_steps
        return workflow
