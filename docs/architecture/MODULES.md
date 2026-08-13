# Nova AI Enterprise Dashboard Package & Module Reference

## Executive Overview
This document provides a comprehensive technical reference for all core packages, modules, repositories, and services comprising the **Nova AI Enterprise Dashboard Backend**.

---

## 1. Module Reference Catalog

### 1. `app.dashboard`
- **Purpose**: Central domain package for business services, REST API routes, schemas, database models, and repositories.
- **Responsibilities**: Orchestrates REST presentation, caching, permission enforcement, overview aggregation, and database persistence.
- **Dependencies**: `app.security`, `app.identity`, `sqlalchemy`, `pydantic`.
- **Public Interfaces**:
  - `DashboardOverviewService`, `SystemDashboardService`, `ResourceDashboardService`, `HealthDashboardService`
  - REST Routers: `/api/v1/dashboard/overview`, `/metrics`, `/health`, `/activity`, `/events`

---

### 2. `app.monitoring`
- **Purpose**: System Monitoring Engine collecting real hardware telemetry from the host system.
- **Responsibilities**: Polling CPU, Memory, Disk, Network IO, GPU, Processes, and System hardware metrics using `psutil` and `GPUtil`.
- **Dependencies**: `psutil`, `GPUtil`, `structlog`, `asyncio`.
- **Public Interfaces**:
  - `SystemMonitoringEngine`
  - Collectors: `CPUMonitor`, `MemoryMonitor`, `DiskMonitor`, `NetworkMonitor`, `GPUMonitor`, `ProcessMonitor`, `SystemMonitor`

---

### 3. `app.live_metrics`
- **Purpose**: Live Metrics Streaming Engine computing differential telemetry deltas and snapshot history.
- **Responsibilities**: Delta change detection, snapshot buffering, rate-limited metric publishing over WebSockets.
- **Dependencies**: `app.monitoring`, `app.websocket`.
- **Public Interfaces**:
  - `LiveMetricsEngine`
  - Subcomponents: `ChangeDetector`, `SnapshotManager`, `MetricsBuffer`, `MetricsRateLimiter`, `MetricsPublisher`

---

### 4. `app.websocket`
- **Purpose**: Authenticated, scalable WebSocket Gateway and channel pub/sub infrastructure.
- **Responsibilities**: WebSocket connection lifecycle management, ping/pong heartbeats, channel subscriptions, topic broadcasting.
- **Dependencies**: `fastapi`, `structlog`, `asyncio`, `pydantic`.
- **Public Interfaces**:
  - `ConnectionManager`, `DashboardBroadcaster`, `SubscriptionManager`, `HeartbeatManager`, `EventRouter`, `WebSocketConnection`

---

### 5. `app.notification_engine`
- **Purpose**: Rule-based notification generation, priority queuing, and deduplication platform.
- **Responsibilities**: Threshold rule evaluation, priority score ranking, fingerprint deduplication, queue dispatching.
- **Dependencies**: `app.websocket`, `structlog`, `pydantic`.
- **Public Interfaces**:
  - `NotificationEngine`
  - Subcomponents: `NotificationRuleEngine`, `PriorityManager`, `NotificationDeduplicator`, `NotificationQueue`, `NotificationDispatcher`

---

### 6. `app.analytics_engine`
- **Purpose**: Historical analytics, time-series downsampling, 12 core KPI calculations, and anomaly detection.
- **Responsibilities**: Aggregating time-series buckets, computing trends and forecasts, detecting statistical spikes, report generation.
- **Dependencies**: `app.live_metrics`, `pydantic`, `structlog`.
- **Public Interfaces**:
  - `AnalyticsEngine`
  - Subcomponents: `TimeSeriesEngine`, `AnalyticsAggregator`, `KPIEngine`, `TrendAnalyzer`, `AnomalyDetector`, `InsightsEngine`, `ReportGenerator`

---

### 7. `app.security`
- **Purpose**: Enterprise security hardening, audit logging, threat detection, and rate limiting.
- **Responsibilities**: Request rate limiting, session revocation, audit log ring buffer, threat intrusion alerts, security headers middleware.
- **Dependencies**: `app.identity.infrastructure.rbac`, `starlette`, `fastapi`.
- **Public Interfaces**:
  - `DashboardSecurityMiddleware`, `AuditLogger`, `SecurityMonitor`, `DashboardRateLimiter`, `DashboardSessionManager`, `WebSocketSecurityManager`, `ThreatDetector`, `ComplianceManager`

---

### 8. `app.dashboard.repositories`
- **Purpose**: Data access layer managing persistence for dashboard entities.
- **Responsibilities**: Encapsulates raw SQLAlchemy queries for system metrics, health logs, notifications, and settings.
- **Dependencies**: `sqlalchemy.ext.asyncio`, `app.dashboard.models`.
- **Public Interfaces**:
  - `DashboardRepository`, `SystemMetricRepository`, `HealthLogRepository`, `NotificationRepository`, `DashboardSettingRepository`

---

### 9. `app.dashboard.services`
- **Purpose**: Asynchronous business service layer.
- **Responsibilities**: Implements core business logic, cache integration via `DashboardCacheService`, and coordinate repository interactions.
- **Dependencies**: `app.dashboard.repositories`, `app.dashboard.schemas`.
- **Public Interfaces**:
  - `DashboardOverviewService`, `SystemDashboardService`, `ResourceDashboardService`, `HealthDashboardService`, `DashboardCacheService`
