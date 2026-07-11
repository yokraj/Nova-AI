"""Unit tests for the Agent Communication Bus subsystem.

Verifies event publishing, subscribing/unsubscribing, event broadcasting,
synchronous request-response routing, multicast, and domain validations.
"""

import asyncio
from typing import Any, Dict, List
import uuid
import pytest

from app.agents import (
    AgentCapability,
    AgentContext,
    AgentDescriptor,
    AgentMetadata,
    AgentPermission,
    AgentRegistry,
    AgentResult,
    BaseAgent,
)
from app.agents.bus import (
    AgentEvent,
    AgentRequest,
    AgentResponse,
    SubscriptionManager,
    RoutingService,
    AgentEventBus,
    RoutingError,
    MessageValidationError,
    SubscriptionError,
)


class DummyBusAgent(BaseAgent):
    """Mock agent implementation for bus routing verifications."""

    async def initialize(self) -> None:
        pass

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        if prompt == "fail":
            return AgentResult(success=False, response="Error occurred", execution_time=0.05)
        if prompt == "raise":
            raise ValueError("Unexpected error")
        return AgentResult(
            success=True,
            response=f"Handled: {prompt}",
            metadata={"meta_field": "val"},
            execution_time=0.05,
        )

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


def test_agent_bus_models_validation() -> None:
    """Verifies fields validation and defaults of request, response, and event models."""
    conv_id = uuid.uuid4()
    req = AgentRequest(
        sender="AgentA",
        receiver="AgentB",
        conversation_id=conv_id,
        payload={"prompt": "hello"},
    )
    assert req.sender == "AgentA"
    assert req.receiver == "AgentB"
    assert req.payload == {"prompt": "hello"}
    assert isinstance(req.request_id, uuid.UUID)

    res = AgentResponse(
        success=True,
        sender="AgentB",
        receiver="AgentA",
        payload={"response": "hi"},
        execution_time=0.12,
    )
    assert res.success is True
    assert res.sender == "AgentB"
    assert res.execution_time == 0.12

    evt = AgentEvent(
        topic="agent.status.changed",
        source="AgentA",
        data={"new_status": "busy"},
    )
    assert evt.topic == "agent.status.changed"
    assert evt.source == "AgentA"
    assert isinstance(evt.event_id, uuid.UUID)


def test_subscription_manager_flows() -> None:
    """Verifies register, unregister, and glob/prefix matching inside SubscriptionManager."""
    manager = SubscriptionManager()
    events_received: List[AgentEvent] = []

    async def listener(event: AgentEvent) -> None:
        events_received.append(event)

    # Register
    manager.register("agent.chat", listener)
    assert listener in manager.listeners("agent.chat")

    # Duplicate registration
    with pytest.raises(SubscriptionError):
        manager.register("agent.chat", listener)

    # Invalid callable
    with pytest.raises(SubscriptionError):
        manager.register("agent.chat", "not_callable")  # type: ignore

    # Glob matching tests
    async def wildcard_listener(event: AgentEvent) -> None:
        pass

    manager.register("agent.*", wildcard_listener)
    assert wildcard_listener in manager.listeners("agent.chat")
    assert wildcard_listener in manager.listeners("agent.status")
    assert listener not in manager.listeners("agent.status")

    # Unregister
    manager.unregister("agent.chat", listener)
    assert listener not in manager.listeners("agent.chat")
    assert wildcard_listener in manager.listeners("agent.chat")

    with pytest.raises(SubscriptionError):
        manager.unregister("agent.chat", listener)


@pytest.mark.anyio
async def test_event_bus_pub_sub() -> None:
    """Verifies publish, subscribe, unsubscribe, and broadcast flows inside AgentEventBus."""
    bus = AgentEventBus()
    received_chat: List[AgentEvent] = []
    received_wildcard: List[AgentEvent] = []

    async def chat_listener(event: AgentEvent) -> None:
        received_chat.append(event)

    async def wildcard_listener(event: AgentEvent) -> None:
        received_wildcard.append(event)

    # Subscribe
    bus.subscribe("agent.chat", chat_listener)
    bus.subscribe("agent.*", wildcard_listener)

    # Publish valid event
    evt = AgentEvent(topic="agent.chat", source="AgentA", data={"message": "hello"})
    await bus.publish(evt)

    assert len(received_chat) == 1
    assert len(received_wildcard) == 1
    assert received_chat[0].event_id == evt.event_id

    # Publish invalid event (validation check)
    with pytest.raises(MessageValidationError):
        await bus.publish(AgentEvent(topic="", source="AgentA"))

    with pytest.raises(MessageValidationError):
        await bus.publish(AgentEvent(topic="agent.chat", source=""))

    # Broadcast event (sets topic to wildcard "*")
    broadcast_evt = AgentEvent(topic="agent.chat", source="AgentA", data={"msg": "broadcast"})
    # Let's subscribe wildcard to "*" as well
    received_broadcast: List[AgentEvent] = []
    
    async def bcast_listener(event: AgentEvent) -> None:
        received_broadcast.append(event)
        
    bus.subscribe("*", bcast_listener)
    await bus.broadcast(broadcast_evt)

    assert len(received_broadcast) == 1
    assert received_broadcast[0].topic == "*"

    # Unsubscribe
    bus.unsubscribe("agent.chat", chat_listener)
    received_chat.clear()
    await bus.publish(AgentEvent(topic="agent.chat", source="AgentA"))
    assert len(received_chat) == 0


