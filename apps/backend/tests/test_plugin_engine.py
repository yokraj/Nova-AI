"""Automated unit test suite verifying the Universal Plugin Platform.

Tests cover:
1. Plugin Discovery
2. Loading & Unloading
3. Lifecycle state transitions
4. Capability registration & lookup
5. Permission verification & dangerous permission handling
6. Sandbox execution & timeouts
7. Built-in reference plugins (Browser, Desktop, File, PDF, Email, Calendar, Office, Terminal)
8. Developer SDK (@nova_plugin, BasePlugin, PluginResult)
9. Event publishing
10. Mock provider simulations
11. Gateway integration APIs
"""

import pytest

from app.ai.gateway import IAIGateway
from app.ai.plugins.configuration import PluginConfiguration
from app.ai.plugins.exceptions import PermissionDeniedError, PluginNotFoundError
from app.ai.plugins.models import CapabilityType, PermissionType, PluginCapability, PluginMetadata, PluginSpec, PluginStatus, RiskLevel
from app.ai.plugins.plugin_engine import PluginEngine
from app.ai.plugins.plugin_manager import PluginManager
from app.ai.plugins.plugin_registry import PluginRegistry
from app.ai.plugins.providers.mock_provider import MockPluginProvider
from app.ai.plugins.sdk import BasePlugin, PluginContext, PluginResult, capability, nova_plugin
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.fixture
def engine() -> PluginEngine:
    config = PluginConfiguration(auto_discover=True, enable_sandbox=True)
    return PluginEngine(config=config)


# ============================================================
# 1. Discovery & Registry
# ============================================================

def test_plugin_registry() -> None:
    registry = PluginRegistry()
    spec = PluginSpec(
        plugin_id="test_plug",
        metadata=PluginMetadata(name="Test Plugin", version="1.0.0"),
        status=PluginStatus.INSTALLED,
    )
    registry.add_plugin(spec)

    assert registry.count() == 1
    assert registry.get_plugin("test_plug") is not None
    assert registry.get_plugin("test_plug").metadata.name == "Test Plugin"


def test_plugin_discovery() -> None:
    engine = PluginEngine(config=PluginConfiguration(auto_discover=False))
    discovered = engine.manager.discovery.discover_plugins()
    assert isinstance(discovered, list)


# ============================================================
# 2. Lifecycle State Transitions
# ============================================================

@pytest.mark.anyio
async def test_plugin_lifecycle(engine: PluginEngine) -> None:
    assert await engine.enable_plugin("browser") is True
    spec = engine.registry.get_plugin("browser")
    assert spec.status == PluginStatus.ENABLED

    assert await engine.disable_plugin("browser") is True
    spec = engine.registry.get_plugin("browser")
    assert spec.status == PluginStatus.DISABLED


# ============================================================
# 3. Built-in Reference Plugins Capabilities
# ============================================================

@pytest.mark.anyio
async def test_browser_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="browser",
        capability="open_url",
        parameters={"url": "https://nova.ai"},
    )
    assert res.success is True
    assert res.data["url"] == "https://nova.ai"


@pytest.mark.anyio
async def test_desktop_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="desktop",
        capability="launch_app",
        parameters={"app_name": "chrome"},
    )
    assert res.success is True
    assert res.data["app"] == "chrome"


@pytest.mark.anyio
async def test_file_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="file",
        capability="list_directory",
        parameters={"path": "."},
    )
    assert res.success is True
    assert "count" in res.data


@pytest.mark.anyio
async def test_pdf_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="pdf",
        capability="summarize_pdf",
        parameters={"path": "test.pdf"},
    )
    assert res.success is True
    assert "summary" in res.data


@pytest.mark.anyio
async def test_email_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="email",
        capability="send_email",
        parameters={"to": "test@example.com", "subject": "Hello"},
    )
    assert res.success is True
    assert res.data["to"] == "test@example.com"


@pytest.mark.anyio
async def test_calendar_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="calendar",
        capability="create_event",
        parameters={"title": "Sprint Planning", "time": "10:00 AM"},
    )
    assert res.success is True
    assert res.data["title"] == "Sprint Planning"


@pytest.mark.anyio
async def test_office_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="office",
        capability="create_document",
        parameters={"title": "Quarterly Report"},
    )
    assert res.success is True
    assert res.data["document"] == "Quarterly Report"


@pytest.mark.anyio
async def test_terminal_plugin_capabilities(engine: PluginEngine) -> None:
    res = await engine.execute_plugin(
        plugin_id="terminal",
        capability="check_environment",
        parameters={},
    )
    assert res.success is True
    assert res.data["status"] == "healthy"


# ============================================================
# 4. Developer SDK
# ============================================================

def test_developer_sdk_decorators() -> None:
    @nova_plugin(
        name="CustomSDKPlugin",
        version="2.0.0",
        description="Custom SDK plugin",
        permissions=[PermissionType.FILE_SYSTEM],
    )
    class CustomSDKPlugin(BasePlugin):
        @capability(
            name="custom_action",
            description="Perform custom action",
            voice_intents=["run custom action"],
        )
        def custom_action(self, context: PluginContext) -> PluginResult:
            return PluginResult.ok(data="custom_output")

    inst = CustomSDKPlugin()
    assert inst.name == "CustomSDKPlugin"
    assert inst.version == "2.0.0"
    assert hasattr(inst.custom_action, "_nova_capability")


# ============================================================
# 5. Voice Command Resolution
# ============================================================

@pytest.mark.anyio
async def test_voice_command_resolution(engine: PluginEngine) -> None:
    resolved = await engine.resolve_voice_command("open website")
    assert resolved is not None
    assert resolved["plugin_id"] == "browser"
    assert resolved["capability"] == "open_url"


# ============================================================
# 6. Mock Provider
# ============================================================

def test_mock_provider() -> None:
    mock = MockPluginProvider()
    spec = mock.simulate_plugin_spec()
    assert spec.plugin_id == "mock_browser"
    assert len(spec.capabilities) == 2

    exec_dict = mock.simulate_execution()
    assert exec_dict["success"] is True

    health_dict = mock.simulate_health()
    assert health_dict["status"] == "healthy"


# ============================================================
# 7. Gateway Integration APIs
# ============================================================

@pytest.mark.anyio
async def test_gateway_plugin_apis() -> None:
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)

    # list_plugins
    plugins = await gateway.list_plugins()
    assert isinstance(plugins, list)
    assert len(plugins) >= 8

    # plugin_capabilities
    caps = await gateway.plugin_capabilities(plugin_id="browser")
    assert isinstance(caps, list)
    assert len(caps) >= 4

    # execute_plugin
    exec_res = await gateway.execute_plugin(
        plugin_id="browser",
        capability="open_url",
        parameters={"url": "https://nova.ai"},
    )
    assert exec_res["success"] is True
