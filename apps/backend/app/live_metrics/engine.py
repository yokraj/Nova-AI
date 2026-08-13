"""Live Metrics Engine Orchestrator Module.

Unites SystemMonitoringEngine, SnapshotManager, ChangeDetector, MetricsBuffer,
MetricsRateLimiter, MetricsPublisher, MetricsScheduler, and MetricsStatistics
into a high-performance continuous real-time telemetry engine.
"""

import asyncio
import time
from typing import Any, Dict, Optional
import structlog

from app.live_metrics.buffer import MetricsBuffer
from app.live_metrics.change_detector import ChangeDetector
from app.live_metrics.config import LiveMetricsConfig
from app.live_metrics.exceptions import (
    CollectorFailure,
    LiveMetricsError,
    MetricsCollectionError,
    PublishError,
)
from app.live_metrics.publisher import MetricsPublisher
from app.live_metrics.rate_limiter import MetricsRateLimiter
from app.live_metrics.scheduler import MetricsScheduler
from app.live_metrics.snapshot import SnapshotManager
from app.live_metrics.statistics import MetricsStatistics
from app.monitoring.cpu import CPUMonitor
from app.monitoring.disk import DiskMonitor
from app.monitoring.gpu import GPUMonitor
from app.monitoring.memory import MemoryMonitor
from app.monitoring.network import NetworkMonitor
from app.monitoring.processes import ProcessMonitor
from app.monitoring.system import SystemMonitor
from app.websocket.broadcaster import DashboardBroadcaster
from app.websocket.manager import ConnectionManager

logger = structlog.get_logger(__name__)


