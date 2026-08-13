"""Mock Plugin Provider — deterministic offline simulations for testing and development."""

from typing import Any, Dict, List
from app.ai.plugins.models import PluginCapability, PluginMetadata, PluginSpec, PluginStatus


class MockPluginProvider:
    """Provides deterministic, offline simulations of plugin operations."""

    def simulate_plugin_spec(self, plugin_id: str = "mock_browser") -> PluginSpec:
        """Return a pre-built mock plugin specification."""
        return PluginSpec(
            plugin_id=plugin_id,
            metadata=PluginMetadata(
                name="Mock Browser Plugin",
                version="1.0.0",
                description="Simulated browser automation plugin.",
            ),
            status=PluginStatus.ENABLED,
            capabilities=[
                PluginCapability(
                    name="open_url",
                    description="Open a web page",
                    voice_intents=["open website", "navigate to url"],
                ),
                PluginCapability(
                    name="take_screenshot",
                    description="Capture screen screenshot",
                    voice_intents=["take screenshot"],
                ),
            ],
        )

    def simulate_execution(
        self, plugin_id: str = "mock_browser", capability: str = "open_url"
    ) -> Dict[str, Any]:
        """Return a pre-built execution result dict."""
        return {
            "request_id": "req_mock_001",
            "plugin_id": plugin_id,
            "capability": capability,
            "success": True,
            "data": {"status": "navigated", "url": "https://nova.ai"},
            "execution_time_seconds": 0.05,
        }

    @staticmethod
    def simulate_health() -> Dict[str, Any]:
        """Return healthy composite health status."""
        return {
            "status": "healthy",
            "components": {
                "registry": "online",
                "capability_registry": "online",
                "sandbox": "online",
            },
            "total_plugins": 8,
            "active_capabilities": 28,
        }
