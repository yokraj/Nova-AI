"""Mock Service Provider simulating internet service workflows deterministically."""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("services_mock_provider")


class MockServiceProvider:
    """Deterministic offline provider for testing internet service automation."""

    def __init__(self) -> None:
        self.logs: List[Dict[str, Any]] = []

    async def execute_mock_service(self, service_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated service workflow."""
        record = {"service_id": service_id, "params": parameters, "status": "completed"}
        self.logs.append(record)
        logger.info("MockServiceProvider executed service", service_id=service_id)
        return {"status": "success", "result": record}
