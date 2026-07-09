"""Unit tests for the Nova AI Runtime Kernel and Capability SDK.

Verifies kernel boots/shutdown lifecycles, service discovery registry mappings,
event bus publish/replay mechanisms, resource managers threshold checks, and
capability states transitions.
"""

from typing import Any
import pytest

from app.runtime import (
    CapabilityException,
    CapabilityState,
    ICapability,
    KernelState,
    ResourceExhaustedException,
    RuntimeContext,
    RuntimeEvent,
    RuntimeKernel,
    RuntimeManager,
)


class MockCapability(ICapability):
    """Custom mock capability implementing ICapability for testing lifecycle transitions."""

    def __init__(self, cap_id: str) -> None:
        self.cap_id = cap_id
        self.state = CapabilityState.INITIALIZED
        self.initialized = False

    def get_id(self) -> str:
        return self.cap_id

    def get_state(self) -> CapabilityState:
        return self.state

    async def initialize(self, context: Any) -> None:
        self.initialized = True

    async def activate(self) -> None:
        self.state = CapabilityState.ACTIVE

    async def suspend(self) -> None:
        self.state = CapabilityState.SUSPENDED

    async def terminate(self) -> None:
        self.state = CapabilityState.STOPPED


@pytest.mark.anyio
async def test_kernel_boot_and_shutdown() -> None:
    """Verifies that kernel initializes, boots all services, and shuts down gracefully."""
    kernel = RuntimeKernel(env="test")
    assert kernel.state == KernelState.OFFLINE

    # Boot kernel
    await kernel.boot()
    assert kernel.state == KernelState.ONLINE
    assert kernel.resource_manager.name == "resource_manager"

    # Verify boot event was published
    history = kernel.event_bus.get_history()
    assert len(history) == 1
    assert history[0].topic == "system.boot"

    # Shutdown kernel
    await kernel.shutdown()
    assert kernel.state == KernelState.OFFLINE


@pytest.mark.anyio
async def test_service_registry() -> None:
    """Verifies service registrations and list checks."""
    kernel = RuntimeKernel(env="test")
    services = kernel.service_registry.list_services()

    assert "resource_manager" in services
    assert "event_bus" in services
    assert "diagnostics" in services
    assert kernel.service_registry.get("event_bus") is kernel.event_bus


@pytest.mark.anyio
async def test_event_bus_matching_and_replay() -> None:
    """Verifies topic wildcard subscriptions and historical event replay loops."""
    kernel = RuntimeKernel(env="test")

    dispatched = []

    async def listener(event: RuntimeEvent) -> None:
        dispatched.append(event)

    # Subscribe before boot to capture boot events
    kernel.event_bus.subscribe("system.*", listener)

    await kernel.boot()

    # Publish matching event
    event_1 = RuntimeEvent(
        topic="system.alert", sender="test", payload={"msg": "alert"}
    )
    await kernel.event_bus.publish(event_1)

    # Publish non-matching event
    event_2 = RuntimeEvent(
        topic="capability.update", sender="test", payload={"msg": "update"}
    )
    await kernel.event_bus.publish(event_2)

    # Boot event + event_1 match pattern system.*
    assert len(dispatched) == 2
    assert dispatched[1].payload["msg"] == "alert"

    # Replay events from index 1 (which maps to event_1 in history index 1, index 0 is boot event)
    dispatched.clear()
    await kernel.event_bus.replay_events(start_index=1)
    assert len(dispatched) == 1
    assert dispatched[0].payload["msg"] == "alert"

    await kernel.shutdown()


@pytest.mark.anyio
async def test_capability_lifecycle() -> None:
    """Verifies manager capability SDK registrations and lifecycle state transitions."""
    kernel = RuntimeKernel(env="test")
    await kernel.boot()

    manager = RuntimeManager(kernel)
    cap = MockCapability("text_processor")

    # Register
    await manager.register_capability(cap)
    assert cap.initialized is True
    assert cap.get_state() == CapabilityState.INITIALIZED
    assert "text_processor" in manager.list_capabilities()

    # Activate
    await manager.activate_capability("text_processor")
    assert cap.get_state() == CapabilityState.ACTIVE

    # Suspend
    await manager.suspend_capability("text_processor")
    assert cap.get_state() == CapabilityState.SUSPENDED

    # Terminate
    await manager.terminate_capability("text_processor")
    assert cap.get_state() == CapabilityState.STOPPED

    await kernel.shutdown()


@pytest.mark.anyio
async def test_resource_manager_boundaries() -> None:
    """Verifies resource limits allocations and exhaustion checks."""
    kernel = RuntimeKernel(env="test")
    await kernel.boot()

    manager = kernel.resource_manager
    manager.allocate("max_threads", 50.0)

    # Request allocation exceeding max limit threshold (100.0)
    with pytest.raises(ResourceExhaustedException):
        manager.allocate("max_threads", 60.0)

    # Release and try again
    manager.release("max_threads", 20.0)
    manager.allocate("max_threads", 30.0)  # Total 60.0 allocated, works!

    util = manager.get_utilization()
    assert util["max_threads"]["allocated"] == 60.0

    await kernel.shutdown()


@pytest.mark.anyio
async def test_diagnostics_aggregates() -> None:
    """Verifies runtime diagnostics snapshot reports."""
    kernel = RuntimeKernel(env="test")
    await kernel.boot()

    report = kernel.diagnostics.get_diagnostics_report(["text_processor"])

    assert "services" in report
    assert "resources" in report
    assert "health" in report
    assert report["loaded_capabilities"] == ["text_processor"]
    assert report["system_cpu_mock"] > 0.0

    await kernel.shutdown()
