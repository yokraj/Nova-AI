# Nova AI Enterprise Dashboard Operations Runbook

## Executive Summary
This operational runbook details standard operating procedures (SOPs) for starting, stopping, monitoring, maintaining, troubleshooting, and recovering the **Nova AI Enterprise Dashboard Backend**.

---

## 1. Service Lifecycle Management

### A. Startup Sequence
1. Verify database availability: `pg_isready -h localhost -p 5432`
2. Run database migrations: `alembic upgrade head`
3. Launch uvicorn server workers:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### B. Graceful Shutdown
Send SIGTERM signal to main worker processes to allow active WebSocket frames to finish flushing:
```bash
kill -15 $(pgrep -f "uvicorn app.main:app")
```

---

## 2. Health Monitoring & Diagnostic Checks

### Health Verification Endpoint
Probe `/api/v1/dashboard/health` via `curl`:
```bash
curl -s http://localhost:8000/api/v1/dashboard/health | jq .
```

Expected Healthy Output:
```json
{
  "is_healthy": true,
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

## 3. Log Inspection & Diagnostics

Log entries are structured JSON streams processed via `structlog`.

### Filtering Error Events:
```bash
journalctl -u nova-dashboard-backend.service -f | grep '"level":"error"'
```

### Tracking Security Threat Alerts:
```bash
journalctl -u nova-dashboard-backend.service | grep "security_alert_generated"
```

---

## 4. Troubleshooting Decision Tree

| Symptom / Alert | Potential Root Cause | Resolution Action |
| :--- | :--- | :--- |
| **High WebSocket Disconnect Rate** | Client heartbeats timing out | Increase `heartbeat_interval` in config or check NGINX `proxy_read_timeout`. |
| **HTTP 429 Rate Limit Spikes** | Client IP exceeding 120 req/min | Verify frontend isn't polling REST endpoints instead of consuming WebSockets. |
| **Hardware Collector Partial Failure** | Host sensor offline (e.g. GPU `pynvml`) | Fallback metrics automatically engaged. Check NVIDIA driver daemon. |
| **Memory Growth In Buffer** | Max queue bounds disabled | Verify `SNAPSHOT_RETENTION` and `MAX_NOTIFICATIONS` bounds in `.env`. |

---

## 5. Maintenance Procedures

### A. Database Retention Purging
Run analytics retention purging script to trim raw metrics older than 90 days:
```bash
py -c "import asyncio; from app.analytics_engine.retention import RetentionManager; asyncio.run(RetentionManager().purge_expired_metrics(90))"
```

### B. In-Memory Cache Reset
To purge stale telemetry cache snapshots without service downtime:
```bash
py -c "from app.dashboard.services.cache_service import DashboardCacheService; DashboardCacheService().clear_all()"
```
