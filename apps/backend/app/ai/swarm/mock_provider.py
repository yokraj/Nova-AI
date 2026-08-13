"""Mock Swarm Provider simulating multi-agent swarm execution deterministically."""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("swarm_mock_provider")


class MockSwarmProvider:
    """Deterministic offline provider for swarm intelligence engine testing."""

    def __init__(self) -> None:
        self.logs: List[Dict[str, Any]] = []

    async def execute_mock_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated swarm action."""
        record = {"action": action_name, "params": parameters, "status": "completed"}
        self.logs.append(record)
        logger.info("MockSwarmProvider executed action", action=action_name)
        return {"status": "success", "result": record}
