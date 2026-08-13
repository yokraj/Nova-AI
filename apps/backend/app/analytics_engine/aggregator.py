"""Analytics Aggregator Module.

Aggregates raw hardware metrics, system states, health records, notifications,
agent workforce data, and mission execution telemetry into summary metrics DTOs.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class AnalyticsAggregator:
    """Enterprise Analytics Aggregator across all Nova AI telemetry domains."""

    def __init__(self) -> None:
        logger.info("analytics_aggregator_initialized")

    def aggregate_resources(self, resource_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates resource metrics (CPU, RAM, Disk, Network, GPU)."""
        if not resource_metrics:
            return {"cpu_avg": 0.0, "memory_avg": 0.0, "disk_avg": 0.0, "gpu_avg": 0.0, "count": 0}

        cpus = [m.get("cpu_percent", 0.0) for m in resource_metrics if "cpu_percent" in m]
        mems = [m.get("memory_percent", 0.0) for m in resource_metrics if "memory_percent" in m]
        disks = [m.get("disk_percent", 0.0) for m in resource_metrics if "disk_percent" in m]
        gpus = [m.get("gpu_percent", 0.0) for m in resource_metrics if "gpu_percent" in m]

        return {
            "cpu_avg": round(sum(cpus) / len(cpus), 2) if cpus else 0.0,
            "memory_avg": round(sum(mems) / len(mems), 2) if mems else 0.0,
            "disk_avg": round(sum(disks) / len(disks), 2) if disks else 0.0,
            "gpu_avg": round(sum(gpus) / len(gpus), 2) if gpus else 0.0,
            "count": len(resource_metrics),
        }

    def aggregate_notifications(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates notification counts, read rates, and priority distribution."""
        total = len(notifications)
        read_count = sum(1 for n in notifications if n.get("read") or n.get("is_read"))
        unread_count = total - read_count

        priority_counts: Dict[str, int] = {}
        for n in notifications:
            prio = str(n.get("priority", "NORMAL")).upper()
            priority_counts[prio] = priority_counts.get(prio, 0) + 1

        return {
            "total_notifications": total,
            "read_count": read_count,
            "unread_count": unread_count,
            "read_rate_percent": round((read_count / total * 100.0), 2) if total > 0 else 0.0,
            "priority_distribution": priority_counts,
        }

    def aggregate_health(self, health_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates health scores and status distribution."""
        if not health_records:
            return {"average_health_score": 1.0, "status_counts": {"healthy": 0}, "total_records": 0}

        scores = [h.get("health_score", 1.0) for h in health_records]
        avg_score = sum(scores) / len(scores) if scores else 1.0

        status_counts: Dict[str, int] = {}
        for h in health_records:
            st = str(h.get("status", "healthy")).lower()
            status_counts[st] = status_counts.get(st, 0) + 1

        return {
            "average_health_score": round(avg_score, 2),
            "status_counts": status_counts,
            "total_records": len(health_records),
        }

    def aggregate_agents(self, agent_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates agent workforce availability and status."""
        total = len(agent_data)
        active = sum(1 for a in agent_data if a.get("status") in ["active", "idle", "busy"])
        busy = sum(1 for a in agent_data if a.get("status") == "busy")

        return {
            "total_agents": total,
            "active_agents": active,
            "busy_agents": busy,
            "availability_rate_percent": round((active / total * 100.0), 2) if total > 0 else 100.0,
        }

    def aggregate_missions(self, mission_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates mission execution completion rates and status."""
        total = len(mission_data)
        completed = sum(1 for m in mission_data if m.get("status") == "completed")
        failed = sum(1 for m in mission_data if m.get("status") == "failed")
        running = sum(1 for m in mission_data if m.get("status") == "running")

        return {
            "total_missions": total,
            "completed_missions": completed,
            "failed_missions": failed,
            "running_missions": running,
            "completion_rate_percent": round((completed / total * 100.0), 2) if total > 0 else 0.0,
        }

    def aggregate_system(self, system_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates system OS uptime and node telemetry."""
        if not system_metrics:
            return {"uptime_avg": 0.0, "nodes_count": 1}
        uptimes = [s.get("uptime", 0.0) for s in system_metrics if "uptime" in s]
        return {
            "uptime_avg": round(sum(uptimes) / len(uptimes), 2) if uptimes else 0.0,
            "nodes_count": len(system_metrics),
        }

    def aggregate_dashboard(self, snapshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates consolidated dashboard overview snapshots."""
        total = len(snapshot_data)
        if total == 0:
            return {"health_score_avg": 1.0, "snapshots_count": 0}

        scores = [s.get("health_score", 1.0) for s in snapshot_data]
        return {
            "health_score_avg": round(sum(scores) / len(scores), 2),
            "snapshots_count": total,
        }

    def aggregate_metrics(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Runs batch aggregation across all telemetry domain lists."""
        return {
            "resources": self.aggregate_resources(raw_telemetry.get("resources", [])),
            "notifications": self.aggregate_notifications(raw_telemetry.get("notifications", [])),
            "health": self.aggregate_health(raw_telemetry.get("health", [])),
            "agents": self.aggregate_agents(raw_telemetry.get("agents", [])),
            "missions": self.aggregate_missions(raw_telemetry.get("missions", [])),
            "system": self.aggregate_system(raw_telemetry.get("system", [])),
            "dashboard": self.aggregate_dashboard(raw_telemetry.get("snapshots", [])),
        }
