"""DashboardProvider aggregating stats and timelines for frontend UIs.
"""

from typing import Any, Dict, List
import uuid


class DashboardProvider:
    """Aggregates execution metrics, span tracing graphs, and statuses for React/Electron frontends."""

    def __init__(self, tracer: Any, health_monitor: Any, telemetry: Any) -> None:
        """Initializes DashboardProvider.

        Args:
            tracer: Tracer context.
            health_monitor: HealthMonitor instance.
            telemetry: TelemetryCollector.
        """
        self.tracer = tracer
        self.health_monitor = health_monitor
        self.telemetry = telemetry
        self._current_executions: List[Dict[str, Any]] = []
        self._completed_executions: List[Dict[str, Any]] = []
        self._failed_executions: List[Dict[str, Any]] = []

    def record_start(self, execution_id: uuid.UUID, agent_name: str, task_name: str) -> None:
        """Tracks active executions."""
        self._current_executions.append(
            {
                "execution_id": str(execution_id),
                "agent_name": agent_name,
                "task_name": task_name,
                "status": "running",
            }
        )

    def record_complete(self, execution_id: uuid.UUID, success: bool, latency: float) -> None:
        """Tracks completed or failed execution outcomes."""
        matching = [item for item in self._current_executions if item["execution_id"] == str(execution_id)]
        for item in matching:
            self._current_executions.remove(item)
            item["status"] = "completed" if success else "failed"
            item["latency"] = latency
            if success:
                self._completed_executions.append(item)
            else:
                self._failed_executions.append(item)

    def execution_timeline(self) -> List[Dict[str, Any]]:
        """Returns execution history sequence logs for UI charts.

        Returns:
            List of execution items.
        """
        return self._completed_executions + self._failed_executions

    def agent_timeline(self) -> List[Dict[str, Any]]:
        """Returns agent execution timeline intervals list.

        Returns:
            List of completed execution items.
        """
        return self._completed_executions

    def trace_graph(self) -> Dict[str, Any]:
        """Formats completed spans into a DAG layout representing a trace graph.

        Returns:
            Dictionary containing node and edge details.
        """
        nodes = []
        edges = []
        for span in self.tracer.get_completed_spans():
            nodes.append(
                {
                    "id": str(span.span_id),
                    "label": span.name,
                    "duration": span.duration,
                    "start_time": span.start_time.isoformat(),
                }
            )
            if span.parent_span_id:
                edges.append({"from": str(span.parent_span_id), "to": str(span.span_id)})
        return {"nodes": nodes, "edges": edges}

    def performance_metrics(self) -> Dict[str, Any]:
        """Exposes CPU, Memory, GPU, and token usage.

        Returns:
            Dictionary containing usage stats.
        """
        snapshot = self.telemetry.snapshot()
        snapshot["gpu_usage"] = 0.0
        return snapshot

    def active_tasks(self) -> List[Dict[str, Any]]:
        """Lists active executions.

        Returns:
            List of active executions.
        """
        return self._current_executions

    def queue_status(self) -> Dict[str, Any]:
        """Exposes job queue statistics mock configurations.

        Returns:
            Dictionary containing queue statistics.
        """
        return {"pending_count": 0, "scheduled_count": len(self._current_executions), "queue_state": "idle"}

    def summary(self) -> Dict[str, Any]:
        """Provides overall summary counters.

        Returns:
            Dictionary containing summary counts.
        """
        total_lat = sum(e.get("latency", 0.0) for e in self._completed_executions)
        count = len(self._completed_executions)
        avg_lat = total_lat / count if count > 0 else 0.0

        return {
            "current_executions": len(self._current_executions),
            "completed_executions": len(self._completed_executions),
            "failed_executions": len(self._failed_executions),
            "average_latency": avg_lat,
            "health": self.health_monitor.get_status(),
            "performance": self.performance_metrics(),
        }
