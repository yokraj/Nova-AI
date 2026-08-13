# Nova AI Enterprise Dashboard Database Schema Reference

## Executive Summary
This document provides complete relational database schema specifications, table structures, column definitions, index strategies, foreign key constraints, and Mermaid ER diagrams for the **Nova AI Enterprise Dashboard Backend**.

---

## 1. Entity Relationship Diagram (ERD)

```mermaid
erdiagram
    SYSTEM_METRICS {
        uuid id PK
        timestamp sampled_at
        float cpu_usage_percent
        float memory_usage_percent
        float disk_usage_percent
        float network_rx_mbps
        float network_tx_mbps
        json telemetry_raw
    }

    HEALTH_LOGS {
        uuid id PK
        timestamp logged_at
        string subsystem
        string status
        float health_score
        json details
    }

    NOTIFICATIONS {
        uuid id PK
        timestamp created_at
        string fingerprint UK
        string priority
        string category
        string title
        string message
        boolean is_read
        boolean is_acknowledged
        json metadata
    }

    DASHBOARD_SETTINGS {
        uuid id PK
        string user_id UK
        int refresh_interval
        string theme
        json widget_layout
        timestamp updated_at
    }
```

---

## 2. Table Specifications

### A. Table: `system_metrics`
Stores sampled system telemetry data for analytics downsampling and historical reporting.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, `default=uuid4` | Unique metric sample identifier |
| `sampled_at` | `TIMESTAMP(tz)` | Indexed, Not Null | UTC timestamp when metric was sampled |
| `cpu_usage_percent` | `FLOAT` | Not Null | Overall CPU utilization percentage (0-100) |
| `memory_usage_percent`| `FLOAT` | Not Null | RAM usage percentage (0-100) |
| `disk_usage_percent` | `FLOAT` | Not Null | Primary disk partition usage percentage |
| `network_rx_mbps` | `FLOAT` | Not Null | Inbound network throughput in MB/s |
| `network_tx_mbps` | `FLOAT` | Not Null | Outbound network throughput in MB/s |
| `telemetry_raw` | `JSONB` / `JSON` | Optional | Full raw collector metric snapshot |

- **Indexes**:
  - `idx_system_metrics_sampled_at`: B-tree index on `sampled_at DESC` for time-series range queries.

---

### B. Table: `health_logs`
Logs diagnostic health state transitions across Nova AI subsystems.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Diagnostic event identifier |
| `logged_at` | `TIMESTAMP(tz)` | Indexed, Not Null | Timestamp of health evaluation |
| `subsystem` | `VARCHAR(64)` | Indexed, Not Null | Subsystem name (e.g. `monitoring`, `websocket`) |
| `status` | `VARCHAR(32)` | Not Null | Health status (`healthy`, `degraded`, `unhealthy`) |
| `health_score` | `FLOAT` | Not Null | Health score scalar (0.0 to 1.0) |
| `details` | `JSONB` / `JSON` | Optional | Contextual diagnostic details |

- **Indexes**:
  - `idx_health_logs_subsystem_time`: Composite index on `(subsystem, logged_at DESC)`.

---

### C. Table: `notifications`
Persists generated system alerts, warnings, and priority notifications.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Notification record identifier |
| `created_at` | `TIMESTAMP(tz)` | Indexed, Not Null | Creation timestamp |
| `fingerprint` | `VARCHAR(64)` | Unique Index, Not Null | SHA-256 deduplication fingerprint hash |
| `priority` | `VARCHAR(16)` | Indexed, Not Null | Severity (`LOW`, `NORMAL`, `HIGH`, `URGENT`) |
| `category` | `VARCHAR(32)` | Not Null | Event category (`resource`, `security`, `system`) |
| `title` | `VARCHAR(128)` | Not Null | Short alert title |
| `message` | `TEXT` | Not Null | Detailed alert body message |
| `is_read` | `BOOLEAN` | Not Null, `default=False` | Read status flag |
| `is_acknowledged` | `BOOLEAN` | Not Null, `default=False` | Acknowledgement flag |
| `metadata` | `JSONB` / `JSON` | Optional | Arbitrary event key-value payload |

- **Indexes**:
  - `uq_notifications_fingerprint`: Unique index on `fingerprint`.
  - `idx_notifications_priority_created`: Composite index on `(priority, created_at DESC)`.

---

### D. Table: `dashboard_settings`
Stores user-specific dashboard UI preferences and dynamic grid widget layouts.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Record identifier |
| `user_id` | `VARCHAR(64)` | Unique Index, Not Null | Owner user identifier |
| `refresh_interval` | `INTEGER` | Not Null, `default=5` | Preferred refresh rate in seconds |
| `theme` | `VARCHAR(32)` | Not Null, `default='dark'`| UI theme (`dark`, `light`, `glassmorphism`)|
| `widget_layout` | `JSONB` / `JSON` | Not Null | JSON grid configuration layout |
| `updated_at` | `TIMESTAMP(tz)` | Not Null | Last update timestamp |

---

## 3. Migration History

Database schema migrations are managed via **Alembic**:

1. `001_initial_dashboard_schema.py`: Created `system_metrics`, `health_logs`, `notifications`, `dashboard_settings` tables.
2. `002_add_fingerprint_unique_index.py`: Added unique index on `notifications.fingerprint`.
3. `003_add_timeseries_composite_indexes.py`: Optimized `sampled_at DESC` and composite time-series index queries.
