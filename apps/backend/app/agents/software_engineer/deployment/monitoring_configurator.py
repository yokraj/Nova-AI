"""Monitoring Configurator generates Prometheus dashboards, alerts, and integrates with Observability SDK.
"""

from typing import Any, Dict
from app.agents.software_engineer.deployment.interfaces import IMonitoringConfigurator
from app.agents.software_engineer.deployment.models import EnvironmentInfo
from app.agent_sdk.observability.metrics import MetricsCollector
from app.agent_sdk.observability.logger import StructuredLogger

class LocalMonitoringConfigurator(IMonitoringConfigurator):
    """Hooks up Observability metrics and outputs alerting rule templates."""

    def __init__(self) -> None:
        self.metrics = MetricsCollector()
        self.logger = StructuredLogger(agent_name="deployment_monitor")

    def configure(self, project_path: str, env_info: EnvironmentInfo) -> Dict[str, Any]:
        """Outputs Prometheus alert templates and configures metrics logger."""
        self.logger.info("Configuring monitoring templates", metadata={"project_path": project_path})
        if hasattr(self.metrics, "increment"):
            self.metrics.increment("deployment_monitoring_configured_total")

        # 1. Prometheus Alert rules YAML
        prometheus_yaml = """groups:
  - name: application-alerts
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Instance Down"
          description: "Target application endpoint has been down for > 5 minutes."
      - alert: HighRequestLatency
        expr: http_request_duration_seconds{quantile="0.9"} > 0.5
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "High Latency Detected"
          description: "90th percentile of latency is above 500ms."
"""

        # 2. Grafana basic dashboard config
        grafana_dashboard_json = """{
  "title": "Application Metrics Dashboard",
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        { "expr": "rate(http_requests_total[5m])" }
      ]
    },
    {
      "title": "Error Rate",
      "type": "graph",
      "targets": [
        { "expr": "rate(http_requests_failed_total[5m])" }
      ]
    }
  ]
}"""

        return {
          "prometheus_alerts.yml": prometheus_yaml,
          "grafana_dashboard.json": grafana_dashboard_json,
        }
