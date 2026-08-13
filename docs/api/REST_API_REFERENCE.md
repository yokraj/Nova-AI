# Nova AI Enterprise Dashboard REST API Reference

## API Overview
The Enterprise Dashboard REST API provides production-ready, OpenAPI-compliant JSON endpoints for querying system status, historical metrics, analytical reports, active notifications, and health diagnostics.

- **Base URL**: `/api/v1/dashboard`
- **Authentication**: Bearer Token (`Authorization: Bearer <jwt_token>`)
- **Required RBAC Permissions**: `dashboard:read`, `dashboard:write`, `dashboard:admin`

---

## 1. Dashboard Overview Endpoint

### `GET /api/v1/dashboard/overview`
Returns high-level consolidated system overview metrics, active agent workforce counts, mission throughput, and hardware summaries.

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**: None
- **Permission Required**: `dashboard:read`
- **Status Codes**:
  - `200 OK`: Request succeeded.
  - `401 Unauthorized`: Invalid or missing token.
  - `403 Forbidden`: Insufficient RBAC permissions.
  - `429 Too Many Requests`: Rate limit exceeded.

#### Response Example (`200 OK`):
```json
{
  "system_status": "healthy",
  "health_score": 0.98,
  "active_agents": 12,
  "active_missions": 4,
  "cpu_usage_percent": 24.5,
  "memory_usage_percent": 45.2,
  "disk_usage_percent": 58.1,
  "network_mbps": 12.4,
  "recent_events_count": 142,
  "timestamp": "2026-08-02T22:30:00Z"
}
```

---

## 2. System Metrics Endpoints

### `GET /api/v1/dashboard/metrics`
Fetches real-time host hardware system telemetry across all monitoring components.

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `category` (optional, string): Filter by `cpu`, `memory`, `disk`, `network`, `gpu`, `processes`.
- **Permission Required**: `dashboard:read`

#### Response Example (`200 OK`):
```json
{
  "resources": {
    "cpu": { "usage_percent": 18.2, "core_count": 8 },
    "memory": { "total_bytes": 34359738368, "used_bytes": 15461882265, "percent": 45.0 },
    "disk": { "total_bytes": 1000204886016, "used_bytes": 450092198707, "percent": 45.0 },
    "network": { "bytes_sent": 104857600, "bytes_recv": 524288000 }
  },
  "timestamp": "2026-08-02T22:30:00Z"
}
```

### `GET /api/v1/dashboard/metrics/timeseries`
Retrieves downsampled historical metrics over specified time ranges.

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `metric_name` (required, string): e.g., `cpu_usage`, `memory_usage`.
  - `start_time` (required, string ISO): Start timestamp.
  - `end_time` (required, string ISO): End timestamp.
  - `interval` (optional, string): `hourly`, `daily`, `weekly`. Default `hourly`.

---

## 3. Health & Diagnostic Endpoints

### `GET /api/v1/dashboard/health`
Returns health diagnostics across system services, database connections, and background engines.

- **Headers**: `Authorization: Bearer <token>`
- **Permission Required**: `dashboard:read`

#### Response Example (`200 OK`):
```json
{
  "is_healthy": true,
  "health_score": 1.0,
  "subsystems": {
    "monitoring": "ok",
    "live_metrics": "ok",
    "notification_engine": "ok",
    "analytics_engine": "ok",
    "websocket_gateway": "ok"
  }
}
```

---

## 4. Analytics Endpoints

### `GET /api/v1/dashboard/analytics/kpis`
Calculates and returns the 12 core system KPIs.

- **Headers**: `Authorization: Bearer <token>`
- **Permission Required**: `dashboard:read`

#### Response Example (`200 OK`):
```json
{
  "cpu_avg_usage": 22.4,
  "memory_avg_usage": 44.8,
  "disk_avg_usage": 55.1,
  "network_throughput_mbps": 14.2,
  "avg_response_time_ms": 3.8,
  "system_health_score": 0.98,
  "notification_rate": 0.05,
  "mission_completion_rate": 99.2,
  "agent_availability": 100.0,
  "workflow_completion_rate": 98.5,
  "uptime_percent": 99.99
}
```

### `GET /api/v1/dashboard/analytics/reports/{domain}`
Generates structured analytics reports for specified domains (`resource`, `health`, `notification`, `agent`, `mission`, `system`).

---

## 5. Error Responses Reference

Standard RFC 7807 Error Object returned for non-2xx status codes:

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "User lacks required permission 'dashboard:admin'",
    "status_code": 403,
    "timestamp": "2026-08-02T22:30:00Z"
  }
}
```
