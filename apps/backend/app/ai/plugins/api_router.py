"""API Router routing external/internal requests to plugin capabilities."""

from typing import Any, Dict, Optional
import structlog

from app.ai.plugins.execution_manager import ExecutionManager
from app.ai.plugins.models import ExecutionResult

logger = structlog.get_logger("plugin_api_router")


class ApiRouter:
    """Routes capability execution requests to the ExecutionManager."""

    def __init__(self, execution_manager: ExecutionManager) -> None:
        self.execution_manager = execution_manager

    async def route_request(
        self,
        plugin_id: str,
        capability_name: str,
        parameters: Dict[str, Any],
        agent_id: str = "system",
        mission_id: Optional[str] = None,
    ) -> ExecutionResult:
        """Route request directly to execution manager."""
        logger.debug("Routing plugin API request", plugin_id=plugin_id, capability=capability_name)
        return await self.execution_manager.execute_capability(
            plugin_id=plugin_id,
            capability_name=capability_name,
            parameters=parameters,
            agent_id=agent_id,
            mission_id=mission_id,
        )
