"""Manual validation script for M3.3.9 – Universal Plugin & Skill Integration Platform.

Run from apps/backend/:
    python test_plugin_manual.py

Expected output:
    =========================================
    Nova AI Plugin Platform Validation
    =========================================
    Stage 1  Plugin Discovery            PASS
    Stage 2  Plugin Registry             PASS
    Stage 3  Lifecycle Management        PASS
    Stage 4  Capability Indexing         PASS
    Stage 5  Permission Verification     PASS
    Stage 6  Sandbox Isolation           PASS
    Stage 7  Built-in Plugins            PASS
    Stage 8  Developer SDK               PASS
    Stage 9  Voice Skill Resolution      PASS
    Stage 10 Telemetry & Health          PASS
    Stage 11 Gateway Integration         PASS
    Stage 12 Complete                    PASS

    12/12 PASS

    Plugin Platform Healthy
"""

import asyncio
import sys


def _banner() -> None:
    print("=========================================")
    print("Nova AI Plugin Platform Validation")
    print("=========================================")


def _result(stage: int, label: str, passed: bool, error: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"Stage {stage:<2} {label:<30} {status}")
    if not passed and error:
        print(f"       Error: {error}")
    return passed


def stage_1_discovery() -> bool:
    try:
        from app.ai.plugins.configuration import PluginConfiguration
        from app.ai.plugins.plugin_discovery import PluginDiscovery

        config = PluginConfiguration(auto_discover=False)
        discovery = PluginDiscovery(config=config)
        discovered = discovery.discover_plugins()
        assert isinstance(discovered, list)
        return True
    except Exception as e:
        return _result(1, "Plugin Discovery", False, str(e)) or False


def stage_2_registry() -> bool:
    try:
        from app.ai.plugins.plugin_registry import PluginRegistry
        from app.ai.plugins.models import PluginSpec, PluginMetadata, PluginStatus

        registry = PluginRegistry()
        spec = PluginSpec(
            plugin_id="val_plugin",
            metadata=PluginMetadata(name="Validation Plugin", version="1.0.0"),
            status=PluginStatus.INSTALLED,
        )
        registry.add_plugin(spec)
        assert registry.count() == 1
        assert registry.get_plugin("val_plugin") is not None
        return True
    except Exception as e:
        return _result(2, "Plugin Registry", False, str(e)) or False


async def stage_3_lifecycle() -> bool:
    try:
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine()
        assert await engine.enable_plugin("browser") is True
        spec = engine.registry.get_plugin("browser")
        assert spec.status.value == "enabled"

        assert await engine.disable_plugin("browser") is True
        spec = engine.registry.get_plugin("browser")
        assert spec.status.value == "disabled"
        return True
    except Exception as e:
        return _result(3, "Lifecycle Management", False, str(e)) or False


def stage_4_capabilities() -> bool:
    try:
        from app.ai.plugins.capability_registry import CapabilityRegistry
        from app.ai.plugins.models import PluginCapability

        cap_reg = CapabilityRegistry()
        cap = PluginCapability(name="open_url", description="Open URL")
        cap_reg.register_capability("browser", cap)

        found = cap_reg.find_capability("open_url", plugin_id="browser")
        assert found is not None
        assert found[1].name == "open_url"
        return True
    except Exception as e:
        return _result(4, "Capability Indexing", False, str(e)) or False


async def stage_5_permissions() -> bool:
    try:
        from app.ai.plugins.permission_manager import PermissionManager
        from app.ai.plugins.models import PermissionType

        mgr = PermissionManager()
        # Non-dangerous permission auto grants
        verified = await mgr.verify_permissions("file", [PermissionType.FILE_SYSTEM])
        assert verified is True
        return True
    except Exception as e:
        return _result(5, "Permission Verification", False, str(e)) or False


async def stage_6_sandbox() -> bool:
    try:
        from app.ai.plugins.sandbox import PluginSandbox
        from app.ai.plugins.models import ExecutionRequest

        sandbox = PluginSandbox(timeout_seconds=2.0)
        request = ExecutionRequest(plugin_id="val", capability="fast_op")

        def _fast_op():
            return "fast_result"

        res = await sandbox.execute(request, _fast_op)
        assert res.success is True
        assert res.data == "fast_result"
        return True
    except Exception as e:
        return _result(6, "Sandbox Isolation", False, str(e)) or False


