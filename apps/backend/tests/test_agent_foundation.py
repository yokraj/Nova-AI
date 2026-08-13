"""Unit tests for the Multi-Agent Foundation framework.
"""

import pytest
import asyncio
from datetime import datetime

from app.ai.agents.configuration import MultiAgentFoundationConfiguration
from app.ai.agents.exceptions import (
    AgentStateError,
    AgentRegistrationError,
    AgentPermissionsError
)
from app.ai.agents.models import AgentMetadata, AgentDescriptor, AgentCapability, AgentContext
from app.ai.agents.state_machine import AgentStateValue
from app.ai.agents.implementations.mock_agent import MockAgent
from app.ai.agents.manager import AgentManager

@pytest.mark.anyio
async def test_agent_configuration():
    """Verifies settings model initialization."""
    config = MultiAgentFoundationConfiguration()
    assert config.enabled is True
    assert config.registry.maximum_agents == 100
    assert config.manager.heartbeat_interval == 10.0

@pytest.mark.anyio
async def test_agent_lifecycle_and_state_machine():
    """Verifies legal transitions CREATED -> INITIALIZING -> READY -> BUSY -> STOPPED."""
    meta = AgentMetadata(
        id="test_lifecycle",
        name="LifecycleAgent",
        type="test_agent",
        capabilities=[AgentCapability(name="testing", description="Capability to test")]
    )
    agent = MockAgent(metadata=meta)
    
    assert agent.state == AgentStateValue.CREATED
    
    # Transition to initializing
    await agent.initialize()
    assert agent.state == AgentStateValue.INITIALIZING
    
    # Transition to starting/ready
    await agent.start()
    assert agent.state == AgentStateValue.READY
    
    # Execution transition to busy then ready
    res = await agent.execute("Simulated Task Input", execution_id="exec_001")
    assert res.status == "success"
    assert res.data["mock_result"] == "Successfully completed: Simulated Task Input"
    assert agent.state == AgentStateValue.READY
    
    # Stop transition
    await agent.stop()
    assert agent.state == AgentStateValue.STOPPED
    
    await agent.shutdown()

@pytest.mark.anyio
async def test_illegal_state_transition():
    """Verifies that illegal status transitions raise errors."""
    meta = AgentMetadata(id="test_illegal", name="IllegalAgent", type="test")
    agent = MockAgent(metadata=meta)
    
    # Directly running start before initializing is illegal
    with pytest.raises(AgentStateError):
        await agent.start()

@pytest.mark.anyio
async def test_agent_registry_and_discovery():
    """Verifies adding, removing, and looking up registration blueprints by ID and alias."""
    manager = AgentManager()
    registry = manager.registry
    
    meta = AgentMetadata(
        id="queryable_agent",
        name="QueryableAgent",
        type="search_type",
        capabilities=[AgentCapability(name="debugging", description="Debug application issues")],
        tags=["dev-tag"]
    )
    descriptor = AgentDescriptor(
        class_path="app.ai.agents.implementations.mock_agent.MockAgent",
        dependencies=[]
    )
    
    registry.register(descriptor, meta)
    assert registry.exists("queryable_agent") is True
    assert registry.exists("QueryableAgent") is True  # Case-insensitive alias matching
    
    # Run Discovery queries
    from app.ai.agents.discovery import DiscoveryService
    discovery = DiscoveryService(registry)
    
    found_by_cap = discovery.discover_by_capability("debugging")
    assert len(found_by_cap) == 1
    assert found_by_cap[0].metadata.id == "queryable_agent"
    
    found_by_type = discovery.discover_by_type("search_type")
    assert len(found_by_type) == 1
    
    found_by_tag = discovery.discover_by_tag("dev-tag")
    assert len(found_by_tag) == 1

@pytest.mark.anyio
async def test_dependency_container_and_locator():
    """Verifies DI container resolution static access points."""
    from app.ai.agents.service_locator import ServiceLocator
    container = ServiceLocator.get_container()
    
    container.register_singleton("dummy_dep", lambda: "ServiceMockInstance")
    assert container.resolve("dummy_dep") == "ServiceMockInstance"
    assert ServiceLocator.resolve("dummy_dep") == "ServiceMockInstance"

@pytest.mark.anyio
async def test_event_bus():
    """Verifies asynchronous broadcast event dispatches to active listeners."""
    from app.ai.agents.event_bus import EventBus
    bus = EventBus()
    
    results = []
    async def test_listener(agent_id: str) -> None:
        results.append(agent_id)

    bus.subscribe("AgentStarted", test_listener)
    await bus.publish("AgentStarted", agent_id="software_engineer_agent")
    
    assert results == ["software_engineer_agent"]

@pytest.mark.anyio
async def test_permissions_system():
    """Verifies hierarchical permission checks."""
    from app.ai.agents.permissions import PermissionsSystem, PermissionProfile
    permissions = PermissionsSystem()
    
    # Developer rank allows ReadOnly access
    permissions.check_clearance(PermissionProfile.DEVELOPER, PermissionProfile.READ_ONLY)
    
    # ReadOnly rank prohibits Developer access
    with pytest.raises(AgentPermissionsError):
        permissions.check_clearance(PermissionProfile.READ_ONLY, PermissionProfile.DEVELOPER)

@pytest.mark.anyio
async def test_scheduler():
    """Verifies immediate and delayed task execution loops."""
    from app.ai.agents.scheduler import AgentScheduler
    scheduler = AgentScheduler()
    
    counter = 0
    async def scheduled_task() -> None:
        nonlocal counter
        counter += 1

    scheduler.schedule_immediate(scheduled_task())
    await asyncio.sleep(0.01)
    assert counter == 1

    scheduler.schedule_delayed(0.02, scheduled_task())
    await asyncio.sleep(0.05)
    assert counter == 2

    scheduler.shutdown()

@pytest.mark.anyio
async def test_diagnostics_and_heartbeat():
    """Verifies heartbeat pulse emissions and diagnostics recording."""
    manager = AgentManager()
    
    meta = AgentMetadata(id="diagnostic_agent", name="DiagnosticAgent", type="test")
    descriptor = AgentDescriptor(class_path="app.ai.agents.implementations.mock_agent.MockAgent")
    manager.registry.register(descriptor, meta)
    
    await manager.start_agent("diagnostic_agent")
    agent = manager.get_agent("diagnostic_agent")
    assert agent is not None

    pulse = manager.heartbeat.generate_heartbeat(agent)
    assert pulse.agent_id == "diagnostic_agent"
    assert pulse.state == AgentStateValue.READY
    
    await manager.stop_agent("diagnostic_agent")

@pytest.mark.anyio
async def test_agent_manager_orchestration():
    """Verifies complete Manager-driven agent lifecycles."""
    manager = AgentManager()
    
    meta = AgentMetadata(id="managed_test", name="ManagedTest", type="test")
    descriptor = AgentDescriptor(class_path="app.ai.agents.implementations.mock_agent.MockAgent")
    manager.registry.register(descriptor, meta)
    
    # Start agent through manager
    await manager.start_agent("managed_test")
    agent = manager.get_agent("managed_test")
    assert agent is not None
    assert agent.state == AgentStateValue.READY
    
    # Execute task
    result = await agent.execute("Pipeline test task")
    assert result.status == "success"
    
    # Teardown
    await manager.shutdown()
    assert manager.get_agent("managed_test") is None
