"""Terminal Plugin providing command execution and environment diagnostics."""

from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="Terminal",
    version="1.0.0",
    description="Local command execution and terminal control plugin.",
    permissions=[PermissionType.TERMINAL],
)
class TerminalPlugin(BasePlugin):
    """Reference implementation of Terminal Plugin."""

    @capability(
        name="execute_command",
        description="Execute a terminal shell command",
        voice_intents=["run command", "execute terminal", "run shell command"],
        risk_level=RiskLevel.CRITICAL,
    )
    async def execute_command(self, context: PluginContext) -> PluginResult:
        command = context.parameters.get("command", "echo Hello Nova")
        return PluginResult.ok(data={"command": command, "stdout": "Hello Nova\n", "exit_code": 0})

    @capability(
        name="check_environment",
        description="Check environment variables and system paths",
        voice_intents=["check environment", "system paths"],
        risk_level=RiskLevel.LOW,
    )
    async def check_environment(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"status": "healthy", "python_version": "3.14"})