async def stage_7_builtins() -> bool:
    try:
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine()

        # Browser
        r1 = await engine.execute_plugin("browser", "open_url", {"url": "https://nova.ai"})
        assert r1.success is True

        # Desktop
        r2 = await engine.execute_plugin("desktop", "launch_app", {"app_name": "notepad"})
        assert r2.success is True

        # PDF
        r3 = await engine.execute_plugin("pdf", "summarize_pdf", {"path": "doc.pdf"})
        assert r3.success is True

        # Terminal
        r4 = await engine.execute_plugin("terminal", "check_environment", {})
        assert r4.success is True
        return True
    except Exception as e:
        return _result(7, "Built-in Plugins", False, str(e)) or False


def stage_8_sdk() -> bool:
    try:
        from app.ai.plugins.sdk import nova_plugin, capability, BasePlugin, PluginContext, PluginResult
        from app.ai.plugins.models import PermissionType

        @nova_plugin(
            name="SDKVal",
            version="1.0.0",
            permissions=[PermissionType.CLIPBOARD],
        )
        class SDKValPlugin(BasePlugin):
            @capability(name="copy", description="Copy to clipboard")
            def copy(self, ctx: PluginContext) -> PluginResult:
                return PluginResult.ok("copied")

        inst = SDKValPlugin()
        assert inst.name == "SDKVal"
        return True
    except Exception as e:
        return _result(8, "Developer SDK", False, str(e)) or False


async def stage_9_voice() -> bool:
    try:
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine()
        resolved = await engine.resolve_voice_command("open website")
        assert resolved is not None
        assert resolved["plugin_id"] == "browser"
        return True
    except Exception as e:
        return _result(9, "Voice Skill Resolution", False, str(e)) or False


async def stage_10_health() -> bool:
    try:
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine()

        metrics = await engine.get_metrics()
        assert metrics.total_installed >= 8

        health = engine.check_health()
        assert health.status == "healthy"
        return True
    except Exception as e:
        return _result(10, "Telemetry & Health", False, str(e)) or False


async def stage_11_gateway() -> bool:
    try:
        from app.core.dependency_container import resolve, register_ai_gateway_dependencies
        from app.ai.gateway import IAIGateway

        try:
            register_ai_gateway_dependencies()
        except Exception:
            pass

        gateway = resolve(IAIGateway)

        plugins = await gateway.list_plugins()
        assert len(plugins) >= 8

        caps = await gateway.plugin_capabilities("browser")
        assert len(caps) >= 4

        res = await gateway.execute_plugin("browser", "open_url", {"url": "https://nova.ai"})
        assert res["success"] is True
        return True
    except Exception as e:
        return _result(11, "Gateway Integration", False, str(e)) or False


async def stage_12_complete() -> bool:
    try:
        from app.ai.plugins.providers.mock_provider import MockPluginProvider
        mock = MockPluginProvider()

        spec = mock.simulate_plugin_spec()
        assert spec.plugin_id == "mock_browser"

        res = mock.simulate_execution()
        assert res["success"] is True

        health = mock.simulate_health()
        assert health["status"] == "healthy"
        return True
    except Exception as e:
        return _result(12, "Complete", False, str(e)) or False


async def main() -> None:
    _banner()

    results = []

    # Sync stages
    results.append(_result(1, "Plugin Discovery", stage_1_discovery()))
    results.append(_result(2, "Plugin Registry", stage_2_registry()))

    # Async stages
    results.append(_result(3, "Lifecycle Management", await stage_3_lifecycle()))
    results.append(_result(4, "Capability Indexing", stage_4_capabilities()))
    results.append(_result(5, "Permission Verification", await stage_5_permissions()))
    results.append(_result(6, "Sandbox Isolation", await stage_6_sandbox()))
    results.append(_result(7, "Built-in Plugins", await stage_7_builtins()))
    results.append(_result(8, "Developer SDK", stage_8_sdk()))
    results.append(_result(9, "Voice Skill Resolution", await stage_9_voice()))
    results.append(_result(10, "Telemetry & Health", await stage_10_health()))
    results.append(_result(11, "Gateway Integration", await stage_11_gateway()))
    results.append(_result(12, "Complete", await stage_12_complete()))

    passed = sum(results)
    total = len(results)

    print()
    print(f"{passed}/{total} PASS")
    print()

    if passed == total:
        print("Plugin Platform Healthy")
    else:
        print("Plugin Platform Degraded")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
