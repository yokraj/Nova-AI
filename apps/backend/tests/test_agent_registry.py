"""Unit tests for the Agent Registry and Discovery.

Verifies agent registration, naming collisions checks, unregistration lists,
health updates, and python package scans discovery methods.
"""

from typing import Dict, Any
import uuid
import pytest

from app.agents import (
    AgentCapability,
    AgentContext,
    AgentDescriptor,
    AgentDuplicateError,
    AgentHealth,
    AgentMetadata,
    AgentPermission,
    AgentRegistry,
    AgentResult,
    AgentStatus,
    BaseAgent,
    Discovery,
    DiscoveryService,
    HealthReport,
    DuplicateAgentError,
    AgentRegistrationError,
    AgentNotFoundError,
    AgentInitializationError,
)



class DummyRegistryAgent(BaseAgent):
    """Mock agent implementation to check lifecycle status updates."""

    def __init__(self, metadata: AgentMetadata) -> None:
        super().__init__(metadata)
        self.initialized = False
        self.shutdown_completed = False

    async def initialize(self) -> None:
        self.initialized = True

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        return AgentResult(success=True, response="Done", execution_time=0.1)

    async def shutdown(self) -> None:
        self.shutdown_completed = True

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


def test_agent_registry_crud_operations() -> None:
    """Verifies register, exist checks, list, and unregister operations."""
    registry = AgentRegistry()

    meta = AgentMetadata(name="UniqueAgent", description="crud test")
    agent = DummyRegistryAgent(meta)

    descriptor = AgentDescriptor(
        id=uuid.uuid4(),
        name="UniqueAgent",
        description="crud test desc",
        capabilities=[AgentCapability.CHAT],
        permissions=[AgentPermission.NETWORK],
    )

    # Register
    registry.register(agent, descriptor)
    assert registry.exists(descriptor.id) is True
    assert registry.get(descriptor.id) == agent

    # List
    agents_list = registry.list()
    assert len(agents_list) == 1
    assert agents_list[0].name == "UniqueAgent"

    # Capability and Permission search
    chat_agents = registry.find_by_capability(AgentCapability.CHAT)
    assert len(chat_agents) == 1
    assert chat_agents[0].id == descriptor.id

    code_agents = registry.find_by_capability(AgentCapability.CODE)
    assert len(code_agents) == 0

    net_agents = registry.find_by_permission(AgentPermission.NETWORK)
    assert len(net_agents) == 1

    # Unregister
    registry.unregister(descriptor.id)
    assert registry.exists(descriptor.id) is False


def test_agent_registry_duplicate_violations() -> None:
    """Verifies that duplicate registrations raise AgentDuplicateError."""
    registry = AgentRegistry()

    agent_id = uuid.uuid4()
    desc1 = AgentDescriptor(id=agent_id, name="AgentOne", description="test")
    desc2 = AgentDescriptor(id=agent_id, name="AgentTwo", description="test")
    desc3 = AgentDescriptor(id=uuid.uuid4(), name="AgentOne", description="test")

    agent1 = DummyRegistryAgent(AgentMetadata(name="AgentOne", description="test"))
    agent2 = DummyRegistryAgent(AgentMetadata(name="AgentTwo", description="test"))
    agent3 = DummyRegistryAgent(AgentMetadata(name="AgentOne", description="test"))

    registry.register(agent1, desc1)

    # Duplicate ID
    with pytest.raises(AgentDuplicateError):
        registry.register(agent2, desc2)

    # Duplicate Name
    with pytest.raises(AgentDuplicateError):
        registry.register(agent3, desc3)


@pytest.mark.anyio
async def test_agent_registry_initialization_lifecycle() -> None:
    """Verifies initialize_all and shutdown_all correctly changes states."""
    registry = AgentRegistry()

    meta = AgentMetadata(name="LifeAgent", description="life")
    agent = DummyRegistryAgent(meta)
    desc = AgentDescriptor(name="LifeAgent", description="life desc")

    registry.register(agent, desc)
    assert registry.health(desc.id).status == AgentStatus.REGISTERED

    # Initialize all
    await registry.initialize_all()
    assert agent.initialized is True
    assert registry.health(desc.id).status == AgentStatus.INITIALIZED

    # Shutdown all
    await registry.shutdown_all()
    assert agent.shutdown_completed is True
    assert registry.health(desc.id).status == AgentStatus.STOPPED


class FailingRegistryAgent(BaseAgent):
    """Mock agent that fails during initialize callback."""

    async def initialize(self) -> None:
        raise ValueError("Initialization failure simulation")

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        return AgentResult(success=False, response="Failed", execution_time=0.0)

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "error"}


