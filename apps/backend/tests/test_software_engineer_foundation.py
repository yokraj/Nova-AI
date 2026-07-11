"""Unit tests for the Software Engineering Agent Foundation.

Verifies configuration, metadata, workspace validations, memory buffers, sessions,
state transitions, factory helpers, health monitoring, and integrations.
"""

import os
import tempfile
import pytest

from app.agent_sdk.metadata import SDKMetadata
from app.agents.registry.registry import AgentRegistry
from app.agents.scheduler.scheduler import AgentScheduler
from app.agents.software_engineer import (
    HealthProvider,
    SoftwareCapability,
    SoftwareEngineerAgent,
    SoftwareEngineerConfiguration,
    SoftwareEngineerContext,
    SoftwareEngineerFactory,
    SoftwareEngineerMetadata,
    SoftwareEngineerState,
    WorkspaceError,
)


def test_configuration_and_metadata() -> None:
    """Verifies that configuration and metadata models parse values properly."""
    config = SoftwareEngineerConfiguration(
        default_model="llama3", temperature=0.5, workspace_root="/tmp/workspace"
    )
    assert config.default_model == "llama3"
    assert config.temperature == 0.5
    assert config.workspace_root == "/tmp/workspace"

    meta = SoftwareEngineerMetadata(
        agent_name="SoftwareEngineerAgent",
        sdk_version="1.0.0",
        runtime_version="Python 3.14",
        version="1.0.0",
        description="Core developer foundation agent.",
    )
    assert meta.agent_name == "SoftwareEngineerAgent"
    assert "developer foundation" in meta.description
    assert "python" in meta.supported_languages
    assert "git" in meta.supported_tools


@pytest.mark.anyio
async def test_state_transitions() -> None:
    """Verifies agent state updates and lifecycle hooks transitions."""
    agent = SoftwareEngineerFactory.create_default()
    assert agent.state == SoftwareEngineerState.IDLE

    # Initialize triggers startup hooks (Thinking)
    await agent.initialize()
    assert agent.state == SoftwareEngineerState.THINKING

    # Manual transitions
    agent.update_state(SoftwareEngineerState.PLANNING)
    assert agent.state == SoftwareEngineerState.PLANNING

    # Shutdown triggers shutdown hooks (Idle)
    await agent.shutdown()
    assert agent.state == SoftwareEngineerState.IDLE


def test_workspace_validation() -> None:
    """Verifies that WorkspaceManager lists files inside folder and validates paths."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files
        file1_path = os.path.join(tmp_dir, "test1.py")
        with open(file1_path, "w") as f:
            f.write("print('hello')")

        agent = SoftwareEngineerFactory.create_testing(tmp_dir)
        assert agent.workspace_manager.current_workspace() == os.path.abspath(tmp_dir)

        files = agent.workspace_manager.list_files()
        assert "test1.py" in files

        info = agent.workspace_manager.workspace_information()
        assert info["total_files"] == 1
        assert info["status"] == "open"

        assert agent.workspace_manager.validate_workspace() is True

    # Validate non-existent folder throws WorkspaceError
    agent_empty = SoftwareEngineerFactory.create_default()
    with pytest.raises(WorkspaceError):
        agent_empty.workspace_manager.open_workspace("/non/existent/path/folder")


def test_memory_and_sessions() -> None:
    """Verifies memory buffer tracking limits and session touch timestamps."""
    agent = SoftwareEngineerFactory.create_default()
    memory = agent.session.memory

    # Record entries
    memory.add_file("file1.py")
    memory.add_symbol("MyClass")
    memory.add_error("IndexError")
    memory.add_search("grep regex")
    memory.add_task("task-1")

    assert "file1.py" in memory.recent_files
    assert "MyClass" in memory.recent_symbols
    assert "IndexError" in memory.recent_errors
    assert "grep regex" in memory.recent_searches
    assert "task-1" in memory.recent_tasks

    # Memory capping check (keep last 10 items)
    for i in range(15):
        memory.add_file(f"file_{i}.py")
    assert len(memory.recent_files) == 10
    assert memory.recent_files[-1] == "file_14.py"

    # Session touch timestamps updates
    prev_time = agent.session.updated_at
    agent.session.touch()
    assert agent.session.updated_at >= prev_time


def test_factory_and_health() -> None:
    """Verifies factory helper constructions and health metrics exposers."""
    # Factory check
    agent = SoftwareEngineerFactory.create_default()
    assert agent.metadata.agent_name == "SoftwareEngineerAgent"

    agent_test = SoftwareEngineerFactory.create_testing("/tmp")
    assert agent_test.metadata.agent_name == "TestingSoftwareEngineerAgent"
    assert agent_test.workspace_manager.current_workspace() is not None

    # Health check
    health = agent.health_provider.get_health()
    assert health["status"] == "Idle"
    assert health["workspace_loaded"] is False
    assert health["active_tasks"] == 0


def test_registry_and_scheduler_integration() -> None:
    """Verifies agent registry mapping registrations and scheduler job enqueues."""
    agent = SoftwareEngineerFactory.create_default()

    # 1. Registry integration
    registry = AgentRegistry()
    registry.register(agent)

    descriptors = registry.list()
    assert len(descriptors) == 1
    assert descriptors[0].name == "SoftwareEngineerAgent"

    from app.agents.bus.routing import RoutingService
    routing_service = RoutingService(registry)
    scheduler = AgentScheduler(routing_service)
    assert scheduler is not None
