"""System Monitoring Engine Module.

Orchestrates real-time hardware telemetry collection across CPU, Memory, Storage,
GPU, Network, Process, and System OS monitors.
Converts collected host metrics into domain DTOs and persists them exclusively
through business services (SystemMonitorService, ResourceMonitorService, HealthService,
DashboardService, AnalyticsService).
"""

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import structlog

from app.dashboard.schemas import (
    DashboardSnapshotCreate,
    GPUMetricCreate,
    HealthRecordCreate,
    ProcessMetricCreate,
    ResourceMetricCreate,
    SystemMetricCreate,
)
from app.dashboard.services import (
    AnalyticsService,
    DashboardService,
    HealthService,
    ResourceMonitorService,
    SystemMonitorService,
)

from app.database.models.dashboard import (
    DashboardSnapshot,
    GPUMetric,
    HealthRecord,
    ProcessMetric,
    ResourceMetric,
    SystemMetric,
)
from app.database.models.enums import HealthStatus, ResourceType
from app.monitoring.cpu import CPUMonitor
from app.monitoring.disk import DiskMonitor
from app.monitoring.gpu import GPUMonitor
from app.monitoring.memory import MemoryMonitor
from app.monitoring.network import NetworkMonitor
from app.monitoring.processes import ProcessMonitor
from app.monitoring.system import SystemMonitor

logger = structlog.get_logger(__name__)


