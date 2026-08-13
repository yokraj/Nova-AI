"""Base class for all Nova AI autonomous agents.
"""

import time
from datetime import datetime
import structlog
from typing import Any, Dict, Optional

from app.ai.agents.state_machine import AgentStateMachine, AgentStateValue
from app.ai.agents.models import AgentMetadata, AgentState, AgentStatus, AgentInfo
from app.ai.agents.base.lifecycle_hooks import LifecycleHooks
from app.ai.agents.base.agent_session import AgentSession
from app.ai.agents.base.agent_result import AgentResult
from app.ai.agents.exceptions import AgentStateError

logger = structlog.get_logger("base_agent")

class BaseAgent:
    """Abstract agent controller standardizing states, hooks, and execution policies."""

    def __init__(self, metadata: AgentMetadata, config: Optional[Any] = None) -> None:
        self.metadata = metadata
        self.config = config
        self.state_machine = AgentStateMachine()
        self.hooks = LifecycleHooks()
        self.session = AgentSession(self.metadata.id)

        self.total_executions = 0
        self.failed_executions = 0
        self.errors_count = 0
        self._start_time = time.time()

    @property
    def id(self) -> str:
        """Returns unique agent ID."""
        return self.metadata.id

    @property
    def name(self) -> str:
        """Returns agent name."""
        return self.metadata.name

    @property
    def state(self) -> str:
        """Returns current StateMachine value."""
        return self.state_machine.current_state

    def get_info(self) -> AgentInfo:
        """Compiles a complete runtime metrics report."""
        uptime = time.time() - self._start_time
        return AgentInfo(
            metadata=self.metadata,
            state=AgentState(
                value=self.state,
                progress=0.0,
                last_updated=datetime.utcnow()
            ),
            status=AgentStatus(
                health="HEALTHY" if self.errors_count == 0 else "DEGRADED",
                uptime_seconds=uptime,
                active_tasks_count=1 if self.state == AgentStateValue.BUSY else 0,
                errors_count=self.errors_count
            )
        )

    async def initialize(self) -> None:
        """Bootstraps agent resources, transitioning state to INITIALIZING."""
        await self.hooks.trigger("before_initialize")
        self.state_machine.transition_to(AgentStateValue.INITIALIZING)
        await self._on_initialize()
        await self.hooks.trigger("after_initialize")

    async def _on_initialize(self) -> None:
        """Hook for subclass resource setups."""
        pass

    async def configure(self, config: Any) -> None:
        """Overwrites local properties dynamically."""
        self.config = config
        await self._on_configure(config)

    async def _on_configure(self, config: Any) -> None:
        """Hook for subclass configuration updates."""
        pass

    async def start(self) -> None:
        """Activates agent state, transitioning to STARTING and then READY."""
        await self.hooks.trigger("before_start")
        self.state_machine.transition_to(AgentStateValue.STARTING)
        await self._on_start()
        self.state_machine.transition_to(AgentStateValue.READY)
        await self.hooks.trigger("after_start")

    async def _on_start(self) -> None:
        """Hook for subclass activation logic."""
        pass

    async def stop(self) -> None:
        """Gracefully suspends task processing, transitioning to STOPPED."""
        await self.hooks.trigger("before_stop")
        self.state_machine.transition_to(AgentStateValue.STOPPING)
        await self._on_stop()
        self.state_machine.transition_to(AgentStateValue.STOPPED)
        await self.hooks.trigger("after_stop")

    async def _on_stop(self) -> None:
        """Hook for subclass teardown tasks."""
        pass

    async def shutdown(self) -> None:
        """Releases locks and resources completely."""
        if self.state not in (AgentStateValue.STOPPED, AgentStateValue.CREATED):
            try:
                await self.stop()
            except Exception as err:
                logger.warning("Error stopping agent during shutdown", agent_id=self.id, error=str(err))
        await self._on_shutdown()

    async def _on_shutdown(self) -> None:
        """Hook for final subclass cleanup."""
        pass

    async def restart(self) -> None:
        """Restarts the lifecycle transitions sequence."""
        await self.stop()
        self.state_machine.transition_to(AgentStateValue.CREATED)
        await self.initialize()
        await self.start()

    async def suspend(self) -> None:
        """Pauses executions availability."""
        self.state_machine.transition_to(AgentStateValue.PAUSED)
        await self._on_suspend()

    async def _on_suspend(self) -> None:
        """Hook for pausing tasks."""
        pass

    async def resume(self) -> None:
        """Re-enables ready state access."""
        self.state_machine.transition_to(AgentStateValue.READY)
        await self._on_resume()

    async def _on_resume(self) -> None:
        """Hook for resuming tasks."""
        pass

    async def execute(self, task: Any, **kwargs: Any) -> AgentResult:
        """Standard task wrapper tracking execution durations and lifecycle states."""
        if self.state not in (AgentStateValue.READY, AgentStateValue.IDLE):
            raise AgentStateError(f"Agent '{self.name}' cannot process executions in '{self.state}' state.")

        self.state_machine.transition_to(AgentStateValue.BUSY)
        await self.hooks.trigger("before_execute")

        start_time = time.perf_counter()
        exec_id = kwargs.get("execution_id", "default_exec")

        try:
            res_data = await self._on_execute(task, **kwargs)
            self.total_executions += 1
            self.state_machine.transition_to(AgentStateValue.READY)
            duration = (time.perf_counter() - start_time) * 1000.0

            result = AgentResult(
                execution_id=exec_id,
                status="success",
                data=res_data,
                duration_ms=duration
            )
        except Exception as err:
            self.failed_executions += 1
            self.errors_count += 1
            self.state_machine.transition_to(AgentStateValue.FAILED)
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("Agent execution cycle failed", agent_id=self.id, error=str(err))

            result = AgentResult(
                execution_id=exec_id,
                status="failed",
                error_message=str(err),
                duration_ms=duration
            )

        await self.hooks.trigger("after_execute", result)
        return result

    async def _on_execute(self, task: Any, **kwargs: Any) -> Dict[str, Any]:
        """Custom logic block executed by concrete subclass implementations."""
        raise NotImplementedError("Subclasses must implement execution handler logic.")
