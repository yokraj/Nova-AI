"""Heartbeat monitor tracking agents uptime and memory usages.
"""

import structlog
from datetime import datetime
from typing import Any
from app.ai.agents.models import AgentHeartbeat

logger = structlog.get_logger("agent_heartbeat")

class HeartbeatMonitor:
    """Gathers periodic diagnostics indicators from running agent sessions."""

    def __init__(self, registry: Any) -> None:
        self.registry = registry

    def generate_heartbeat(self, agent: Any) -> AgentHeartbeat:
        """Returns structural metrics pulse representing current agent states."""
        info = agent.get_info()
        return AgentHeartbeat(
            agent_id=agent.id,
            timestamp=datetime.utcnow(),
            state=agent.state,
            uptime=info.status.uptime_seconds,
            memory_usage_bytes=1024 * 1024 * 12,  # Simulated baseline footprint
            execution_count=agent.total_executions,
            active_task=info.active_task
        )
