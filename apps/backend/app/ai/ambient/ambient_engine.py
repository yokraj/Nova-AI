"""Ambient Engine central facade orchestrating continuous listening, wake words, desktop context, and privacy."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.ambient.ambient_manager import AmbientManager
from app.ai.ambient.cache import AmbientCache
from app.ai.ambient.configuration import AmbientConfiguration
from app.ai.ambient.health import AmbientHealthMonitor
from app.ai.ambient.interfaces import IAmbientEngine
from app.ai.ambient.metrics import AmbientMetricsTracker
from app.ai.ambient.models import AmbientHealth, AmbientMetrics, AmbientState

logger = structlog.get_logger("ambient_engine")


class AmbientEngine(IAmbientEngine):
    """Central facade runtime orchestrating Nova's Ambient Intelligence & Continuous Voice Assistant."""

    def __init__(self, config: Optional[AmbientConfiguration] = None) -> None:
        self.config = config or AmbientConfiguration()
        self.manager = AmbientManager()
        self.metrics = AmbientMetricsTracker()
        self.health_monitor = AmbientHealthMonitor()
        self.cache = AmbientCache()
        self.state = AmbientState.IDLE
        self._listening = False

    async def start(self) -> None:
        """Start Ambient Intelligence Engine and continuous listening."""
        if self.config.privacy_mode:
            self.state = AmbientState.PRIVACY_MODE
            logger.info("Ambient Engine start requested while in Privacy Mode")
            return
        self._listening = True
        self.state = AmbientState.LISTENING
        await self.manager.mic.start_listening()
        logger.info("Ambient Engine started continuous listening")

    async def stop(self) -> None:
        """Stop Ambient Intelligence Engine."""
        self._listening = False
        self.state = AmbientState.IDLE
        await self.manager.mic.stop_listening()
        logger.info("Ambient Engine stopped")

    async def pause_listening(self) -> None:
        """Pause continuous microphone listening."""
        self.state = AmbientState.PAUSED
        await self.manager.mic.pause_listening()
        self.metrics.record_privacy_toggle()
        logger.info("Ambient Engine listening paused")

    async def resume_listening(self) -> None:
        """Resume continuous microphone listening."""
        if not self.config.privacy_mode:
            self.state = AmbientState.LISTENING
            await self.manager.mic.resume_listening()
            self.metrics.record_privacy_toggle()
            logger.info("Ambient Engine listening resumed")

    async def process_conversation(self, query: str) -> Dict[str, Any]:
        """Process voice turn and return conversation response."""
        self.metrics.record_conversation()
        self.state = AmbientState.CONVERSING
        res = await self.manager.conversation.handle_user_speech(query)
        self.state = AmbientState.LISTENING
        return res

    async def get_proactive_alerts(self) -> List[Dict[str, Any]]:
        """Evaluate current desktop context and return proactive ambient alerts."""
        sug_list = await self.manager.get_proactive_suggestions()
        for s in sug_list:
            self.metrics.record_suggestion()
            if s.auto_create_mission:
                self.metrics.record_mission()
        return [s.model_dump(mode="json") for s in sug_list]

    async def get_metrics(self) -> AmbientMetrics:
        """Retrieve telemetry metrics."""
        return self.metrics.get_metrics()

    def check_health(self) -> AmbientHealth:
        """Retrieve composite health status."""
        return self.health_monitor.check_health()
