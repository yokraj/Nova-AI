"""Unit tests for the Enterprise Agent SDK Foundation.

Verifies SDK initialization, metadata versioning, context tracing, configuration loading
and merging, lifecycle state transitions, and health telemetry checks.
"""

import asyncio
from datetime import datetime, UTC
import uuid
import pytest

from app.agent_sdk import (
    BaseAgentSDK,
    SDKConfiguration,
    SDKContext,
    SDKMetadata,
    HealthStatus,
    SDKInitializationError,
    SDKConfigurationError,
    SDKRuntimeError,
)


class DummyAgentSDK(BaseAgentSDK):
    """Concrete subclass of BaseAgentSDK for testing lifecycle operations."""

    pass


def test_sdk_metadata() -> None:
    """Verifies SDKMetadata instantiation and default version values."""
    meta = SDKMetadata(agent_name="TestAgent")
    assert meta.agent_name == "TestAgent"
    assert meta.sdk_version == "1.0.0"
    assert meta.runtime_version == "Python 3.14"


def test_sdk_configuration_validation_and_merge() -> None:
    """Verifies configuration loading, invalid limits validation, and merging."""
    config = SDKConfiguration()
    config.load({"settings": {"mode": "auto"}, "timeout": 15.0})
    assert config.settings["mode"] == "auto"
    assert config.timeout == 15.0

    # Validation check
    config.validate()

    with pytest.raises(SDKConfigurationError):
        invalid_config = SDKConfiguration(timeout=-5.0)
        invalid_config.validate()

    # Load failure checks
    with pytest.raises(SDKConfigurationError):
        config.load({"timeout": "not-a-number"})

    # Merge configuration
    config_a = SDKConfiguration(settings={"a": 1}, timeout=10.0)
    config_b = SDKConfiguration(settings={"b": 2}, api_key="secret")
    merged = config_a.merge(config_b)

    assert merged.settings == {"a": 1, "b": 2}
    assert merged.timeout == 10.0
    assert merged.api_key == "secret"


def test_sdk_context() -> None:
    """Verifies SDKContext request parameters tracing."""
    conv_id = uuid.uuid4()
    req_id = uuid.uuid4()
    ctx = SDKContext(
        user_id="user_123",
        conversation_id=conv_id,
        request_id=req_id,
        ai_provider="ollama",
        selected_model="llama3",
        locale="en-GB",
        timezone="Europe/London",
    )

    assert ctx.user_id == "user_123"
    assert ctx.conversation_id == conv_id
    assert ctx.request_id == req_id
    assert ctx.locale == "en-GB"


@pytest.mark.anyio
async def test_sdk_lifecycle_and_health() -> None:
    """Verifies start, stop, double-start exceptions, and health telemetry reports."""
    meta = SDKMetadata(agent_name="LifecycleAgent")
    sdk = DummyAgentSDK(meta)

    # Initial state
    assert sdk.health().healthy is False
    assert sdk.health().uptime == 0.0

    # Start up
    await sdk.initialize()
    assert sdk.health().healthy is True
    await asyncio.sleep(0.05)
    assert sdk.health().uptime > 0.0

    # Verify double startup error
    with pytest.raises(SDKInitializationError):
        await sdk.initialize()

    # Context setting
    ctx = SDKContext(
        user_id="user_1",
        conversation_id=uuid.uuid4(),
        ai_provider="ollama",
        selected_model="llama3",
    )
    sdk.set_context(ctx)
    assert sdk.context is not None
    assert sdk.health().last_execution is not None

    # Restart
    await sdk.lifecycle_manager.restart()
    assert sdk.health().healthy is True

    # Shutdown
    await sdk.shutdown()
    assert sdk.health().healthy is False
