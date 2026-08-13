"""Plugin Executor executing step capabilities via the Plugin Platform."""

from typing import Any, Dict, Optional
import structlog

from app.ai.execution.interfaces import IPluginExecutor
from app.ai.execution.models import ExecutionStep
from app.ai.plugins.plugin_engine import PluginEngine

logger = structlog.get_logger("execution_plugin_executor")


class PluginExecutor(IPluginExecutor):
    """Executes a single step capability using the central PluginEngine."""

    def __init__(self, plugin_engine: Optional[PluginEngine] = None) -> None:
        self.plugin_engine = plugin_engine or PluginEngine()

    async def execute_step(self, step: ExecutionStep, context_data: Dict[str, Any]) -> Any:
        """Execute a step's plugin capability."""
        logger.info(
            "Executing plugin capability for step",
            step_id=step.step_id,
            plugin_id=step.plugin_id,
            capability=step.capability,
        )

        # Merge step parameters with shared context data if needed
        merged_params = dict(step.parameters)
        for k, v in context_data.items():
            if k not in merged_params:
                merged_params[k] = v

        res = await self.plugin_engine.execute_plugin(
            plugin_id=step.plugin_id,
            capability=step.capability,
            parameters=merged_params,
        )

        if not res.success:
            raise Exception(f"Plugin capability '{step.plugin_id}.{step.capability}' failed: {res.error}")

        return res.data
