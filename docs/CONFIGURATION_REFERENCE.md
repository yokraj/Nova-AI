# Nova AI Enterprise Configuration Reference

## Overview
This reference specifies all configuration environment variables, defaults, type constraints, validation rules, and usage examples across all subsystems of the **Nova AI Enterprise Dashboard Backend**.

---

## Configuration Settings Reference Table

| Variable Name | Subsystem | Type | Default Value | Validation / Allowed Values | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `NOVA_ENV` | Core | String | `development` | `development`, `testing`, `production` | Deployment environment mode |
| `NOVA_HOST` | Network | String | `0.0.0.0` | Valid IPv4/IPv6 address | Bind IP address for web server |
| `NOVA_PORT` | Network | Integer | `8000` | `1024 - 65535` | Listening TCP port |
| `NOVA_LOG_LEVEL` | Logging | String | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Log verbosity level |
| `JWT_SECRET_KEY` | Security | String | Required in prod | Min 32 characters | Secret key for JWT verification |
| `JWT_ALGORITHM` | Security | String | `HS256` | `HS256`, `RS256` | Signature algorithm for JWT |
| `RATE_LIMIT_BURST` | Security | Integer | `20` | `1 - 100` | Max request burst rate per window |
| `RATE_LIMIT_MAX` | Security | Integer | `120` | `10 - 1000` | Max requests per minute per IP |
| `METRICS_INTERVAL` | Monitoring | Float | `1.0` | `0.1 - 60.0` | Telemetry polling rate (seconds) |
| `CHANGE_THRESHOLD`| Live Metrics| Float | `0.01` | `0.001 - 0.5` | Delta change detection ratio |
| `SNAPSHOT_RETENTION`| Live Metrics| Integer | `50` | `10 - 500` | Max ring buffer snapshot size |
| `MAX_NOTIFICATIONS`| Notifications| Integer | `1000` | `100 - 10000` | Max priority queue notification capacity |
| `DUPLICATE_WINDOW` | Notifications| Float | `300.0` | `10 - 3600` | Fingerprint deduplication TTL (s) |
| `ANALYTICS_RETENTION_DAYS`| Analytics| Integer | `90` | `7 - 365` | Historical retention window (days) |
| `ANOMALY_THRESHOLD`| Analytics| Float | `2.0` | `1.0 - 5.0` | Z-score threshold for anomalies |

---

## Production Configuration Example (`.env`)

```ini
NOVA_ENV=production
NOVA_HOST=0.0.0.0
NOVA_PORT=8000
NOVA_LOG_LEVEL=INFO

JWT_SECRET_KEY=9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a
JWT_ALGORITHM=HS256
RATE_LIMIT_BURST=20
RATE_LIMIT_MAX=120

METRICS_INTERVAL=1.0
CHANGE_THRESHOLD=0.01
SNAPSHOT_RETENTION=50

MAX_NOTIFICATIONS=1000
DUPLICATE_WINDOW=300.0

ANALYTICS_RETENTION_DAYS=90
ANOMALY_THRESHOLD=2.0
```
