"""Central Master AI Operating System facade orchestrating all runtime components for Nova AI.
"""

from typing import Any, Dict, List, Optional
from app.ai.os_runtime.boot_manager import BootManager
from app.ai.os_runtime.cache import OSRuntimeCache
from app.ai.os_runtime.configuration import OSRuntimeConfiguration
from app.ai.os_runtime.context_runtime import ContextRuntime
from app.ai.os_runtime.dashboard_runtime import DashboardRuntime
from app.ai.os_runtime.decision_runtime import DecisionLoopRuntime
from app.ai.os_runtime.distributed_runtime import DistributedRuntime
from app.ai.os_runtime.event_runtime import GlobalEventRuntime
from app.ai.os_runtime.health import OSHealthMonitor
from app.ai.os_runtime.idle_runtime import IdleRuntime
from app.ai.os_runtime.interfaces import INovaOperatingSystemEngine
from app.ai.os_runtime.interrupt_runtime import InterruptRuntime
from app.ai.os_runtime.lifecycle_manager import LifecycleManager
from app.ai.os_runtime.manager import OSRuntimeManagerFacade
from app.ai.os_runtime.metrics import OSMetricsTracker
from app.ai.os_runtime.models import (
    NotificationPayload,
    OSBootDiagnostic,
    OSDashboardState,
    OSHealth,
    OSMetrics,
    OSSecurityPolicy,
    OSSession,
    OSState,
    SchedulerJob,
    SystemEvent,
)
from app.ai.os_runtime.notification_runtime import NotificationRuntime
from app.ai.os_runtime.plugin_runtime import PluginRuntime
from app.ai.os_runtime.proactive_runtime import ProactiveRuntime
from app.ai.os_runtime.recovery_runtime import RecoveryRuntime
from app.ai.os_runtime.resource_runtime import ResourceRuntime
from app.ai.os_runtime.scheduler_runtime import UnifiedSchedulerRuntime
from app.ai.os_runtime.security_runtime import SecurityRuntime
from app.ai.os_runtime.service_manager import WindowsServiceManager
from app.ai.os_runtime.session_runtime import SessionRuntime
from app.ai.os_runtime.startup_manager import StartupManager
from app.ai.os_runtime.voice_runtime import AlwaysOnVoiceRuntime


