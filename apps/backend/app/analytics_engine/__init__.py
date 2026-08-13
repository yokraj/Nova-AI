"""Nova AI Enterprise Analytics Engine Package.

Provides historical time-series downsampling, batch metric aggregations, 12 core KPI
computations, trend directional analysis, z-score anomaly detection, diagnostic insight
generation, export-ready structured reporting, and automated retention cleanup.
"""

from app.analytics_engine.aggregator import AnalyticsAggregator
from app.analytics_engine.anomaly import AnomalyDetector
from app.analytics_engine.config import AnalyticsConfig
from app.analytics_engine.engine import AnalyticsEngine
from app.analytics_engine.exceptions import (
    AggregationError,
    AnalyticsEngineError,
    AnomalyDetectionError,
    InsightError,
    KPIError,
    ReportGenerationError,
    RetentionError,
    TrendAnalysisError,
)
from app.analytics_engine.insights import InsightsEngine
from app.analytics_engine.kpi import KPIEngine
from app.analytics_engine.reports import ReportGenerator
from app.analytics_engine.retention import RetentionManager
from app.analytics_engine.statistics import AnalyticsStatistics
from app.analytics_engine.timeseries import TimeSeriesEngine
from app.analytics_engine.trends import TrendAnalyzer

__all__ = [
    "AnalyticsEngine",
    "TimeSeriesEngine",
    "AnalyticsAggregator",
    "KPIEngine",
    "TrendAnalyzer",
    "AnomalyDetector",
    "InsightsEngine",
    "ReportGenerator",
    "RetentionManager",
    "AnalyticsStatistics",
    "AnalyticsConfig",
    "AnalyticsEngineError",
    "AggregationError",
    "TrendAnalysisError",
    "ReportGenerationError",
    "KPIError",
    "InsightError",
    "RetentionError",
    "AnomalyDetectionError",
]
