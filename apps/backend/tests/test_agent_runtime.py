"""Unit tests for the Agent Runtime Foundation.

Verifies metadata models validations, context values, permissions configuration,
capabilities, and subclass lifecycle execution methods inheritance.
"""

from typing import Any, Dict
import uuid
import pytest
from pydantic import ValidationError

from app.agents import (
    AgentCapability,
    AgentContext,
    AgentMetadata,
    AgentPermission,
    AgentResult,
    BaseAgent,
)


class DummyAgent(BaseAgent):
    """Minimal dummy implementation to verify BaseAgent subclassing interface."""

    def __init__(self, metadata: AgentMetadata) -> None:
        super().__init__(metadata)
        self.initialized = False
        self.shutdown_completed = False

    async def initialize(self) -> None:
        self.initialized = True

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        return AgentResult(
            success=True,
            response=f"Dummy response to: {prompt}",
            metadata={"processed_by": self.metadata.name},
            execution_time=0.05,
        )

    async def shutdown(self) -> None:
        self.shutdown_completed = True

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok", "agent_id": str(self.metadata.id)}


def test_agent_metadata_pydantic_validation() -> None:
    """Verifies metadata validation requires name and description."""
    # Correct configuration
    meta = AgentMetadata(
        name="TestAgent",
        description="Verifies functionality.",
        capabilities=[AgentCapability.CHAT],
        permissions=[AgentPermission.FILESYSTEM],
    )
    assert meta.name == "TestAgent"
    assert meta.version == "0.1.0"
    assert len(meta.capabilities) == 1

    # Missing description field triggers validation error
    with pytest.raises(ValidationError):
        AgentMetadata(name="BadAgent")  # type: ignore


def test_agent_context_validation() -> None:
    """Verifies that AgentContext validates UUID inputs correctly."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    context = AgentContext(
        user_id=user_id,
        conversation_id=conv_id,
        locale="en-GB",
        timezone="GMT",
    )
    assert context.user_id == user_id
    assert context.conversation_id == conv_id
    assert context.ai_provider == "ollama"

    # Invalid user_id string triggers validation error
    with pytest.raises(ValidationError):
        AgentContext(user_id="invalid-uuid", conversation_id=conv_id)  # type: ignore


@pytest.mark.anyio
async def test_base_agent_lifecycle_and_inheritance() -> None:
    """Verifies agent lifecycle callbacks subclassing works correctly."""
    meta = AgentMetadata(
        name="LifecycleAgent",
        description="lifecycle testing",
    )
    agent = DummyAgent(meta)

    # Verify metadata getter works
    assert agent.metadata.name == "LifecycleAgent"

    # 1. Initialize
    await agent.initialize()
    assert agent.initialized is True

    # 2. Execute
    context = AgentContext(
        user_id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
    )
    result = await agent.execute(context, "Run action")
    assert result.success is True
    assert result.response == "Dummy response to: Run action"
    assert result.metadata["processed_by"] == "LifecycleAgent"
    assert result.execution_time == 0.05

    # 3. Health
    health = await agent.health()
    assert health["status"] == "ok"

    # 4. Shutdown
    await agent.shutdown()
    assert agent.shutdown_completed is True