@pytest.mark.anyio
async def test_routing_service() -> None:
    """Verifies RoutingService request-response, multicast, and broadcast flows."""
    registry = AgentRegistry()
    routing = RoutingService(registry)

    # Setup agent A and B in registry
    meta_a = AgentMetadata(name="AgentA", description="first agent")
    agent_a = DummyBusAgent(meta_a)
    registry.register(agent_a)

    meta_b = AgentMetadata(name="AgentB", description="second agent")
    agent_b = DummyBusAgent(meta_b)
    registry.register(agent_b)

    # 1. Resolve receiver
    assert routing.resolve_receiver("AgentA") == agent_a
    assert routing.resolve_receiver(str(meta_b.id)) == agent_b
    assert routing.resolve_receiver("NonExistent") is None

    # 2. Route request (success)
    req = AgentRequest(
        sender="AgentA",
        receiver="AgentB",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "test query"},
    )
    res = await routing.route_request(req)
    assert res.success is True
    assert res.sender == "AgentB"
    assert res.receiver == "AgentA"
    assert res.payload["response"] == "Handled: test query"
    assert res.payload["meta_field"] == "val"
    assert res.execution_time > 0.0

    # 3. Route request (error execution return)
    req_fail = AgentRequest(
        sender="AgentA",
        receiver="AgentB",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "fail"},
    )
    res_fail = await routing.route_request(req_fail)
    assert res_fail.success is False
    assert "Error occurred" in res_fail.payload["response"]

    # 4. Route request (raised exception)
    req_raise = AgentRequest(
        sender="AgentA",
        receiver="AgentB",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "raise"},
    )
    with pytest.raises(RoutingError):
        await routing.route_request(req_raise)

    # 5. Route request to missing receiver
    req_missing = AgentRequest(
        sender="AgentA",
        receiver="MissingAgent",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "query"},
    )
    with pytest.raises(RoutingError):
        await routing.route_request(req_missing)

    # 6. Route request to disabled receiver
    meta_disabled = AgentMetadata(name="DisabledAgent", description="disabled")
    agent_disabled = DummyBusAgent(meta_disabled)
    desc_disabled = AgentDescriptor(name="DisabledAgent", description="disabled", enabled=False)
    registry.register(agent_disabled, desc_disabled)

    req_disabled = AgentRequest(
        sender="AgentA",
        receiver="DisabledAgent",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "query"},
    )
    with pytest.raises(RoutingError):
        await routing.route_request(req_disabled)

    # 7. Multicast
    multicast_req = AgentRequest(
        sender="AgentA",
        receiver="Placeholder",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "multicast query"},
    )
    responses = await routing.multicast(multicast_req, ["AgentA", "AgentB", "DisabledAgent"])
    assert len(responses) == 3
    # AgentA and AgentB should be successful, DisabledAgent should contain error
    assert responses[0].success is True
    assert responses[0].sender == "AgentA"
    assert responses[1].success is True
    assert responses[1].sender == "AgentB"
    assert responses[2].success is False
    assert "disabled" in responses[2].payload["error"]

    # 8. Broadcast
    broadcast_req = AgentRequest(
        sender="AgentA",
        receiver="Placeholder",
        conversation_id=uuid.uuid4(),
        payload={"prompt": "broadcast query"},
    )
    broadcast_responses = await routing.broadcast(broadcast_req)
    # Registry has AgentA (sender), AgentB (enabled), DisabledAgent (disabled).
    # Broadcast should target all enabled agents EXCEPT sender (meaning only AgentB).
    assert len(broadcast_responses) == 1
    assert broadcast_responses[0].sender == "AgentB"
    assert broadcast_responses[0].success is True
