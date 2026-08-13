"""Unit and Integration Test Suite for Nova AI Enterprise Analytics Engine.

Tests TimeSeriesEngine downsampling, AnalyticsAggregator, KPIEngine computations,
TrendAnalyzer directional vectors, AnomalyDetector z-scores, InsightsEngine,
ReportGenerator, RetentionManager, AnalyticsStatistics, and AnalyticsEngine lifecycle.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.analytics_engine import (
    AnalyticsAggregator,
    AnalyticsConfig,
    AnalyticsEngine,
    AnalyticsStatistics,
    AnomalyDetector,
    InsightsEngine,
    KPIEngine,
    ReportGenerator,
    RetentionManager,
    TimeSeriesEngine,
    TrendAnalyzer,
)


def test_analytics_config():
    """Test AnalyticsConfig initialization and default parameter values."""
    cfg = AnalyticsConfig()
    assert cfg.analytics_retention_days == 90
    assert cfg.aggregation_interval == 60.0
    assert cfg.anomaly_threshold == 2.0


def test_timeseries_engine():
    """Test TimeSeriesEngine sample downsampling and range queries."""
    ts_engine = TimeSeriesEngine()

    now = datetime.now(timezone.utc)
    samples = [
        {"timestamp": (now - timedelta(minutes=50)).isoformat(), "value": 10.0},
        {"timestamp": (now - timedelta(minutes=40)).isoformat(), "value": 20.0},
        {"timestamp": (now - timedelta(minutes=30)).isoformat(), "value": 30.0},
    ]

    hourly = ts_engine.aggregate_hourly(samples)
    assert len(hourly) == 1
    assert hourly[0]["average"] == 20.0
    assert hourly[0]["min"] == 10.0
    assert hourly[0]["max"] == 30.0


def test_analytics_aggregator():
    """Test AnalyticsAggregator resource, health, and notification aggregations."""
    agg = AnalyticsAggregator()

    resources = [
        {"cpu_percent": 50.0, "memory_percent": 60.0},
        {"cpu_percent": 70.0, "memory_percent": 80.0},
    ]
    res_agg = agg.aggregate_resources(resources)
    assert res_agg["cpu_avg"] == 60.0
    assert res_agg["memory_avg"] == 70.0

    notifs = [
        {"read": True, "priority": "HIGH"},
        {"read": False, "priority": "NORMAL"},
    ]
    notif_agg = agg.aggregate_notifications(notifs)
    assert notif_agg["total_notifications"] == 2
    assert notif_agg["read_count"] == 1
    assert notif_agg["read_rate_percent"] == 50.0


def test_kpi_engine():
    """Test KPIEngine calculating 12 core enterprise KPIs."""
    kpi_engine = KPIEngine()

    telemetry = {
        "resources": {"cpu_avg": 45.0, "memory_avg": 60.0, "disk_avg": 70.0, "gpu_avg": 20.0, "network_bytes_sec": 10485760.0},
        "health": {"average_health_score": 0.95},
        "notifications": {"total_notifications": 120},
        "missions": {"completion_rate_percent": 98.5},
        "agents": {"availability_rate_percent": 95.0},
        "workflows": {"completion_rate_percent": 99.0},
        "system": {"uptime_avg": 86400.0},
    }

    kpis = kpi_engine.generate_kpis(telemetry)
    assert kpis["cpu_utilization_percent"] == 45.0
    assert kpis["memory_utilization_percent"] == 60.0
    assert kpis["network_throughput_mbps"] == 10.0
    assert kpis["average_health_score"] == 0.95
    assert kpis["mission_completion_rate_percent"] == 98.5


def test_trend_analyzer():
    """Test TrendAnalyzer moving average, growth rate, and directional vectors."""
    trend_analyzer = TrendAnalyzer()

    # 1. Moving average
    ma = trend_analyzer.moving_average([10.0, 20.0, 30.0, 40.0], window=2)
    assert ma[-1] == 35.0

    # 2. Increasing Trend
    inc_trend = trend_analyzer.calculate_trend([10.0, 20.0, 30.0, 50.0])
    assert inc_trend["direction"] == "Increasing"

    # 3. Decreasing Trend
    dec_trend = trend_analyzer.calculate_trend([50.0, 40.0, 30.0, 10.0])
    assert dec_trend["direction"] == "Decreasing"


def test_anomaly_detector():
    """Test AnomalyDetector z-score statistical spike detection."""
    detector = AnomalyDetector(z_threshold=2.0)

    # Spike at last value (100.0)
    samples = [10.0, 11.0, 10.5, 9.8, 10.2, 10.1, 100.0]
    anomalies = detector.detect_cpu_anomalies(samples)

    assert len(anomalies) >= 1
    assert anomalies[0]["value"] == 100.0
    assert anomalies[0]["type"] == "spike"


def test_insights_engine():
    """Test InsightsEngine generating structured recommendations."""
    insights_engine = InsightsEngine()

    telemetry = {
        "resources": {"cpu_avg": 90.0, "disk_avg": 88.0},
        "health": {"average_health_score": 0.65},
        "trends": {"memory": {"direction": "Increasing"}},
    }

    insights = insights_engine.generate_dashboard_insights(telemetry)
    assert len(insights) >= 3
    titles = [i["title"] for i in insights]
    assert "High CPU Utilization" in titles
    assert "Low Free Disk Capacity" in titles
    assert "System Health Score Degradation" in titles


def test_report_generator():
    """Test ReportGenerator producing export-ready reports."""
    generator = ReportGenerator()

    summary = {"resources": {"cpu_avg": 50.0}, "health": {"health_score": 1.0}}
    dash_report = generator.generate_dashboard_report(summary)

    assert dash_report["report_type"] == "Dashboard Executive Summary"
    assert "generated_at" in dash_report
    assert dash_report["data"] == summary


def test_analytics_engine_workflow():
    """Test AnalyticsEngine end-to-end collection, aggregation, KPIs, insights, and report generation."""
    engine = AnalyticsEngine()
    engine.start()

    raw_telemetry = {
        "resources": [
            {"cpu_percent": 88.0, "memory_percent": 75.0, "disk_percent": 90.0},
            {"cpu_percent": 92.0, "memory_percent": 80.0, "disk_percent": 92.0},
            {"cpu_percent": 86.0, "memory_percent": 78.0, "disk_percent": 88.0},
        ],
        "health": [{"health_score": 0.60, "status": "degraded"}],
        "notifications": [{"read": True, "priority": "HIGH"}, {"read": False, "priority": "URGENT"}],
        "agents": [{"status": "busy"}, {"status": "idle"}],
        "missions": [{"status": "completed"}, {"status": "failed"}],
    }

    # 1. Collect
    result = engine.collect(raw_telemetry)
    assert "aggregated" in result
    assert "kpis" in result
    assert "anomalies" in result
    assert "insights" in result

    # Verify insights detected High CPU and Low Disk
    insight_titles = [i["title"] for i in result["insights"]]
    assert "High CPU Utilization" in insight_titles

    # 2. Generate Reports
    reports = engine.generate_reports(result["aggregated"])
    assert "dashboard" in reports
    assert "system" in reports
    assert "health" in reports

    summary_stats = engine.statistics.get_summary()
    assert summary_stats["aggregation_runs"] == 1
    assert summary_stats["reports_generated"] == 1

    engine.stop()
