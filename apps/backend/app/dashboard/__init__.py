"""Nova AI Enterprise Dashboard Package.

Provides backend architecture, database persistence, business services, event tracking,
health diagnostics, and dependency injection providers for the Enterprise Dashboard.
"""

from app.dashboard.cache import DashboardCache, DashboardCacheService
from app.dashboard.config import DashboardConfig
from app.dashboard.exceptions import (
    ConfigurationNotFoundError,
    DashboardCacheError,
    DashboardConfigError,
    DashboardException,
    DashboardNotFoundError,
    DashboardSubscriptionError,
    EventNotFoundError,
    HealthRecordNotFoundError,
    MetricNotFoundError,
    NotificationNotFoundError,
)
from app.dashboard.routes import router as dashboard_router
from app.dashboard.services import (
    AgentDashboardService,
    AnalyticsService,
    DashboardEventManager,
    DashboardService,
    HealthService,
    MissionDashboardService,
    NotificationService,
    ResourceMonitorService,
    SystemMonitorService,
)

__all__ = [
    "DashboardConfig",
    "DashboardService",
    "SystemMonitorService",
    "ResourceMonitorService",
    "MissionDashboardService",
    "AgentDashboardService",
    "NotificationService",
    "AnalyticsService",
    "HealthService",
    "DashboardCacheService",
    "DashboardCache",
    "DashboardEventManager",
    "DashboardException",
    "DashboardNotFoundError",
    "NotificationNotFoundError",
    "MetricNotFoundError",
    "HealthRecordNotFoundError",
    "ConfigurationNotFoundError",
    "EventNotFoundError",
    "dashboard_router",
]
