"""Execution Manager orchestrating capability calls with permissions, sandbox, and learning integration."""

from typing import Any, Dict, Optional
import structlog

from app.ai.plugins.capability_registry import CapabilityRegistry
from app.ai.plugins.exceptions import PluginExecutionError, PluginNotFoundError
from app.ai.plugins.models import ExecutionRequest, ExecutionResult, PluginStatus
from app.ai.plugins.permission_manager import PermissionManager
from app.ai.plugins.plugin_registry import PluginRegistry
from app.ai.plugins.sandbox import PluginSandbox
from app.ai.plugins.sdk.context import PluginContext
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("execution_manager")


class ExecutionManager:
    """Orchestrates plugin execution: permission check -> sandbox execution -> learning engine update."""

    def __init__(
        self,
        registry: Optional[PluginRegistry] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        permission_manager: Optional[PermissionManager] = None,
        sandbox: Optional[PluginSandbox] = None,
    ) -> None:
        self.registry = registry or PluginRegistry()
        self.capabilities = capability_registry or CapabilityRegistry()
        self.permissions = permission_manager or PermissionManager()
        self.sandbox = sandbox or PluginSandbox()

    async def execute_capability(
        self,
        plugin_id: str,
        capability_name: str,
        parameters: Dict[str, Any],
        agent_id: str = "system",
        mission_id: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ) -> ExecutionResult:
        """Execute a capability safely."""
        spec = self.registry.get_plugin(plugin_id)
        if not spec:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' not found.")

        if spec.status != PluginStatus.ENABLED:
            raise PluginExecutionError(f"Plugin '{plugin_id}' is not in ENABLED state (current: {spec.status.value}).")

        found = self.capabilities.find_capability(capability_name, plugin_id=plugin_id)
        if not found:
            raise PluginNotFoundError(f"Capability '{capability_name}' not found on plugin '{plugin_id}'.")

        _, cap_obj = found

        # 1. Permission verification (triggers human approval if dangerous)
        await self.permissions.verify_permissions(
            plugin_id=plugin_id,
            required_permissions=cap_obj.required_permissions,
            mission_id=mission_id,
        )

        instance = self.registry.get_instance(plugin_id)
        if not instance:
            raise PluginExecutionError(f"Plugin instance '{plugin_id}' is not loaded.")

        # 2. Build context and execution request
        context = PluginContext(
            agent_id=agent_id,
            mission_id=mission_id,
            parameters=parameters,
        )
        request = ExecutionRequest(
            plugin_id=plugin_id,
            capability=capability_name,
            parameters=parameters,
            agent_id=agent_id,
            mission_id=mission_id,
            timeout_seconds=timeout_seconds,
        )

        # 3. Sandbox execution
        async def _run():
            return await instance.execute_capability(capability_name, context)

        exec_res = await self.sandbox.execute(request, _run)

        # Extract data from inner PluginResult if returned
        if exec_res.success and hasattr(exec_res.data, "success"):
            inner = exec_res.data
            exec_res.success = inner.success
            exec_res.data = inner.data
            exec_res.error = inner.error

        # 4. Continuous Learning Integration (feed result to Learning Engine if mission_id present)
        if mission_id:
            await self._feed_learning(mission_id, plugin_id, capability_name, exec_res)

        return exec_res

    async def _feed_learning(
        self,
        mission_id: str,
        plugin_id: str,
        capability: str,
        res: ExecutionResult,
    ) -> None:
        """Inform Learning Engine of plugin capability execution outcome."""
        try:
            gateway = resolve(IAIGateway)
            await gateway.learn_from_mission(
                mission_id=mission_id,
                mission_result={
                    "goal": f"Execute plugin capability {plugin_id}.{capability}",
                    "status": "success" if res.success else "failed",
                    "duration_seconds": res.execution_time_seconds,
                    "agents_used": [res.plugin_id],
                },
            )
        except Exception:
            pass
