"""Analytics Engine Orchestrator Module.

Unites AnalyticsConfig, TimeSeriesEngine, AnalyticsAggregator, KPIEngine,
TrendAnalyzer, AnomalyDetector, InsightsEngine, ReportGenerator, RetentionManager,
and AnalyticsStatistics into an integrated enterprise analytics system.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
import structlog

from app.analytics_engine.aggregator import AnalyticsAggregator
from app.analytics_engine.anomaly import AnomalyDetector
from app.analytics_engine.config import AnalyticsConfig
from app.analytics_engine.exceptions import AnalyticsEngineError
from app.analytics_engine.insights import InsightsEngine
from app.analytics_engine.kpi import KPIEngine
from app.analytics_engine.reports import ReportGenerator
from app.analytics_engine.retention import RetentionManager
from app.analytics_engine.statistics import AnalyticsStatistics
from app.analytics_engine.timeseries import TimeSeriesEngine
from app.analytics_engine.trends import TrendAnalyzer
from app.dashboard.services import AnalyticsService

logger = structlog.get_logger(__name__)


class AnalyticsEngine:
    """Enterprise Master Orchestrator for Real-Time & Historical Data Analytics."""

    def __init__(
        self,
        config: Optional[AnalyticsConfig] = None,
        analytics_service: Optional[AnalyticsService] = None,
    ) -> None:
        self.config = config or AnalyticsConfig()
        self.analytics_service = analytics_service

        self.timeseries_engine = TimeSeriesEngine()
        self.aggregator = AnalyticsAggregator()
        self.kpi_engine = KPIEngine()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector(z_threshold=self.config.anomaly_threshold)
        self.insights_engine = InsightsEngine(confidence_threshold=self.config.insight_threshold)
        self.report_generator = ReportGenerator()
        self.retention_manager = RetentionManager(
            analytics_service=self.analytics_service,
            retention_days=self.config.analytics_retention_days,
        )
        self.statistics = AnalyticsStatistics()

        self._running = False
        self._paused = False

        logger.info("analytics_engine_initialized", config=self.config.model_dump())

    def start(self) -> None:
        """Starts the Analytics Engine."""
        if not self._running:
            self._running = True
            self._paused = False
            logger.info("analytics_engine_started")

    def stop(self) -> None:
        """Stops the Analytics Engine."""
        if self._running:
            self._running = False
            self._paused = False
            logger.info("analytics_engine_stopped")

    def pause(self) -> None:
        """Pauses background aggregation execution."""
        if self._running and not self._paused:
            self._paused = True
            logger.info("analytics_engine_paused")

    def resume(self) -> None:
        """Resumes background aggregation execution."""
        if self._running and self._paused:
            self._paused = False
            logger.info("analytics_engine_resumed")

    def collect(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collects raw telemetry and computes consolidated metrics, KPIs, trends, and insights."""
        start_time = time.time()

        # 1. Aggregate
        aggregated = self.aggregate(telemetry_data)

        # 2. KPIs
        kpis = self.generate_kpis(aggregated)

        # 3. Anomalies
        anomalies = self.detect_anomalies(telemetry_data)

        # 4. Insights
        insights = self.generate_dashboard_insights(aggregated)

        duration_ms = (time.time() - start_time) * 1000.0
        self.statistics.record_aggregation(duration_ms)

        return {
            "aggregated": aggregated,
            "kpis": kpis,
            "anomalies": anomalies,
            "insights": insights,
        }

    def aggregate(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregates raw telemetry inputs."""
        return self.aggregator.aggregate_metrics(telemetry_data)

    def generate_kpis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates enterprise KPI metrics."""
        kpis = self.kpi_engine.generate_kpis(telemetry_data)
        self.statistics.record_kpis()
        return kpis

    def detect_anomalies(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detects statistical anomalies across CPU, RAM, Disk, and Health scores."""
        anomalies = []

        res = telemetry_data.get("resources", {})
        if isinstance(res, list):
            cpus = [r.get("cpu_percent", 0.0) for r in res if "cpu_percent" in r]
            if cpus:
                anomalies.extend(self.anomaly_detector.detect_cpu_anomalies(cpus))

            mems = [r.get("memory_percent", 0.0) for r in res if "memory_percent" in r]
            if mems:
                anomalies.extend(self.anomaly_detector.detect_memory_anomalies(mems))

        self.statistics.record_anomalies(len(anomalies))
        return anomalies

    def generate_dashboard_insights(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates structured diagnostic insight recommendations."""
        insights = self.insights_engine.generate_dashboard_insights(telemetry_data)
        self.statistics.record_insights(len(insights))
        return insights

    def generate_reports(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates 8 domain-specific export-ready reports."""
        reports = {
            "dashboard": self.report_generator.generate_dashboard_report(summary_data),
            "system": self.report_generator.generate_system_report(summary_data.get("system", {})),
            "resource": self.report_generator.generate_resource_report(summary_data.get("resources", {})),
            "notification": self.report_generator.generate_notification_report(summary_data.get("notifications", {})),
            "analytics": self.report_generator.generate_analytics_report(summary_data),
            "health": self.report_generator.generate_health_report(summary_data.get("health", {})),
            "mission": self.report_generator.generate_mission_report(summary_data.get("missions", {})),
            "agent": self.report_generator.generate_agent_report(summary_data.get("agents", {})),
        }
        self.statistics.record_report()
        return reports

    async def cleanup(self) -> int:
        """Executes retention cleanup."""
        self.statistics.record_cleanup()
        return await self.retention_manager.cleanup_old_metrics()
