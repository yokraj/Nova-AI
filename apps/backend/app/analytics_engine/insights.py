"""Insights Engine Module.

Generates structured diagnostic insight objects based on system telemetry,
trend directional analysis, statistical anomaly signals, and operational thresholds.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

logger = structlog.get_logger(__name__)


class InsightsEngine:
    """Enterprise Insights Engine generating structured operational recommendations."""

    def __init__(self, confidence_threshold: float = 0.8) -> None:
        self.confidence_threshold = confidence_threshold
        logger.info("insights_engine_initialized", confidence_threshold=confidence_threshold)

    def generate_dashboard_insights(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluates telemetry data dictionary and returns list of structured insight DTOs."""
        insights = []

        res = telemetry_data.get("resources", {})
        health = telemetry_data.get("health", {})
        missions = telemetry_data.get("missions", {})
        agents = telemetry_data.get("agents", {})
        notifs = telemetry_data.get("notifications", {})
        trends = telemetry_data.get("trends", {})

        # 1. High CPU Usage Insight
        cpu = res.get("cpu_avg", res.get("cpu_percent", 0.0))
        if cpu >= 85.0:
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "High CPU Utilization",
                "type": "performance_warning",
                "severity": "CRITICAL" if cpu >= 95.0 else "WARNING",
                "description": f"Host CPU utilization is sustained at {cpu:.1f}%. Consider scaling background worker pools.",
                "confidence": 0.95,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # 2. Increasing RAM Trend Insight
        ram_trend = trends.get("memory", {}).get("direction", "Stable")
        if ram_trend == "Increasing":
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "Memory Consumption Trending Upward",
                "type": "capacity_warning",
                "severity": "WARNING",
                "description": "RAM usage is exhibiting a consistent upward trend. Check for potential memory leaks.",
                "confidence": 0.85,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # 3. Low Disk Space Insight
        disk = res.get("disk_avg", res.get("disk_percent", 0.0))
        if disk >= 85.0:
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "Low Free Disk Capacity",
                "type": "storage_alert",
                "severity": "CRITICAL" if disk >= 95.0 else "WARNING",
                "description": f"Root disk partition storage usage is at {disk:.1f}%. Retention cleanup recommended.",
                "confidence": 0.90,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # 4. Health Degradation Insight
        health_score = health.get("average_health_score", health.get("health_score", 1.0))
        if health_score < 0.7:
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "System Health Score Degradation",
                "type": "health_alert",
                "severity": "CRITICAL",
                "description": f"Overall system health score dropped to {health_score:.2f}. Inspect active alerts.",
                "confidence": 0.95,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # 5. Frequent Mission Failures Insight
        failed_missions = missions.get("failed_missions", 0)
        if failed_missions >= 3:
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "Frequent Mission Failures Detected",
                "type": "workflow_alert",
                "severity": "HIGH",
                "description": f"{failed_missions} mission executions failed recently. Review agent error logs.",
                "confidence": 0.88,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # 6. Agent Instability Insight
        avail_rate = agents.get("availability_rate_percent", 100.0)
        if avail_rate < 80.0:
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "Workforce Agent Instability",
                "type": "workforce_alert",
                "severity": "HIGH",
                "description": f"Agent workforce availability rate dropped to {avail_rate:.1f}%. Check node connections.",
                "confidence": 0.85,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        # 7. Notification Spikes Insight
        notif_count = notifs.get("total_notifications", 0)
        if notif_count >= 50:
            insights.append({
                "insight_id": str(uuid.uuid4()),
                "title": "Notification Burst Detected",
                "type": "alert_spike",
                "severity": "MEDIUM",
                "description": f"{notif_count} alert notifications generated in short timeframe. Check system logs.",
                "confidence": 0.80,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        logger.info("insights_generated", count=len(insights))
        return insights
