"""Unit tests for the Enterprise Permission Manager subsystem.

Verifies agent validation, policy evaluations (allow, deny, prompt),
manual grants and revocations, expiration of temporary grants, and listing permissions.
"""

import asyncio
from datetime import datetime, UTC
from typing import Any, Dict
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
from app.agents.permissions import (
    PermissionManager,
    PermissionRequest,
    PermissionResult,
    PermissionPolicy,
    PolicyEffect,
    PolicyDuration,
    ResourceType,
    PermissionDeniedError,
    PermissionExpiredError,
    InvalidPermissionError,
    PolicyViolationError,
)


class DummyPermissionAgent(BaseAgent):
    """Mock agent implementation for permission manager tests."""

    async def initialize(self) -> None:
        pass

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        return AgentResult(success=True, response="Done", execution_time=0.0)

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


@pytest.fixture
def registry_with_agents() -> AgentRegistry:
    """Fixture initializing registry with dummy agents."""
    registry = AgentRegistry()

    # Agent A: Enabled
    meta_a = AgentMetadata(name="AgentA", description="First agent")
    agent_a = DummyPermissionAgent(meta_a)
    registry.register(agent_a)

    # Agent B: Disabled
    meta_b = AgentMetadata(name="AgentB", description="Second agent")
    agent_b = DummyPermissionAgent(meta_b)
    desc_b = AgentDescriptor(name="AgentB", description="Second agent", enabled=False)
    registry.register(agent_b, desc_b)

    return registry


def test_agent_validation(registry_with_agents: AgentRegistry) -> None:
    """Verifies validate_agent checks registered and enabled states."""
    manager = PermissionManager(registry_with_agents)

    # Resolve agent ids
    agent_a_id = [d.id for d in registry_with_agents.list() if d.name == "AgentA"][0]
    agent_b_id = [d.id for d in registry_with_agents.list() if d.name == "AgentB"][0]
    random_id = uuid.uuid4()

    assert manager.validate_agent(agent_a_id) is True  # Registered and Enabled
    assert manager.validate_agent(agent_b_id) is False  # Registered but Disabled
    assert manager.validate_agent(random_id) is False  # Unregistered


def test_policy_allow_and_deny_evaluations(registry_with_agents: AgentRegistry) -> None:
    """Verifies that policies grant ALLOW and DENY properly and fall back correctly."""
    agent_a_id = [d.id for d in registry_with_agents.list() if d.name == "AgentA"][0]

    policy_allow = PermissionPolicy(
        policy_id="allow_fs",
        agent_id=str(agent_a_id),
        permission=AgentPermission.FILESYSTEM,
        resource_type=ResourceType.FILESYSTEM,
        resource_pattern="/tmp/*",
        effect=PolicyEffect.ALLOW,
        duration=PolicyDuration.PERMANENT,
    )

    policy_deny = PermissionPolicy(
        policy_id="deny_net",
        agent_id="*",
        permission=AgentPermission.NETWORK,
        resource_type=ResourceType.NETWORK,
        resource_pattern="*",
        effect=PolicyEffect.DENY,
        duration=PolicyDuration.PERMANENT,
    )

    manager = PermissionManager(registry_with_agents, policies=[policy_allow, policy_deny])

    # 1. ALLOW match
    req_allow = PermissionRequest(
        agent_id=agent_a_id,
        permission=AgentPermission.FILESYSTEM,
        resource="/tmp/test_file.txt",
        reason="Writing scratch files",
    )
    result_allow = manager.request_permission(req_allow)
    assert result_allow.granted is True
    assert "allow_fs" in result_allow.reason

    # 2. DENY match
    req_deny = PermissionRequest(
        agent_id=agent_a_id,
        permission=AgentPermission.NETWORK,
        resource="http://google.com",
        reason="Outgoing api call",
    )
    with pytest.raises(PermissionDeniedError):
        manager.request_permission(req_deny)

    # 3. Default Deny (no matching policy)
    req_default = PermissionRequest(
        agent_id=agent_a_id,
        permission=AgentPermission.CAMERA,
        resource="main_camera",
        reason="Take snap",
    )
    with pytest.raises(PermissionDeniedError):
        manager.request_permission(req_default)


def test_grant_and_revoke(registry_with_agents: AgentRegistry) -> None:
    """Verifies manual grants and revocations function correctly."""
    agent_a_id = [d.id for d in registry_with_agents.list() if d.name == "AgentA"][0]
    manager = PermissionManager(registry_with_agents)

    # Initial state
    assert manager.check_permission(agent_a_id, AgentPermission.MICROPHONE, "mic_device") is False

    # Manual grant
    manager.grant_permission(agent_a_id, AgentPermission.MICROPHONE, "mic_device")
    assert manager.check_permission(agent_a_id, AgentPermission.MICROPHONE, "mic_device") is True

    # Check non-matching path resource
    assert manager.check_permission(agent_a_id, AgentPermission.MICROPHONE, "other_mic") is False

    # Revoke
    manager.revoke_permission(agent_a_id, AgentPermission.MICROPHONE, "mic_device")
    assert manager.check_permission(agent_a_id, AgentPermission.MICROPHONE, "mic_device") is False


@pytest.mark.anyio
async def test_grant_expiration(registry_with_agents: AgentRegistry) -> None:
    """Verifies temporary grant rules expire correctly, raising PermissionExpiredError."""
    agent_a_id = [d.id for d in registry_with_agents.list() if d.name == "AgentA"][0]

    policy_temp = PermissionPolicy(
        policy_id="temp_allow",
        agent_id=str(agent_a_id),
        permission=AgentPermission.TERMINAL,
        resource_type=ResourceType.TERMINAL,
        resource_pattern="cmd.exe",
        effect=PolicyEffect.ALLOW,
        duration=PolicyDuration.TEMPORARY,
        ttl_seconds=1,  # Expires in 1 second
    )

    manager = PermissionManager(registry_with_agents, policies=[policy_temp])

    req = PermissionRequest(
        agent_id=agent_a_id,
        permission=AgentPermission.TERMINAL,
        resource="cmd.exe",
        reason="Run compilation tests",
    )
    result = manager.request_permission(req)
    assert result.granted is True
    assert result.expires_at is not None

    # Check immediately -> allowed
    assert manager.check_permission(agent_a_id, AgentPermission.TERMINAL, "cmd.exe") is True

    # Sleep past expiration (1.1 seconds)
    await asyncio.sleep(1.1)

    # Check after -> raises PermissionExpiredError
    with pytest.raises(PermissionExpiredError):
        manager.check_permission(agent_a_id, AgentPermission.TERMINAL, "cmd.exe")

    # Verify cleaned up from list
    assert len(manager.list_permissions(agent_a_id)) == 0


def test_list_permissions_filter(registry_with_agents: AgentRegistry) -> None:
    """Verifies list_permissions filters active grants correctly."""
    agent_a_id = [d.id for d in registry_with_agents.list() if d.name == "AgentA"][0]
    manager = PermissionManager(registry_with_agents)

    manager.grant_permission(agent_a_id, AgentPermission.CLIPBOARD, "sys_clip")
    manager.grant_permission(agent_a_id, AgentPermission.SCREEN, "monitor_1")

    # List specific agent
    grants_a = manager.list_permissions(agent_a_id)
    assert len(grants_a) == 2
    assert {g.permission for g in grants_a} == {AgentPermission.CLIPBOARD, AgentPermission.SCREEN}

    # List global
    all_grants = manager.list_permissions()
    assert len(all_grants) == 2