class LiveMetricsEngine:
    """Enterprise Master Orchestrator for Real-Time Telemetry Streaming."""

    def __init__(
        self,
        config: Optional[LiveMetricsConfig] = None,
        monitoring_engine: Optional[Any] = None,
        connection_manager: Optional[ConnectionManager] = None,
        broadcaster: Optional[DashboardBroadcaster] = None,
    ) -> None:
        self.config = config or LiveMetricsConfig()
        self.monitoring_engine = monitoring_engine
        self.connection_manager = connection_manager or ConnectionManager()
        self.broadcaster = broadcaster or DashboardBroadcaster(manager=self.connection_manager)

        # Standalone hardware sensors if monitoring_engine is not passed
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.network_monitor = NetworkMonitor()
        self.gpu_monitor = GPUMonitor()
        self.process_monitor = ProcessMonitor()
        self.system_monitor = SystemMonitor()

        self.snapshot_manager = SnapshotManager(max_retention=self.config.snapshot_retention)
        self.change_detector = ChangeDetector(threshold=self.config.change_threshold)
        self.buffer = MetricsBuffer(capacity=self.config.buffer_size)
        self.rate_limiter = MetricsRateLimiter(max_rate_per_sec=self.config.publish_rate)
        self.publisher = MetricsPublisher(broadcaster=self.broadcaster)
        self.statistics = MetricsStatistics()

        self.scheduler = MetricsScheduler(
            collection_callback=self._scheduler_tick,
            cleanup_callback=self._cleanup_tick,
            collection_interval=self.config.metrics_interval,
        )

        self._running = False

        logger.info("live_metrics_engine_initialized", config=self.config.model_dump())

    def start(self) -> None:
        """Starts the Live Metrics Engine and background scheduler loops."""
        if not self._running:
            self._running = True
            self.scheduler.start()
            logger.info("live_metrics_engine_started")

    def stop(self) -> None:
        """Stops the Live Metrics Engine and cancels background tasks."""
        if self._running:
            self._running = False
            self.scheduler.stop()
            logger.info("live_metrics_engine_stopped")

    def pause(self) -> None:
        """Pauses metric collection execution."""
        self.scheduler.pause()
        logger.info("live_metrics_engine_paused")

    def resume(self) -> None:
        """Resumes metric collection execution."""
        self.scheduler.resume()
        logger.info("live_metrics_engine_resumed")

    async def collect_metrics(self) -> Dict[str, Any]:
        """Collects real hardware metrics across all collectors safely."""
        start_time = time.time()
        metrics: Dict[str, Any] = {}

        try:
            cpu_usage = await asyncio.to_thread(self.cpu_monitor.get_cpu_usage)
            mem_info = await asyncio.to_thread(self.memory_monitor.get_virtual_memory)
            disk_info = await asyncio.to_thread(self.disk_monitor.get_disk_usage)
            net_info = await asyncio.to_thread(self.network_monitor.get_network_io)
            gpu_info = await asyncio.to_thread(self.gpu_monitor.get_gpu_devices)
            proc_info = await asyncio.to_thread(self.process_monitor.get_top_cpu_processes, 10)
            sys_info = await asyncio.to_thread(self.system_monitor.get_system_information)

            metrics = {
                "resources": {
                    "cpu": {"usage_percent": cpu_usage},
                    "memory": mem_info,
                    "disk": disk_info,
                    "network": net_info,
                    "gpu": gpu_info,
                },
                "system": sys_info,
                "health": {
                    "status": "healthy" if cpu_usage < 80 and mem_info.get("percent", 0) < 85 else "degraded",
                    "health_score": round(max(0.0, min(1.0, 1.0 - (cpu_usage / 200.0))), 2),
                },
                "processes": proc_info,
                "timestamp": datetime_now_iso(),
            }
        except Exception as exc:
            logger.error("metrics_collection_partial_failure", error=str(exc))
            metrics = {"error": str(exc), "timestamp": time.time()}

        duration_ms = (time.time() - start_time) * 1000.0
        self.statistics.record_collection(duration_ms)

        # Store in SnapshotManager ring buffer
        self.snapshot_manager.capture_snapshot(metrics)
        return metrics

    async def _publish_channel_safe(self, channel: str, publish_coro, payload: Dict[str, Any], current_val: Any, prev_val: Any) -> None:
        """Publishes channel payload if changed and within rate limits."""
        # 1. Change detection
        if not self.change_detector.has_changed(current_val if isinstance(current_val, dict) else {"val": current_val}, prev_val if isinstance(prev_val, dict) else {"val": prev_val} if prev_val is not None else None):
            self.statistics.record_skipped(channel)
            return

        # 2. Rate limiting
        if not self.rate_limiter.allow_publish(channel):
            self.statistics.record_skipped(channel)
            logger.debug("publish_skipped_rate_limited", channel=channel)
            return

        # 3. Publish over WebSocket
        start_time = time.time()
        try:
            await publish_coro(payload)
            self.rate_limiter.record_publish(channel)
            duration_ms = (time.time() - start_time) * 1000.0
            self.statistics.record_broadcast(channel, duration_ms)
        except Exception as exc:
            logger.warning("channel_publish_failed", channel=channel, error=str(exc))

    async def publish_metrics(self, metrics: Dict[str, Any]) -> None:
        """Evaluates deltas and publishes changed telemetry across all topic channels."""
        prev_snapshot = self.snapshot_manager.get_previous_snapshot()
        prev_data = prev_snapshot.get("data", {}) if prev_snapshot else {}

        # 1. Resources (CPU, RAM, Disk, Network, GPU)
        res_curr = metrics.get("resources", {})
        res_prev = prev_data.get("resources", {})
        if res_curr:
            await self._publish_channel_safe("resources", self.publisher.publish_resources, res_curr, res_curr, res_prev)

            # CPU
            if "cpu" in res_curr:
                await self._publish_channel_safe("cpu", self.publisher.publish_cpu, res_curr["cpu"], res_curr["cpu"], res_prev.get("cpu"))

            # Memory
            if "memory" in res_curr:
                await self._publish_channel_safe("memory", self.publisher.publish_memory, res_curr["memory"], res_curr["memory"], res_prev.get("memory"))

            # Disk
            if "disk" in res_curr:
                await self._publish_channel_safe("disk", self.publisher.publish_disk, res_curr["disk"], res_curr["disk"], res_prev.get("disk"))

            # Network
            if "network" in res_curr:
                await self._publish_channel_safe("network", self.publisher.publish_network, res_curr["network"], res_curr["network"], res_prev.get("network"))

            # GPU
            if "gpu" in res_curr:
                await self._publish_channel_safe("gpu", self.publisher.publish_gpu, {"gpu": res_curr["gpu"]}, res_curr["gpu"], res_prev.get("gpu"))

        # 2. System
        sys_curr = metrics.get("system", {})
        sys_prev = prev_data.get("system", {})
        if sys_curr:
            await self._publish_channel_safe("system", self.publisher.publish_system, sys_curr, sys_curr, sys_prev)

        # 3. Health
        health_curr = metrics.get("health", {})
        health_prev = prev_data.get("health", {})
        if health_curr:
            await self._publish_channel_safe("health", self.publisher.publish_health, health_curr, health_curr, health_prev)

        # 4. Processes
        proc_curr = metrics.get("processes", {})
        proc_prev = prev_data.get("processes", {})
        if proc_curr:
            await self._publish_channel_safe("processes", self.publisher.publish_processes, {"processes": proc_curr}, proc_curr, proc_prev)

    async def publish_dashboard(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_dashboard(payload)

    async def publish_resources(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_resources(payload)

    async def publish_health(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_health(payload)

    async def publish_notifications(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_notifications(payload)

    async def publish_events(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_events(payload)

    async def publish_agents(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_agents(payload)

    async def publish_missions(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_missions(payload)

    async def publish_analytics(self, payload: Dict[str, Any]) -> None:
        await self.publisher.publish_analytics(payload)

    async def _scheduler_tick(self) -> None:
        """Internal callback invoked periodically by MetricsScheduler."""
        metrics = await self.collect_metrics()
        await self.publish_metrics(metrics)

    async def _cleanup_tick(self) -> None:
        """Internal cleanup callback invoked periodically by MetricsScheduler."""
        self.snapshot_manager.cleanup_old_snapshots()


def datetime_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