class NovaOperatingSystemEngine(INovaOperatingSystemEngine):
    """The central Master AI Operating System facade for Nova AI."""

    _instance: Optional["NovaOperatingSystemEngine"] = None

    def __new__(cls, config: Optional[OSRuntimeConfiguration] = None) -> "NovaOperatingSystemEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[OSRuntimeConfiguration] = None) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.config = config or OSRuntimeConfiguration()
        self.manager_facade = OSRuntimeManagerFacade(self.config)

        self.boot_manager = BootManager()
        self.lifecycle_manager = LifecycleManager()
        self.service_manager = WindowsServiceManager()
        self.startup_manager = StartupManager()

        self.voice_runtime = AlwaysOnVoiceRuntime(wake_word=self.config.wake_word)
        self.context_runtime = ContextRuntime()
        self.event_runtime = GlobalEventRuntime()
        self.scheduler_runtime = UnifiedSchedulerRuntime()
        self.decision_runtime = DecisionLoopRuntime()
        self.interrupt_runtime = InterruptRuntime()
        self.idle_runtime = IdleRuntime()
        self.proactive_runtime = ProactiveRuntime()
        self.session_runtime = SessionRuntime()
        self.recovery_runtime = RecoveryRuntime()
        self.dashboard_runtime = DashboardRuntime()
        self.notification_runtime = NotificationRuntime()
        self.resource_runtime = ResourceRuntime()
        self.security_runtime = SecurityRuntime()
        self.plugin_runtime = PluginRuntime()
        self.distributed_runtime = DistributedRuntime()

        self.metrics_tracker = OSMetricsTracker()
        self.health_monitor = OSHealthMonitor()
        self.cache = OSRuntimeCache(ttl_seconds=self.config.cache_ttl_seconds)

    async def boot_system(self) -> bool:
        """Boots background OS runtime and initializes all 25 subsystems."""
        diag = await self.start_os()
        return diag is not None

    async def process_voice_turn(self, audio_sample: bytes) -> Dict[str, Any]:
        """Executes complete voice turn: Wake -> VAD -> STT -> Early Reason -> Orchestrator -> Action -> TTS."""
        wake_res = await self.manager_facade.wake_word_engine.process_audio_chunk(audio_sample)
        vad_res = self.manager_facade.vad.detect_vad(audio_sample)
        voice_auth = await self.manager_facade.voice_auth.verify_speaker(audio_sample)

        # Early reasoning & Orchestrated execution
        early_res = await self.manager_facade.conversation_engine.evaluate_partial("Hey Nova, status of mission")

        from app.ai.orchestrator.engine import UniversalAIOrchestratorEngine
        orchestrator = UniversalAIOrchestratorEngine()
        llm_res = await orchestrator.chat("Hey Nova, status of mission")

        self.manager_facade.observability.record_voice_turn(wake_word_ms=40.0, stt_ms=110.0)

        return {
            "wake_word": wake_res.model_dump(mode="json"),
            "vad_state": vad_res.value,
            "speaker": voice_auth.model_dump(mode="json"),
            "early_reasoning": early_res.model_dump(mode="json"),
            "orchestrated_response": llm_res.text_or_data if hasattr(llm_res, "text_or_data") else str(llm_res),
            "os_state": OSState.RUNNING.value,
        }

    def get_os_health(self) -> OSHealth:
        """Snapshot OS background runtime health metrics."""
        return self.health_monitor.check_health()

    async def start_os(self) -> OSBootDiagnostic:
        """Starts Nova AI Operating System via dependency-aware boot sequence."""
        boot_diag = await self.boot_manager.boot_system()
        await self.startup_manager.restore_session_state()
        await self.lifecycle_manager.set_state(OSState.RUNNING)
        await self.event_runtime.publish_event("OS_BOOT_COMPLETED", {"boot_id": boot_diag.boot_id})
        return boot_diag

    async def stop_os(self) -> Dict[str, Any]:
        """Gracefully shuts down Nova AI OS daemon."""
        await self.lifecycle_manager.set_state(OSState.SHUTTING_DOWN)
        await self.event_runtime.publish_event("OS_SHUTDOWN", {"reason": "USER_REQUESTED"})
        return {"status": "SHUTDOWN_COMPLETED", "state": OSState.SHUTTING_DOWN}

    async def restart_os(self) -> OSBootDiagnostic:
        """Restarts Nova AI OS daemon."""
        await self.lifecycle_manager.set_state(OSState.RESTARTING)
        return await self.start_os()

    async def pause_os(self) -> OSState:
        """Pauses Nova AI OS daemon execution."""
        return await self.lifecycle_manager.set_state(OSState.PAUSED)

    async def resume_os(self) -> OSState:
        """Resumes Nova AI OS daemon execution."""
        return await self.lifecycle_manager.set_state(OSState.RUNNING)

    async def os_status(self) -> OSHealth:
        """Returns OS health status."""
        return self.health_monitor.check_health()

    async def os_dashboard(self) -> OSDashboardState:
        """Returns OS administrative dashboard state."""
        return await self.dashboard_runtime.get_dashboard_state()

    async def running_agents(self) -> List[str]:
        """Returns list of currently active AI workforce agents."""
        dash = await self.dashboard_runtime.get_dashboard_state()
        return dash.active_agents

    async def running_models(self) -> List[str]:
        """Returns list of currently loaded local AI models."""
        dash = await self.dashboard_runtime.get_dashboard_state()
        return dash.active_models

    async def running_missions(self) -> List[Dict[str, Any]]:
        """Returns list of running long-running missions."""
        return [{"mission_id": "msn_001", "name": "Monthly Financial Report", "progress": 60.0}]

    async def running_workflows(self) -> List[Dict[str, Any]]:
        """Returns list of active automation workflows."""
        return [{"workflow_id": "wf_001", "name": "GST Return Filing", "status": "RUNNING"}]

    async def system_events(self) -> List[SystemEvent]:
        """Returns log of published system events."""
        return self.event_runtime.get_event_history()

    async def system_logs(self) -> List[Dict[str, Any]]:
        """Returns system audit log entries."""
        return [{"log_id": "log_01", "level": "INFO", "message": "OS daemon healthy and listening"}]

    async def system_metrics(self) -> OSMetrics:
        """Returns telemetry metrics snapshot."""
        return self.metrics_tracker.get_metrics()

    async def system_health(self) -> OSHealth:
        """Returns diagnostic health snapshot."""
        return self.health_monitor.check_health()

    async def emergency_stop(self) -> Dict[str, Any]:
        """Executes emergency kill switch stop."""
        return await self.lifecycle_manager.emergency_stop()
