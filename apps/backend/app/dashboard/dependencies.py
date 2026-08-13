"""Dashboard Dependency Providers Module.

Provides FastAPI dependency injection functions for injecting repository-backed
dashboard services, monitoring services, notification managers, analytics services,
health services, event managers, and cache services.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.cache import DashboardCacheService
from app.dashboard.repositories import (
    AnalyticsRepository,
    ConfigurationRepository,
    DashboardBaseRepository,
    DashboardRepository,
    HealthRepository,
    MetricsRepository,
    NotificationRepository,
)
from app.dashboard.service import (
    AgentDashboardService,
    AnalyticsService,
    DashboardCacheService,
    DashboardEventManager,
    DashboardService,
    HealthService,
    MissionDashboardService,
    NotificationService,
    ResourceMonitorService,
    SystemMonitorService,
)
from app.database.models.dashboard import DashboardEvent
from app.database.session import get_db

# Singleton cache instance for in-memory caching across requests
_global_cache_service = DashboardCacheService(default_ttl=60)


def get_cache_service() -> DashboardCacheService:
    """FastAPI dependency provider returning the global in-memory DashboardCacheService.
    
    Returns:
        DashboardCacheService instance.
    """
    return _global_cache_service


def get_dashboard_service(session: AsyncSession = Depends(get_db)) -> DashboardService:
    """FastAPI dependency provider returning DashboardService instance.
    
    Returns:
        DashboardService backed by DashboardRepository.
    """
    repo = DashboardRepository(session)
    return DashboardService(repository=repo)


def get_monitor_service(session: AsyncSession = Depends(get_db)) -> SystemMonitorService:
    """FastAPI dependency provider returning SystemMonitorService instance.
    
    Returns:
        SystemMonitorService backed by MetricsRepository.
    """
    repo = MetricsRepository(session)
    return SystemMonitorService(metrics_repository=repo)


def get_resource_service(session: AsyncSession = Depends(get_db)) -> ResourceMonitorService:
    """FastAPI dependency provider returning ResourceMonitorService instance.
    
    Returns:
        ResourceMonitorService backed by MetricsRepository.
    """
    repo = MetricsRepository(session)
    return ResourceMonitorService(metrics_repository=repo)


def get_notification_service(session: AsyncSession = Depends(get_db)) -> NotificationService:
    """FastAPI dependency provider returning NotificationService instance.
    
    Returns:
        NotificationService backed by NotificationRepository.
    """
    repo = NotificationRepository(session)
    return NotificationService(repository=repo)


def get_analytics_service(session: AsyncSession = Depends(get_db)) -> AnalyticsService:
    """FastAPI dependency provider returning AnalyticsService instance.
    
    Returns:
        AnalyticsService backed by AnalyticsRepository.
    """
    repo = AnalyticsRepository(session)
    return AnalyticsService(repository=repo)


def get_health_service(session: AsyncSession = Depends(get_db)) -> HealthService:
    """FastAPI dependency provider returning HealthService instance.
    
    Returns:
        HealthService backed by HealthRepository.
    """
    repo = HealthRepository(session)
    return HealthService(repository=repo)


def get_event_manager(session: AsyncSession = Depends(get_db)) -> DashboardEventManager:
    """FastAPI dependency provider returning DashboardEventManager instance.
    
    Returns:
        DashboardEventManager backed by DashboardBaseRepository for DashboardEvent.
    """
    repo = DashboardBaseRepository(DashboardEvent, session)
    return DashboardEventManager(repository=repo)
