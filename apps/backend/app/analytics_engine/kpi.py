"""KPI Engine Module.

Computes 12 core enterprise performance Key Performance Indicators (KPIs)
including hardware utilization, throughput, completion rates, and availability.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class KPIEngine:
    """Enterprise Key Performance Indicator (KPI) calculation engine."""

    def __init__(self) -> None:
        logger.info("kpi_engine_initialized")

    def generate_kpis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates 12 core KPIs from consolidated telemetry data."""
        res = telemetry_data.get("resources", {})
        health = telemetry_data.get("health", {})
        notifs = telemetry_data.get("notifications", {})
        missions = telemetry_data.get("missions", {})
        agents = telemetry_data.get("agents", {})
        workflows = telemetry_data.get("workflows", {})
        system = telemetry_data.get("system", {})

        # 1. CPU Utilization (%)
        cpu_util = float(res.get("cpu_avg", res.get("cpu_percent", 0.0)))

        # 2. GPU Utilization (%)
        gpu_util = float(res.get("gpu_avg", res.get("gpu_percent", 0.0)))

        # 3. Memory Utilization (%)
        mem_util = float(res.get("memory_avg", res.get("memory_percent", 0.0)))

        # 4. Disk Utilization (%)
        disk_util = float(res.get("disk_avg", res.get("disk_percent", 0.0)))

        # 5. Network Throughput (MB/s)
        net_throughput = float(res.get("network_bytes_sec", 0.0)) / (1024 * 1024)

        # 6. Average Response Time (ms)
        avg_response_time = float(telemetry_data.get("avg_response_time_ms", 15.0))

        # 7. Average Health Score (0.0 to 1.0)
        avg_health_score = float(health.get("average_health_score", health.get("health_score", 1.0)))

        # 8. Notification Rate (notifs/min)
        notif_rate = float(notifs.get("total_notifications", 0)) / 60.0

        # 9. Mission Completion Rate (%)
        mission_rate = float(missions.get("completion_rate_percent", 100.0))

        # 10. Agent Availability (%)
        agent_availability = float(agents.get("availability_rate_percent", 100.0))

        # 11. Workflow Completion Rate (%)
        workflow_rate = float(workflows.get("completion_rate_percent", 100.0))

        # 12. System Uptime (seconds)
        system_uptime = float(system.get("uptime_avg", system.get("uptime_seconds", 86400.0)))

        return {
            "cpu_utilization_percent": round(cpu_util, 2),
            "gpu_utilization_percent": round(gpu_util, 2),
            "memory_utilization_percent": round(mem_util, 2),
            "disk_utilization_percent": round(disk_util, 2),
            "network_throughput_mbps": round(net_throughput, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "average_health_score": round(avg_health_score, 2),
            "notification_rate_per_min": round(notif_rate, 2),
            "mission_completion_rate_percent": round(mission_rate, 2),
            "agent_availability_percent": round(agent_availability, 2),
            "workflow_completion_rate_percent": round(workflow_rate, 2),
            "system_uptime_seconds": round(system_uptime, 2),
        }
