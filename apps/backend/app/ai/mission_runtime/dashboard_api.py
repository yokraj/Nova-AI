"""Dashboard API serving mission list, timeline, logs, telemetry, and state.
"""

from typing import Any, Dict, List
import time
from app.ai.mission_runtime.interfaces import IDashboardAPI


class DashboardAPI(IDashboardAPI):
    """Dashboard API providing aggregated administrative data views for frontend UI."""

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Provides dashboard summary telemetry.

        Returns:
            Dictionary containing active missions, timelines, health metrics, and logs.
        """
        timeline = [
            {"timestamp": time.time() - 3600, "event": "Mission 'File GST Return' created"},
            {"timestamp": time.time() - 1800, "event": "Completed Task 1: Scrape GST Portal invoices"},
            {"timestamp": time.time() - 600, "event": "Requested Approval: Confirm GST payment"},
            {"timestamp": time.time() - 100, "event": "User approved payment"},
        ]

        return {
            "active_missions_count": 2,
            "completed_missions_count": 14,
            "system_health": "HEALTHY",
            "timeline": timeline,
            "metrics": {
                "avg_recovery_time_seconds": 1.2,
                "checkpoint_success_rate": 100.0,
            },
        }