class SystemMonitoringEngine:
    """Enterprise System Monitoring Engine orchestrator."""

    def __init__(
        self,
        system_service: SystemMonitorService,
        resource_service: ResourceMonitorService,
        health_service: HealthService,
        dashboard_service: DashboardService,
        analytics_service: Optional[AnalyticsService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes system monitoring engine with injected business services."""
        self.system_service = system_service
        self.resource_service = resource_service
        self.health_service = health_service
        self.dashboard_service = dashboard_service
        self.analytics_service = analytics_service

        # Monitoring settings with fallbacks
        self.config = config or {}
        self.metrics_interval = self.config.get("metrics_interval", 15)
        self.retention_days = self.config.get("retention_days", 30)
        self.cache_ttl = self.config.get("cache_ttl", 300)
        self.heartbeat_interval = self.config.get("heartbeat_interval", 60)

        # Individual hardware collectors
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.network_monitor = NetworkMonitor()
        self.gpu_monitor = GPUMonitor()
        self.process_monitor = ProcessMonitor()
        self.system_monitor = SystemMonitor()

        logger.info(
            "system_monitoring_engine_initialized",
            metrics_interval=self.metrics_interval,
            retention_days=self.retention_days,
        )

    async def collect_system_metrics(self) -> Optional[SystemMetric]:
        """Collects real system OS and telemetry metrics and persists via SystemMonitorService."""
        start_time = time.perf_counter()
        logger.info("collection_started", collector="system_metrics")
        try:
            sys_info = await asyncio.to_thread(self.system_monitor.get_system_information)
            cpu_usage = await asyncio.to_thread(self.cpu_monitor.get_cpu_usage)
            mem_info = await asyncio.to_thread(self.memory_monitor.get_virtual_memory)
            disk_info = await asyncio.to_thread(self.disk_monitor.get_disk_usage)
            net_info = await asyncio.to_thread(self.network_monitor.get_network_io)

            dto = SystemMetricCreate(
                hostname=sys_info.get("hostname", "localhost"),
                os_name=sys_info.get("os_name", "Unknown"),
                cpu_usage=cpu_usage,
                memory_total=mem_info.get("total", 0),
                memory_used=mem_info.get("used", 0),
                memory_available=mem_info.get("available", 0),
                swap_used=self.memory_monitor.get_swap_usage().get("used", 0),
                disk_total=disk_info.get("total", 0),
                disk_used=disk_info.get("used", 0),
                network_upload=net_info.get("bytes_sent", 0),
                network_download=net_info.get("bytes_recv", 0),
                uptime=sys_info.get("uptime_seconds", 0.0),
            )

            record = await self.system_service.record_system_metrics(dto)
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.info("collection_completed", collector="system_metrics", duration_ms=duration)
            return record
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("collection_failed", collector="system_metrics", error=str(exc), duration_ms=duration)
            return None

    async def collect_resource_metrics(self) -> List[ResourceMetric]:
        """Collects CPU, Memory, Disk, and Network hardware utilization metrics."""
        start_time = time.perf_counter()
        logger.info("collection_started", collector="resource_metrics")
        records = []
        try:
            cpu_val = await asyncio.to_thread(self.cpu_monitor.get_cpu_usage)
            mem_val = await asyncio.to_thread(self.memory_monitor.get_memory_percent)
            mem_info = await asyncio.to_thread(self.memory_monitor.get_virtual_memory)
            disk_info = await asyncio.to_thread(self.disk_monitor.get_disk_usage)
            net_info = await asyncio.to_thread(self.network_monitor.get_network_io)

            resources = [
                (ResourceType.CPU, "cpu_overall", cpu_val, 100.0, cpu_val, "%", "normal"),
                (ResourceType.MEMORY, "memory_overall", float(mem_info.get("used", 0)), float(mem_info.get("total", 1)), mem_val, "bytes", "normal"),
                (ResourceType.DISK, "disk_root", float(disk_info.get("used", 0)), float(disk_info.get("total", 1)), float(disk_info.get("percent", 0.0)), "bytes", "normal"),
                (ResourceType.NETWORK, "network_io", float(net_info.get("bytes_recv", 0)), 1000000000.0, 0.0, "bytes", "normal"),
            ]

            for res_type, name, cur, max_v, pct, unit, status in resources:
                try:
                    dto = ResourceMetricCreate(
                        resource_type=res_type,
                        resource_name=name,
                        current_value=float(cur),
                        maximum_value=float(max_v),
                        percentage=float(pct),
                        unit=unit,
                        status=status,
                    )
                    rec = await self.resource_service.record_resource_metric(dto)
                    records.append(rec)
                except Exception as exc:
                    logger.warning("resource_metric_item_failed", resource=name, error=str(exc))

            duration = (time.perf_counter() - start_time) * 1000.0
            logger.info("collection_completed", collector="resource_metrics", duration_ms=duration, count=len(records))
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("collection_failed", collector="resource_metrics", error=str(exc), duration_ms=duration)
        return records

    async def collect_gpu_metrics(self) -> List[GPUMetric]:
        """Collects GPU hardware metrics if devices exist."""
        start_time = time.perf_counter()
        logger.info("collection_started", collector="gpu_metrics")
        records = []
        try:
            gpus = await asyncio.to_thread(self.gpu_monitor.get_gpu_devices)
            for gpu in gpus:
                try:
                    dto = GPUMetricCreate(
                        gpu_name=gpu.get("name", "Unknown GPU"),
                        gpu_index=int(gpu.get("device_index", 0)),
                        temperature=float(gpu.get("temperature_celsius", 0.0)),
                        memory_total=int(gpu.get("memory_total_mb", 0)),
                        memory_used=int(gpu.get("memory_used_mb", 0)),
                        utilization=float(gpu.get("load_percent", 0.0)),
                        power_usage=float(gpu.get("power_watts", 0.0)),
                        fan_speed=0.0,
                    )
                    rec = await self.resource_service.record_gpu_metric(dto)
                    records.append(rec)
                except Exception as exc:
                    logger.warning("gpu_metric_item_failed", device=gpu.get("name"), error=str(exc))

            duration = (time.perf_counter() - start_time) * 1000.0
            logger.info("collection_completed", collector="gpu_metrics", duration_ms=duration, count=len(records))
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("collection_failed", collector="gpu_metrics", error=str(exc), duration_ms=duration)
        return records

    async def collect_process_metrics(self) -> List[ProcessMetric]:
        """Collects top running process metrics."""
        start_time = time.perf_counter()
        logger.info("collection_started", collector="process_metrics")
        records = []
        try:
            top_procs = await asyncio.to_thread(self.process_monitor.get_top_cpu_processes, 10)
            for proc in top_procs:
                try:
                    dto = ProcessMetricCreate(
                        pid=proc["pid"],
                        process_name=proc["name"],
                        cpu_percent=proc["cpu_percent"],
                        memory_percent=proc["memory_percent"],
                        status=proc["status"],
                    )
                    rec = await self.resource_service.record_process_metric(dto)
                    records.append(rec)
                except Exception as exc:
                    logger.warning("process_metric_item_failed", pid=proc.get("pid"), error=str(exc))

            duration = (time.perf_counter() - start_time) * 1000.0
            logger.info("collection_completed", collector="process_metrics", duration_ms=duration, count=len(records))
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("collection_failed", collector="process_metrics", error=str(exc), duration_ms=duration)
        return records

    async def collect_health_metrics(self) -> Optional[HealthRecord]:
        """Evaluates overall system health status and records diagnostic record."""
        start_time = time.perf_counter()
        logger.info("collection_started", collector="health_metrics")
        try:
            cpu_val = await asyncio.to_thread(self.cpu_monitor.get_cpu_usage)
            mem_val = await asyncio.to_thread(self.memory_monitor.get_memory_percent)
            disk_val = float((await asyncio.to_thread(self.disk_monitor.get_disk_usage)).get("percent", 0.0))

            if cpu_val > 90.0 or mem_val > 95.0 or disk_val > 95.0:
                status = HealthStatus.OFFLINE
                message = f"High resource pressure: CPU {cpu_val}%, RAM {mem_val}%, Disk {disk_val}%"
            elif cpu_val > 80.0 or mem_val > 85.0 or disk_val > 85.0:
                status = HealthStatus.DEGRADED
                message = f"Elevated resource usage: CPU {cpu_val}%, RAM {mem_val}%, Disk {disk_val}%"
            else:
                status = HealthStatus.HEALTHY
                message = "All host system components operating within healthy limits."

            dto = HealthRecordCreate(
                component="system_hardware",
                status=status,
                message=message,
                metrics_summary={"cpu_usage": cpu_val, "memory_usage": mem_val, "disk_usage": disk_val},
            )
            record = await self.health_service.record_health(dto)
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.info("collection_completed", collector="health_metrics", duration_ms=duration)
            return record
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("collection_failed", collector="health_metrics", error=str(exc), duration_ms=duration)
            return None

    async def collect_dashboard_snapshot(self) -> DashboardSnapshot:
        """Aggregates all collectors and creates a new DashboardSnapshot record."""
        start_time = time.perf_counter()
        logger.info("collection_started", collector="dashboard_snapshot")
        try:
            sys_fut = self.collect_system_metrics()
            res_fut = self.collect_resource_metrics()
            gpu_fut = self.collect_gpu_metrics()
            proc_fut = self.collect_process_metrics()
            health_fut = self.collect_health_metrics()

            sys_rec, res_recs, gpu_recs, proc_recs, health_rec = await asyncio.gather(
                sys_fut, res_fut, gpu_fut, proc_fut, health_fut, return_exceptions=True
            )

            cpu_val = await asyncio.to_thread(self.cpu_monitor.get_cpu_usage)
            mem_val = await asyncio.to_thread(self.memory_monitor.get_memory_percent)
            health_score = max(0.0, min(1.0, 1.0 - (cpu_val / 200.0) - (mem_val / 200.0)))

            dto = DashboardSnapshotCreate(
                system_status={
                    "os": self.system_monitor.get_os(),
                    "uptime": self.system_monitor.get_uptime(),
                    "load": self.cpu_monitor.get_load_average(),
                },
                resource_status={
                    "cpu_percent": cpu_val,
                    "memory_percent": mem_val,
                    "gpu_count": len(gpu_recs) if isinstance(gpu_recs, list) else 0,
                    "process_count": self.process_monitor.get_process_count(),
                },
                active_agents=0,
                active_models=0,
                running_missions=0,
                running_workflows=0,
                voice_status="idle",
                health_score=health_score,
            )

            snapshot = await self.dashboard_service.create_snapshot(dto)
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.info("collection_completed", collector="dashboard_snapshot", snapshot_id=str(snapshot.id), duration_ms=duration)
            return snapshot
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000.0
            logger.error("collection_failed", collector="dashboard_snapshot", error=str(exc), duration_ms=duration)
            raise