class DependentRegistryAgent(BaseAgent):
    """Mock agent that has dependencies."""
    dependencies = ["LifeAgent"]  # Depend on Agent with name "LifeAgent"

    async def initialize(self) -> None:
        pass

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        return AgentResult(success=True, response="Done", execution_time=0.1)

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


def test_agent_registry_discovery() -> None:
    """Verifies dynamic python modules discovery logic."""
    registry = AgentRegistry()
    discovery = Discovery(registry)

    # Scanning app/agents submodules (should contain DummyRegistryAgent if registered, but scans packages)
    # Validate method
    assert discovery.validate(DummyRegistryAgent) is True
    assert discovery.validate(BaseAgent) is False

    # Discover app.agents
    classes = discovery.discover("app.agents")
    assert isinstance(classes, list)


def test_agent_registry_new_features() -> None:
    """Verifies new specifications of M2.5.2."""
    registry = AgentRegistry()

    # 1. Register with implicit descriptor
    meta = AgentMetadata(
        id=uuid.uuid4(),
        name="AutoDescAgent",
        description="Implicit descriptor test",
        capabilities=[AgentCapability.VISION],
        permissions=[AgentPermission.CAMERA]
    )
    agent = DummyRegistryAgent(meta)
    
    registry.register(agent)  # descriptor omitted
    assert registry.exists(meta.id) is True
    
    desc = registry.list()[0]
    assert desc.name == "AutoDescAgent"
    assert desc.capabilities == [AgentCapability.VISION]
    assert desc.permissions == [AgentPermission.CAMERA]
    assert desc.enabled is True
    assert desc.tags == []

    # 2. Enabled and disabled lists
    assert len(registry.enabled_agents()) == 1
    assert len(registry.disabled_agents()) == 0

    # Let's register a disabled agent
    disabled_meta = AgentMetadata(name="DisabledAgent", description="disabled test")
    disabled_agent = DummyRegistryAgent(disabled_meta)
    disabled_desc = AgentDescriptor(
        id=disabled_meta.id,
        name="DisabledAgent",
        description="disabled test",
        enabled=False
    )
    registry.register(disabled_agent, disabled_desc)
    
    assert len(registry.enabled_agents()) == 1
    assert len(registry.disabled_agents()) == 1
    assert registry.disabled_agents()[0].name == "DisabledAgent"

    # 3. Global health check showing dict of reports
    all_health = registry.health()
    assert isinstance(all_health, dict)
    assert meta.id in all_health
    assert disabled_meta.id in all_health
    assert isinstance(all_health[meta.id], HealthReport)
    assert all_health[meta.id].status == AgentStatus.REGISTERED
    assert all_health[disabled_meta.id].status == AgentStatus.DISABLED

    # Single health check
    single_health = registry.health(meta.id)
    assert isinstance(single_health, HealthReport)
    assert single_health.error_count == 0


@pytest.mark.anyio
async def test_agent_registry_failures() -> None:
    """Verifies validation and initialization failure scenarios."""
    registry = AgentRegistry()

    # 1. Invalid agent registration check
    with pytest.raises(AgentRegistrationError):
        registry.register("not_an_agent")  # type: ignore

    # 2. Initialization failure check
    fail_meta = AgentMetadata(name="FailingAgent", description="fails")
    fail_agent = FailingRegistryAgent(fail_meta)
    fail_desc = AgentDescriptor(name="FailingAgent", description="fails")
    
    registry.register(fail_agent, fail_desc)
    
    with pytest.raises(AgentInitializationError):
        await registry.initialize_all()
        
    assert registry.health(fail_desc.id).status == AgentStatus.FAILED
    assert registry.health(fail_desc.id).error_count == 1


def test_agent_registry_dependency_checks() -> None:
    """Verifies dependency_check method on DiscoveryService."""
    registry = AgentRegistry()
    discovery_service = DiscoveryService(registry)

    # Register dependent agent
    dep_meta = AgentMetadata(name="DependentAgent", description="dep test")
    dep_agent = DependentRegistryAgent(dep_meta)
    dep_desc = AgentDescriptor(name="DependentAgent", description="dep test")
    registry.register(dep_agent, dep_desc)

    # dependency_check should return False since "LifeAgent" is not registered
    assert discovery_service.dependency_check(dep_desc.id) is False
    assert discovery_service.dependency_check() is False

    # Register "LifeAgent"
    life_meta = AgentMetadata(name="LifeAgent", description="dependency")
    life_agent = DummyRegistryAgent(life_meta)
    life_desc = AgentDescriptor(name="LifeAgent", description="dependency")
    registry.register(life_agent, life_desc)

    # dependency_check should now return True
    assert discovery_service.dependency_check(dep_desc.id) is True
    assert discovery_service.dependency_check() is True

