"""EventPublisher publishing events to system-wide event bus.
"""

from typing import Any, Dict, Optional

from app.runtime.events.event import SystemEvent
from app.runtime.events.event_bus import EventBus
from app.runtime.events.topics import Topic


class EventPublisher:
    """Publishes agent, execution, and permission status change events onto the System Event Bus."""

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        """Initializes EventPublisher.

        Args:
            event_bus: Active EventBus instance. If None, instantiates a default.
        """
        self.event_bus = event_bus or EventBus()

    async def _publish(self, topic: Topic, event_type: str, source: str, payload_data: Dict[str, Any]) -> None:
        """Builds and publishes SystemEvent payload."""
        merged_payload = {"event_type": event_type}
        merged_payload.update(payload_data)
        event = SystemEvent(topic=topic, source=source, payload=merged_payload)
        await self.event_bus.publish(event)

    async def publish_agent_started(self, agent_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        await self._publish(Topic.AGENT_STARTED, "AgentStarted", agent_name, payload or {})

    async def publish_agent_completed(self, agent_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        await self._publish(Topic.AGENT_STOPPED, "AgentCompleted", agent_name, payload or {})

    async def publish_agent_failed(
        self, agent_name: str, error: str, payload: Optional[Dict[str, Any]] = None
    ) -> None:
        data = {"error": error}
        data.update(payload or {})
        await self._publish(Topic.AGENT_STOPPED, "AgentFailed", agent_name, data)

    async def publish_permission_granted(
        self, agent_name: str, resource: str, payload: Optional[Dict[str, Any]] = None
    ) -> None:
        data = {"resource": resource}
        data.update(payload or {})
        await self._publish(Topic.CONVERSATION_UPDATED, "PermissionGranted", agent_name, data)

    async def publish_permission_denied(
        self, agent_name: str, resource: str, payload: Optional[Dict[str, Any]] = None
    ) -> None:
        data = {"resource": resource}
        data.update(payload or {})
        await self._publish(Topic.JOB_FAILED, "PermissionDenied", agent_name, data)

    async def publish_execution_started(self, execution_id: str, payload: Optional[Dict[str, Any]] = None) -> None:
        await self._publish(Topic.JOB_STARTED, "ExecutionStarted", execution_id, payload or {})

    async def publish_execution_completed(
        self, execution_id: str, result: Any, payload: Optional[Dict[str, Any]] = None
    ) -> None:
        data = {"result": str(result)}
        data.update(payload or {})
        await self._publish(Topic.JOB_COMPLETED, "ExecutionCompleted", execution_id, data)

    async def publish_execution_failed(
        self, execution_id: str, error: str, payload: Optional[Dict[str, Any]] = None
    ) -> None:
        data = {"error": error}
        data.update(payload or {})
        await self._publish(Topic.JOB_FAILED, "ExecutionFailed", execution_id, data)
