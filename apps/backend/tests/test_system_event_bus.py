"""Unit tests for the Enterprise System Event Bus subsystem.

Verifies publishing events, single and multiple subscriptions, batch publishing,
event broadcasts, event store persistence, and historical event replaying.
"""

import asyncio
from datetime import datetime, timedelta, UTC
from typing import List
import uuid
import pytest

from app.runtime.events import (
    EventBus,
    EventStore,
    SystemEvent,
    Topic,
    EventHandler,
    HandlerError,
    EventPublishError,
    EventReplayError,
)


class DummyEventHandler(EventHandler):
    """Mock event handler for system event bus testing."""

    def __init__(self, allowed_topics: List[Topic]) -> None:
        """Initializes DummyEventHandler.

        Args:
            allowed_topics: Topics this handler is configured to handle.
        """
        self.allowed_topics = allowed_topics
        self.received_events: List[SystemEvent] = []
        self.should_fail = False

    async def handle(self, event: SystemEvent) -> None:
        """Processes event, or raises error if configured to fail.

        Args:
            event: SystemEvent payload.
        """
        if self.should_fail:
            raise ValueError("Simulated handler failure.")
        self.received_events.append(event)

    def can_handle(self, event: SystemEvent) -> bool:
        """Checks if topic is in configured allowed list.

        Args:
            event: SystemEvent payload.

        Returns:
            True if allowed; False otherwise.
        """
        return event.topic in self.allowed_topics


@pytest.mark.anyio
async def test_system_event_bus_pub_sub() -> None:
    """Verifies publish and subscribe notifications to multiple subscribers and callables."""
    store = EventStore()
    bus = EventBus(store)

    handler = DummyEventHandler([Topic.USER_REGISTERED])
    received_callback: List[SystemEvent] = []

    async def callback_listener(event: SystemEvent) -> None:
        received_callback.append(event)

    # Subscribe
    bus.subscribe(Topic.USER_REGISTERED, handler)
    bus.subscribe(Topic.USER_REGISTERED, callback_listener)

    # Publish
    evt = SystemEvent(
        topic=Topic.USER_REGISTERED,
        source="AuthService",
        payload={"user_id": "usr_100", "email": "test@nova.ai"},
    )
    await bus.publish(evt)

    # Verify notifications received
    assert len(handler.received_events) == 1
    assert handler.received_events[0].event_id == evt.event_id
    assert len(received_callback) == 1
    assert received_callback[0].event_id == evt.event_id

    # Verify event stored
    assert len(store.list(Topic.USER_REGISTERED)) == 1

    # Unsubscribe
    bus.unsubscribe(Topic.USER_REGISTERED, callback_listener)
    received_callback.clear()
    await bus.publish(evt)
    assert len(received_callback) == 0


@pytest.mark.anyio
async def test_system_event_bus_batch_publish() -> None:
    """Verifies batch publishing of multiple events concurrently."""
    bus = EventBus()
    handler = DummyEventHandler([Topic.CONVERSATION_CREATED, Topic.CONVERSATION_UPDATED])
    bus.subscribe(Topic.CONVERSATION_CREATED, handler)
    bus.subscribe(Topic.CONVERSATION_UPDATED, handler)

    evts = [
        SystemEvent(topic=Topic.CONVERSATION_CREATED, source="Conversations", payload={"id": "conv_1"}),
        SystemEvent(topic=Topic.CONVERSATION_UPDATED, source="Conversations", payload={"id": "conv_1"}),
    ]

    await bus.publish_batch(evts)
    assert len(handler.received_events) == 2
    assert {e.topic for e in handler.received_events} == {
        Topic.CONVERSATION_CREATED,
        Topic.CONVERSATION_UPDATED,
    }


@pytest.mark.anyio
async def test_system_event_bus_broadcast() -> None:
    """Verifies that broadcast delivers the event to all unique subscribers regardless of topic registration."""
    bus = EventBus()
    handler_user = DummyEventHandler([Topic.USER_REGISTERED])
    handler_agent = DummyEventHandler([Topic.AGENT_STARTED])

    bus.subscribe(Topic.USER_REGISTERED, handler_user)
    bus.subscribe(Topic.AGENT_STARTED, handler_agent)

    broadcast_evt = SystemEvent(
        topic=Topic.AI_REQUEST,
        source="Gateway",
        payload={"query": "hello"},
    )
    await bus.broadcast(broadcast_evt)

    # Both handlers receive the event since it's a broadcast
    assert len(handler_user.received_events) == 1
    assert len(handler_agent.received_events) == 1


@pytest.mark.anyio
async def test_system_event_bus_replay() -> None:
    """Verifies event storage and chronological replay capabilities."""
    store = EventStore()
    bus = EventBus(store)

    handler = DummyEventHandler([Topic.JOB_COMPLETED])
    bus.subscribe(Topic.JOB_COMPLETED, handler)

    now = datetime.now(UTC)
    evt_old = SystemEvent(
        topic=Topic.JOB_COMPLETED,
        source="Scheduler",
        payload={"job": "job_1"},
        timestamp=now - timedelta(minutes=5),
    )
    evt_new = SystemEvent(
        topic=Topic.JOB_COMPLETED,
        source="Scheduler",
        payload={"job": "job_2"},
        timestamp=now,
    )

    await bus.publish(evt_old)
    await bus.publish(evt_new)

    # Clear handler history
    handler.received_events.clear()

    # Replay matching topic since 3 minutes ago (only evt_new should run)
    await bus.replay(topic=Topic.JOB_COMPLETED, since=now - timedelta(minutes=3))
    assert len(handler.received_events) == 1
    assert handler.received_events[0].payload["job"] == "job_2"

    # Replay all since 6 minutes ago (both should run chronologically)
    handler.received_events.clear()
    await bus.replay(topic=Topic.JOB_COMPLETED, since=now - timedelta(minutes=6))
    assert len(handler.received_events) == 2
    assert handler.received_events[0].payload["job"] == "job_1"
    assert handler.received_events[1].payload["job"] == "job_2"


@pytest.mark.anyio
async def test_system_event_bus_errors() -> None:
    """Verifies validation publish errors and handler error conversions."""
    bus = EventBus()
    handler = DummyEventHandler([Topic.USER_LOGIN])
    bus.subscribe(Topic.USER_LOGIN, handler)

    # 1. Invalid publish error
    with pytest.raises(EventPublishError):
        await bus.publish(SystemEvent(topic=Topic.USER_LOGIN, source="", payload={}))

    # 2. Handler error propagation
    handler.should_fail = True
    evt = SystemEvent(topic=Topic.USER_LOGIN, source="IdentityService", payload={})
    with pytest.raises(HandlerError):
        await bus.publish(evt)
