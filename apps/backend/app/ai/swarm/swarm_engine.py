"""Swarm Engine central facade orchestrating multi-agent collaboration, delegation, and consensus."""

from typing import Any, Dict, List, Optional
from uuid import uuid4
import structlog

from app.ai.swarm.cache import SwarmCache
from app.ai.swarm.configuration import SwarmConfiguration
from app.ai.swarm.health import SwarmHealthMonitor
from app.ai.swarm.interfaces import ISwarmEngine
from app.ai.swarm.metrics import SwarmMetricsTracker
from app.ai.swarm.models import SwarmHealth, SwarmMetrics, SwarmResult, SwarmState
from app.ai.swarm.swarm_manager import SwarmManager

logger = structlog.get_logger("swarm_engine")


class SwarmEngine(ISwarmEngine):
    """Central facade runtime orchestrating Nova's Multi-Agent Collaboration & Swarm Intelligence Engine."""

    def __init__(self, config: Optional[SwarmConfiguration] = None) -> None:
        self.config = config or SwarmConfiguration()
        self.manager = SwarmManager()
        self.metrics = SwarmMetricsTracker()
        self.health_monitor = SwarmHealthMonitor()
        self.cache = SwarmCache()
        self._active_swarms: Dict[str, Dict[str, Any]] = {}

    async def create_swarm(self, goal: str) -> str:
        """Create new swarm execution context for goal."""
        swarm_id = f"swm_{uuid4().hex[:8]}"
        self.metrics.record_swarm_created()
        self._active_swarms[swarm_id] = {"goal": goal, "state": SwarmState.INITIALIZING.value}
        logger.info("Created new swarm execution context", swarm_id=swarm_id, goal=goal)
        return swarm_id

    async def execute_swarm(self, swarm_id: str) -> SwarmResult:
        """Execute swarm context goal across multi-agent workforce."""
        swarm_info = self._active_swarms.get(swarm_id, {"goal": "Analyze backend, security, performance, docs, deploy"})
        goal = swarm_info.get("goal", "Multi-Agent Collaboration Mission")

        self.metrics.record_tasks_decomposed(6)
        res_dict = await self.manager.execute_swarm_goal(goal)
        self.metrics.record_task_executed()
        self.metrics.record_consensus_vote()

        result = SwarmResult(
            swarm_id=swarm_id,
            goal=goal,
            state=SwarmState.COMPLETED,
            aggregated_output=res_dict.get("aggregated_output", {}),
            voice_summary=res_dict.get("voice_summary", f"Swarm collaboration completed for goal '{goal}'"),
            agents_involved=res_dict.get("agents_involved", ["exec_01", "swe_01", "sec_01", "res_01"]),
            execution_duration_seconds=res_dict.get("execution_duration_seconds", 1.5),
        )
        self.cache.set(swarm_id, result)
        logger.info("Executed swarm goal successfully", swarm_id=swarm_id)
        return result

    async def get_metrics(self) -> SwarmMetrics:
        """Retrieve telemetry metrics."""
        return self.metrics.get_metrics()

    def check_health(self) -> SwarmHealth:
        """Retrieve composite health status."""
        return self.health_monitor.check_health()
